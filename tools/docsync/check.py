#!/usr/bin/env python3
"""Doc-sync check for the Leshy2 hardware + firmware repos.

Two independent checks, both run in CI on every push (see .github/workflows/docsync.yml
in each repo):

  1. Link/anchor integrity — every cross-repo and in-repo Markdown link with a
     "#anchor" must resolve to a real heading in the target file. Catches the most
     common silent divergence: a section is renamed in one repo and the other repo's
     deep link (e.g. esp32-leshy2#9-firmware) quietly dies.

  2. Canonical-section tripwire — sync-map.json lists sections that one repo restates
     from the other (hardware capabilities, the firmware decisions, the link protocol).
     Each carries a recorded hash of the canonical text. When the canonical text
     changes, its hash no longer matches and the check fails, telling you which mirror
     to review. It does NOT edit prose — it flags the divergence for a human to resolve,
     then you re-baseline with `--update`.

Usage:
  check.py --repo esp32-leshy2=<path> --repo esp32-leshy2-firmware=<path> [--map <sync-map.json>] [--update]

Exit code 0 = clean, 1 = divergence found (or, with --update, baselines rewritten).
stdlib only — runs on any GitHub runner without pip.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
GH_PREFIX = "https://github.com/anton-vinogradov/"


def slugify(text):
    """GitHub heading-anchor slug (unicode-aware; does NOT collapse repeated spaces)."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = text.strip()
    return text.replace(" ", "-")


def strip_code_fences(text):
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def read_text(path):
    return path.read_text(encoding="utf-8")


_slug_cache = {}


def heading_slugs(path):
    """Set of GitHub anchor slugs for a Markdown file (with duplicate -1/-2 suffixes)."""
    key = str(path)
    if key in _slug_cache:
        return _slug_cache[key]
    slugs, counts = set(), {}
    in_fence = False
    for line in read_text(path).splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        base = slugify(m.group(2))
        n = counts.get(base, 0)
        slug = base if n == 0 else f"{base}-{n}"
        counts[base] = n + 1
        slugs.add(slug)
    _slug_cache[key] = slugs
    return slugs


def resolve_target(url, current_file, repos):
    """Map a link URL to (target_path, anchor) or None if not our concern.

    Returns (Path|None, anchor|None, note). target_path None with a note means
    'skip'. anchor None means the link has no fragment.
    """
    if "://" in url and not url.startswith(GH_PREFIX):
        return None, None, "external"
    if url.startswith("mailto:"):
        return None, None, "external"

    anchor = None
    if "#" in url:
        url, anchor = url.split("#", 1)

    if url.startswith(GH_PREFIX):
        rest = url[len(GH_PREFIX):]
        parts = [p for p in rest.split("/") if p != ""]
        if not parts:
            return None, None, "external"
        repo = parts[0]
        root = repos.get(repo)
        if root is None:
            return None, None, "unknown-repo"  # a repo we don't have checked out
        if len(parts) == 1:
            target = root / "README.md"
        elif parts[1] == "blob" and len(parts) >= 4:
            target = root / Path(*parts[3:])
        else:
            return None, None, "unsupported-github-path"
        return target, anchor, None

    # relative, in-repo link
    if url == "":
        target = current_file  # pure "#anchor"
    else:
        target = (current_file.parent / url).resolve()
    return target, anchor, None


def iter_markdown(root):
    """Repo-owned Markdown only — skip vendored (node_modules) and hidden (.git, …) dirs."""
    for md in sorted(root.rglob("*.md")):
        parts = md.relative_to(root).parts
        if any(p == "node_modules" or p.startswith(".") for p in parts):
            continue
        yield md


def check_links(repos):
    failures = []
    checked = 0
    for name, root in repos.items():
        for md in iter_markdown(root):
            for url in LINK_RE.findall(strip_code_fences(read_text(md))):
                target, anchor, note = resolve_target(url, md, repos)
                if target is None:
                    continue
                rel = md.relative_to(root)
                if not target.exists():
                    # only complain about missing markdown / in-repo targets
                    if str(target).endswith(".md") or anchor is not None:
                        failures.append(f"{name}/{rel}: link -> missing file {url}")
                    continue
                if anchor is None:
                    continue
                if not str(target).endswith(".md"):
                    continue
                checked += 1
                if anchor not in heading_slugs(target):
                    failures.append(f"{name}/{rel}: dead anchor '#{anchor}' -> {url}")
    return checked, failures


def section_text(path, heading):
    """Text of the section whose heading matches `heading` (by slug), up to the next
    heading of the same or higher level."""
    want = slugify(heading)
    lines = read_text(path).splitlines()
    start = level = None
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if not m:
            continue
        if start is None:
            if slugify(m.group(2)) == want:
                start, level = i, len(m.group(1))
        elif len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    if start is None:
        return None
    return "\n".join(lines[start:])


def normalized_hash(text):
    lines = [ln.rstrip() for ln in text.splitlines()]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def canonical_content(entry, repos):
    root = repos[entry["repo"]]
    path = root / entry["file"]
    if not path.exists():
        return None, f"canonical file missing: {entry['repo']}/{entry['file']}"
    if entry.get("whole_file"):
        return normalized_hash(read_text(path)), None
    text = section_text(path, entry["heading"])
    if text is None:
        return None, f"canonical section not found: {entry['repo']}/{entry['file']} :: {entry['heading']}"
    return normalized_hash(text), None


def check_tripwire(repos, map_path, update):
    data = json.loads(read_text(map_path))
    entries = data.get("canonical", [])
    failures, changed = [], False
    for e in entries:
        h, err = canonical_content(e, repos)
        if err:
            failures.append(err)
            continue
        if update:
            if e.get("sha256") != h:
                e["sha256"] = h
                changed = True
            continue
        if e.get("sha256") != h:
            where = e["repo"] + "/" + e["file"]
            if not e.get("whole_file"):
                where += " :: " + e["heading"]
            failures.append(
                f"canonical changed: {where}\n"
                f"      review its mirror: {e.get('mirror', '?')}\n"
                f"      if the change is intended and the mirror is updated, re-baseline:\n"
                f"        python tools/docsync/check.py --update --repo ..."
            )
    if update and changed:
        map_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(entries), failures, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", action="append", default=[], metavar="name=path")
    ap.add_argument("--map", default=str(SCRIPT_DIR / "sync-map.json"))
    ap.add_argument("--update", action="store_true", help="re-baseline tripwire hashes")
    args = ap.parse_args()

    repos = {}
    for spec in args.repo:
        name, _, path = spec.partition("=")
        repos[name] = Path(path).resolve()
    if not repos:
        ap.error("at least one --repo name=path is required")
    for name, root in repos.items():
        if not root.is_dir():
            ap.error(f"repo path for {name} is not a directory: {root}")

    map_path = Path(args.map).resolve()
    n_checked, link_fail = check_links(repos)
    n_trip, trip_fail, changed = check_tripwire(repos, map_path, args.update)

    print(f"docsync: repos={','.join(repos)} | anchors checked={n_checked} | tripwires={n_trip}")
    if args.update:
        print("tripwire baseline " + ("updated" if changed else "already current"))

    failures = link_fail + ([] if args.update else trip_fail)
    if failures:
        print("\nDIVERGENCE FOUND:\n")
        for f in failures:
            print("  ✗ " + f)
        print(f"\n{len(failures)} issue(s).")
        return 1
    print("OK — docs are in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
