---
name: retro
description: End-of-session retrospective for the egor-ai-helpers rules. Reviews this session for corrections Egor made, rules that were missing or ignored, and tool output that wasted context, then proposes concrete edits to claude/rules/ as a diff. Use when Egor says "retro", "ретро", "what rule was missing", or at the end of a long task.
disable-model-invocation: true
effort: medium
---

# Retro

Look back at this session and turn what went wrong into a rule change, because
a correction that stays in the chat is paid for again next session.

1. Collect the evidence from this conversation only: every place Egor corrected
   you, asked for something a second time, cut an answer short, or redid your
   work. Quote the message in one line each.
2. For each item decide which of the three it is:
   - a rule exists and was not followed: name the file and heading;
   - a rule is missing: draft it in the style of the existing files, as
     observable behaviour, with a before / after example when the point is not
     obvious;
   - noise: tool output or a search that cost context and changed nothing.
     Propose the filter (`tail`, `grep`, a subagent) that would have avoided it.
3. Rank by what cost the most time this session, most severe first. Drop items
   that happened once and are unlikely to repeat; a rule is added on the second
   occurrence, not the first.
4. Output: the ranked list, then the proposed edits to
   `~/egor-ai-helpers/claude/rules/*.md` as a unified diff. Do not apply the
   diff; Egor decides. If nothing is worth changing, say so in one line.
