# egor-ai-helpers

[![Claude Code](https://img.shields.io/badge/Claude_Code-rules_%2B_agents-blueviolet)](https://code.claude.com/docs)
[![Shell](https://img.shields.io/badge/installer-bash-4EAA25?logo=gnubash&logoColor=white)](install.sh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

Opinionated rules and a read-only review agent for [Claude Code](https://code.claude.com/docs).
One command installs them into `~/.claude/`, and they apply in every session and
every project on the machine.

Written for a senior mobile engineer working with Kotlin Multiplatform, Decompose,
Compose Multiplatform and SwiftUI. Most of it is stack-agnostic: how to answer,
when to edit code and when to ask, how to measure confidence before a bug fix, how
to keep a diff minimal.

> The rules are in English. The first rule tells Claude to answer in Russian;
> change that one line if you want another language.

## Why

Default assistant behaviour optimises for sounding helpful: long answers, confident
guesses, "fixes" that silence a symptom, refactors nobody asked for. These rules
optimise for the opposite: every claim has a source, every bug fix has a measured
confidence, every diff is the smallest one that does the job, and the answer ends
with the decision you need to make.

## Features

- **Five-line answers, decision last.** Verdict first, no retelling of what is
  already visible in the terminal. Explanations on request are prose, not bullets.
- **Facts over guesses.** Every statement carries its source: docs, code, command
  output, or an explicit "from memory, not verified". Versions, flag names and
  API names are always checked.
- **Confidence gate for bug fixes.** A fix is applied only at 93%+ confidence, and
  the number is built from five verifiable items, never eyeballed.
- **Minimal diff, project style first.** No drive-by refactors, no code comments,
  no abstractions "for later". A neighbouring file beats the official sample.
- **Mobile baseline.** Coroutines, `Value`, DI, Decompose navigation, spacing and
  text styles in Compose and SwiftUI, iOS and localisation parity. Items backed
  by official docs cite them.
- **`egor-review` agent.** Read-only review of your own diff or a team PR against
  these rules. Every finding is confirmed with `file:line` and a quoted line.
- **Self-healing install.** Git hooks and a `SessionStart` hook keep the copy in
  `~/.claude/CLAUDE.md` in sync with the repo, so a stale rule never loads.
- **Context economy.** Stack-specific rules are path-scoped and load only when a
  matching file is read; verbose work goes to subagents; command output is
  filtered before it enters the context.
- **Verification that cannot lie.** A regression test is shown red without the
  fix and green with it; a failing test is never weakened; a subagent's "done"
  is re-checked by `git diff` before it reaches the report.

## Quick start

Requires `git`, `bash`, `python3` and Claude Code.

```bash
git clone https://github.com/TaN4eLL0/egor-ai-helpers.git ~/egor-ai-helpers && cd ~/egor-ai-helpers && ./install.sh
```

Rules load in a **new** session; the current one already has its context.

Update:

```bash
cd ~/egor-ai-helpers && git pull
```

A git hook re-runs the installer after `pull`, so there is no second step.

Uninstall:

```bash
~/egor-ai-helpers/install.sh --uninstall
```

## Usage

The rules work on their own: they live in `~/.claude/CLAUDE.md` and load into every
session. Run `/context` inside Claude Code to confirm the block is there.

The review agent is invoked in chat, for example "review my changes" for the
current diff or "review PR #123" for an open pull request. It only reads: it never
edits files and never posts to GitHub unless asked explicitly. The report lands in
the terminal grouped by severity: BLOCKER, WARNING, NITPICK.

## Before / after

A bug report, default behaviour:

> Added a null check in `Client.kt` so it no longer crashes. Let me know if you
> want me to add tests too!

The same report under these rules:

> Confidence 96%: the cause is in `Client.kt:42` (NPE on an empty response, in the
> stack trace), the fix returns an error instead of dereferencing, two callers,
> both in `SyncWorker`, covered by `ClientTest`, ran it: 18 passed. Nothing
> unverified.
>
> Not done: `RetryPolicy` untouched; it has its own timeout contract and changing
> it would alter retry behaviour, which is a separate task.

## How it works

`install.sh` concatenates `claude/rules/*.md` in filename order and splices the
result into `~/.claude/CLAUDE.md` between two markers:

```
<!-- egor-ai:start -->
...
<!-- egor-ai:end -->
```

Nothing outside the markers is touched, so the file stays hand-editable and other
installers' blocks can live next to it. Re-running replaces the block instead of
duplicating it.

Two safeguards keep the copy fresh:

- **Git hooks.** `core.hooksPath` points at `githooks/`, and the installer re-runs
  after `commit`, `pull`, `checkout` and `rebase`.
- **SessionStart hook.** `egor-ai-rules-sync.sh` compares the block with
  `claude/rules/` via `install.sh --check` at session start. If the block is
  stale, the hook rebuilds it and prints the fresh rules straight into that
  session's context.

| Path | What |
|---|---|
| `claude/rules/*.md` | Rules. The number prefix sets the concatenation order |
| `claude/agents/` | Subagents → `~/.claude/agents/` |
| `claude/commands/` | Slash commands → `~/.claude/commands/` |
| `claude/hooks/` | Hooks → `~/.claude/hooks/`; `egor-ai-rules-sync.sh` is registered as `SessionStart` |
| `githooks/` | Repo git hooks |

| Rule file | Loaded | When it applies |
|---|---|---|
| `10-communication-style` | always | Language, length, clarity, sourcing, reports |
| `20-crash-fix-confidence` | always | Investigating a crash or a bug |
| `30-implementation` | always | Writing any code; context economy |
| `40-kmp-mobile` | on `*.kt`, `*.kts`, `*.swift` | Coroutines, state, DI, Compose, SwiftUI |
| `45-mobile-feature-delivery` | on `*.kt`, `*.kts`, `*.swift` | Building a feature from a spec and Figma |

Rules that must never be missing (the 93% confidence gate, the answer format)
sit in the always-loaded block. Stack-specific rules start with a `paths:`
frontmatter and are installed as
[path-scoped rules](https://code.claude.com/docs/en/memory#path-specific-rules)
into `~/.claude/rules/`, so they cost nothing until Claude reads a matching file.

## Make it yours

1. Rules in `claude/rules/` are plain markdown. Delete the files that are not
   about your stack (`40-*`, `45-*`) or edit the text.
2. A new rule is a file `claude/rules/NN-name.md`, where `NN` sets the order.
   Start with a `##` heading, because the `#` level in `CLAUDE.md` is taken.
3. Write rules as observable behaviour: the model does not execute "be concise",
   it executes "answers are at most five lines". Give a before / after example for
   anything non-obvious.
4. The placeholder `{{REPO_ROOT}}` inside a rule expands to the checkout path.
   A rule that starts with YAML frontmatter containing `paths:` becomes
   path-scoped instead of joining the always-loaded block.
5. Run `./install.sh` and open a new session.

Installer commands:

```bash
./install.sh --dry-run
```

```bash
./install.sh --check
```

`--dry-run` prints the block that would be written. `--check` exits 0 when
`CLAUDE.md` matches `claude/rules/` and 1 when it is stale.

## Contributing

Issues and pull requests are welcome. A rule change should say which repeated
mistake it prevents and include a before / after example; see
[Make it yours](#make-it-yours) for the format.

## License

[MIT](LICENSE)
