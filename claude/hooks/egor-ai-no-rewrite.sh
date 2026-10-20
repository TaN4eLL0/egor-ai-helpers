#!/usr/bin/env bash
# PreToolUse (Bash): deny history rewrites unless the user asked for them.
set -euo pipefail

cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')
grep -q 'EGOR_AI_ALLOW_REWRITE=1' <<<"$cmd" && exit 0

deny() {
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1"
    exit 0
}

if grep -Eq 'git[^|;&]*\bcommit\b[^|;&]*--amend' <<<"$cmd"; then
    deny "egor-ai: git commit --amend is blocked; make a new commit instead. If Egor asked for it explicitly, prefix the command with EGOR_AI_ALLOW_REWRITE=1"
fi
if grep -Eq 'git[^|;&]*\bpush\b[^|;&]*(--force|-f\b|--force-with-lease)' <<<"$cmd"; then
    deny "egor-ai: force-push is blocked; push a new commit instead. If Egor asked for it explicitly, prefix the command with EGOR_AI_ALLOW_REWRITE=1"
fi
if grep -Eq 'git[^|;&]*\b(filter-branch|filter-repo)\b' <<<"$cmd"; then
    deny "egor-ai: history rewrite is blocked. If Egor asked for it explicitly, prefix the command with EGOR_AI_ALLOW_REWRITE=1"
fi
exit 0
