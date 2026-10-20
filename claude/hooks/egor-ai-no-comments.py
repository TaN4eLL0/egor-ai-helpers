#!/usr/bin/env python3
"""PreToolUse (Edit|Write): deny new code comments in Kotlin and Swift files.

Allowed: linter directives, KDoc on public API inside shared libraries, and
lines that already existed in the file (an edit that only moves them).
"""
import json
import pathlib
import re
import sys

CODE_SUFFIXES = {".kt", ".kts", ".swift"}
KDOC_LIBRARIES = ("kmp-common-components", "idf-kmm-core")
DIRECTIVE = re.compile(r"(swiftlint:|ktlint-|detekt|noinspection|@formatter|SPDX|Copyright|TODO\(\w+-\d+\))")
COMMENT = re.compile(r"^\s*(//|/\*|\*\s)")


def added_lines(data):
    tool = data.get("tool_name")
    inp = data.get("tool_input", {})
    path = pathlib.Path(inp.get("file_path", ""))
    if path.suffix not in CODE_SUFFIXES:
        return path, []
    if tool == "Edit":
        before = inp.get("old_string", "").splitlines()
        after = inp.get("new_string", "").splitlines()
    elif tool == "Write":
        before = path.read_text().splitlines() if path.exists() else []
        after = inp.get("content", "").splitlines()
    else:
        return path, []
    existing = set(before)
    return path, [l for l in after if l not in existing]


def is_offending(path, line):
    if not COMMENT.match(line):
        return False
    if DIRECTIVE.search(line):
        return False
    if any(lib in str(path) for lib in KDOC_LIBRARIES) and line.lstrip().startswith(("/**", "*")):
        return False
    return True


def main():
    data = json.load(sys.stdin)
    path, lines = added_lines(data)
    bad = [l.strip() for l in lines if is_offending(path, l)]
    if not bad:
        return
    sample = "; ".join(bad[:3])[:300].replace('"', "'")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"egor-ai: new comment in {path.name} blocked ({sample}). "
                "Rule: leave no comments in the code unless Egor asked; "
                "explain the non-obvious part in the report instead."
            ),
        }
    }))


if __name__ == "__main__":
    main()
