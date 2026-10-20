#!/usr/bin/env python3
"""Stop: after a turn that edited code, the answer must state the verification
fact and what is not done. Otherwise the turn is sent back once."""
import json
import re
import sys

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
MARKERS = re.compile(
    r"(провер(ил|ка|ял)|не сделано|verif(ied|ication)|didn.t verify|did not verify|not done)",
    re.IGNORECASE,
)


def turn_edited_code(transcript_path):
    edited = False
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for raw in f:
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message", {})
                content = msg.get("content")
                if entry.get("type") == "user" and isinstance(content, str):
                    edited = False
                elif entry.get("type") == "user" and isinstance(content, list):
                    if not any(b.get("type") == "tool_result" for b in content if isinstance(b, dict)):
                        edited = False
                elif entry.get("type") == "assistant" and isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in EDIT_TOOLS:
                            edited = True
    except OSError:
        return False
    return edited


def main():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    last = (data.get("last_assistant_message") or "").strip()
    if not last or last.endswith("?"):
        return
    if not turn_edited_code(data.get("transcript_path", "")):
        return
    if MARKERS.search(last):
        return
    print(json.dumps({
        "decision": "block",
        "reason": (
            "egor-ai: this turn edited code, but the answer has neither a verification "
            "fact nor a 'not done' line. Add one line each: what you ran after the last "
            "edit and what it printed (or 'did not verify, because ...'), and what is not done."
        ),
    }))


if __name__ == "__main__":
    main()
