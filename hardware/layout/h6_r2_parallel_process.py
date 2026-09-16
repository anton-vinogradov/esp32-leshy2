"""Thread-safe POSIX subprocess groups for bounded parallel phase callbacks.

ProcessRegistry.run(argv, log, timeout, cwd=..., env=...) returns exit_code
(integer, "timeout", or "cancelled"), returncode, pid and elapsed seconds.
Use the same Event with run_jobs and its cancel_running=registry.cancel_all.
No worker installs signal handlers. Every exit cleans its own process group,
even when a successful leader leaves children running, and reaps the direct
Popen child. Orphan descendants are reaped by the OS, not by this Python parent.
Children that create another session/group escape this ownership boundary:
nested drivers must clean up those groups themselves when they receive TERM.
"""
import math
import os
from pathlib import Path
import signal
import subprocess
from threading import Event, Lock
import time


class _Group:
    def __init__(self, process, grace):
        self.process, self.grace = process, grace
        self.lock, self.deadline, self.killed = Lock(), None, False

    def signal_once(self, hard=False):
        # The cancelling thread and run()'s finally share ownership. Repeated
        # TERM could interrupt a nested driver's in-progress child cleanup.
        with self.lock:
            if hard:
                if self.killed:
                    return
                self.killed = True
            else:
                if self.deadline is not None:
                    return
                self.deadline = time.monotonic() + self.grace
            try:
                os.killpg(self.process.pid, signal.SIGKILL if hard else signal.SIGTERM)
            except ProcessLookupError:
                pass

    def alive(self):
        try:
            os.killpg(self.process.pid, 0)
            return True
        except ProcessLookupError:
            return False

    def finish(self):
        self.signal_once()
        while self.alive() and time.monotonic() < self.deadline:
            self.process.poll()  # Reap an exited leader while children drain.
            time.sleep(min(0.02, max(0, self.deadline - time.monotonic())))
        if self.alive():
            self.signal_once(hard=True)
        self.process.wait(timeout=5)


class ProcessRegistry:
    """Own bounded process groups; cancel_all stops them once and forbids new work.

    cancel_all requests TERM promptly; active run() calls perform the bounded
    grace/KILL/reap sequence before returning. Callback errors propagate only
    after that cleanup. Cancelled registries are intentionally not reusable.
    """
    def __init__(self, cancel_event=None, grace_seconds=10):
        if (isinstance(grace_seconds, bool) or not isinstance(grace_seconds, (int, float))
                or not math.isfinite(grace_seconds) or grace_seconds < 0):
            raise ValueError("grace_seconds must be finite and nonnegative")
        self.cancel_event = cancel_event if cancel_event is not None else Event()
        self.grace_seconds, self._lock, self._groups = grace_seconds, Lock(), {}

    @property
    def active_count(self):
        with self._lock:
            return len(self._groups)

    def cancel_all(self):
        with self._lock:
            self.cancel_event.set()
            groups = list(self._groups.values())
        for group in groups:
            group.signal_once()

    def _wait(self, group, deadline):
        while True:
            if self.cancel_event.is_set():
                return "cancelled"
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return "timeout"
            try:
                return group.process.wait(timeout=min(0.05, remaining))
            except subprocess.TimeoutExpired:
                pass

    def run(self, command, log, timeout, *, cwd=None, env=None):
        if (isinstance(timeout, bool) or not isinstance(timeout, (int, float))
                or not math.isfinite(timeout) or timeout <= 0):
            raise ValueError("timeout must be finite and positive")
        if isinstance(command, (str, bytes)) or not command:
            raise ValueError("command must be a nonempty argv sequence")
        started, group = time.monotonic(), None
        with Path(log).open("w") as stream:
            try:
                # Registration and cancellation are atomic with respect to
                # spawning: no child can fall between the registry and cancel_all.
                with self._lock:
                    if self.cancel_event.is_set():
                        return {"exit_code": "cancelled", "returncode": None, "pid": None, "seconds": 0.0}
                    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                               stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                    group = _Group(process, self.grace_seconds)
                    self._groups[process.pid] = group
                code = self._wait(group, started + timeout)
            finally:
                if group is not None:
                    try:
                        group.finish()
                    finally:
                        with self._lock:
                            self._groups.pop(group.process.pid, None)
        return {"exit_code": code, "returncode": process.returncode, "pid": process.pid,
                "seconds": round(time.monotonic() - started, 3)}
