#!/usr/bin/env bash
# PreCompact: snapshot the working-tree state so the task can be resumed after
# compaction. The rules tell Claude to read this file right after a compaction.
set -uo pipefail

out="${HOME}/.claude/egor-ai/compact-state.md"
mkdir -p "$(dirname "$out")"
{
    printf '# State saved before compaction (%s)\n\n' "$(date '+%Y-%m-%d %H:%M')"
    printf 'cwd: %s\n' "$PWD"
    if git rev-parse --git-dir >/dev/null 2>&1; then
        printf 'branch: %s\n\n## git status --short\n' "$(git branch --show-current 2>/dev/null)"
        git status --short 2>/dev/null | head -80
        printf '\n## git diff --stat (unstaged + staged)\n'
        git diff --stat HEAD 2>/dev/null | tail -40
        printf '\n## last 5 commits\n'
        git log --oneline -5 2>/dev/null
    else
        printf 'not a git repository\n'
    fi
} > "$out"
exit 0
