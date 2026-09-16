#!/usr/bin/env python3
"""Aggregate one explicitly selected Codex journal without exporting its text.

Local diagnostic counters, not billing or quota. Child-agent usage is not
assumed to be included. Repeated token_count notifications are not summed.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("An explicit timezone is required")
    return result


def measure(events, since, until):
    start, stop = timestamp(since), timestamp(until)
    if stop <= start:
        raise ValueError("Empty or reversed measurement interval")
    baseline = latest = None
    counters = {"tool_calls": 0, "tool_result_characters": 0,
                "assistant_messages": 0, "compactions": 0}
    for event in events:
        if "timestamp" not in event:
            continue
        moment = timestamp(event["timestamp"])
        if moment > stop:
            continue
        payload = event.get("payload", {})
        if event.get("type") == "event_msg" and payload.get("type") == "token_count":
            usage = (payload.get("info") or {}).get("total_token_usage")
            if usage is not None:
                point = {"timestamp": event["timestamp"], "usage": usage}
                previous = latest or baseline
                if moment >= start and previous and any(
                        usage[key] < value for key, value in previous["usage"].items() if key in usage):
                    raise ValueError("Cumulative token counter reset: do not subtract across it")
                if moment < start:
                    baseline = point
                else:
                    latest = point
        if not start <= moment <= stop:
            continue
        if event.get("type") == "compacted":
            counters["compactions"] += 1
        if event.get("type") == "response_item":
            kind = payload.get("type")
            if kind in ("function_call", "custom_tool_call"):
                counters["tool_calls"] += 1
            elif kind in ("function_call_output", "custom_tool_call_output"):
                output = payload.get("output", "")
                counters["tool_result_characters"] += len(output if isinstance(output, str) else json.dumps(output))
            elif kind == "message" and payload.get("role") == "assistant":
                counters["assistant_messages"] += 1
    result = {"requested_start": since, "requested_stop": until,
              "scope": "one local root-task journal; child-agent inclusion unverified",
              "not_billing_or_quota": True, "proxies": counters,
              "token_delta": None, "uncached_input_plus_output_proxy": None}
    if baseline and latest:
        delta = {key: latest["usage"][key] - value for key, value in baseline["usage"].items()
                 if key in latest["usage"]}
        if any(value < 0 for value in delta.values()):
            raise ValueError("Cumulative token counter reset: do not subtract across it")
        result.update(counter_start=baseline["timestamp"], counter_stop=latest["timestamp"], token_delta=delta)
        needed = ("input_tokens", "cached_input_tokens", "output_tokens")
        if all(key in delta for key in needed):
            fresh = delta["input_tokens"] - delta["cached_input_tokens"]
            if fresh < 0:
                raise ValueError("Cached input exceeds input delta")
            result["uncached_input_plus_output_proxy"] = fresh + delta["output_tokens"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--since", required=True)
    parser.add_argument("--until", default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    with args.session.open() as stream:
        # Read-only: only numeric aggregates and timestamps leave this process.
        print(json.dumps(measure((json.loads(line) for line in stream), args.since, args.until), indent=2))


if __name__ == "__main__":
    main()
