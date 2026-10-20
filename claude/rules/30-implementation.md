## Writing code

Applies always, whenever you write or change code, not only in new features.

### Project style matters more than anything else

Before the first line of code, read two or three existing files of the same
layer and repeat their structure: naming, order of class members, error
handling, approach to DI, test structure, log format. Project style ranks above
both your preferences and "how it is done in the industry". If the project does
it differently from the official example, do it the project's way, and name the
discrepancy to me separately; the decision to change the style is mine.

The project's documentation for agents is read before the code, not after. If
the repository has `knowledge/`, `docs/` or a similar base with conventions,
module architecture and patterns, find the files in it on the task's topic and
read them before choosing where to put the code and which styles to take. A
base that is only updated after the work prevents not a single mistake, because
by the time of the update the code is already written.

Before writing a new screen, widget or layer, find a neighbouring feature in
the project that already solves a similar task, and repeat its layout across
modules, packages and files. Invent your own structure only when there is no
such neighbour, and then name that in the report.

### Extensibility

Extensibility is measured by one criterion: adding the next case of the same
kind requires a change **in one place** and does not require changing existing
calls. It is not measured by the number of interfaces, layers and factories.

Therefore add an extension point only when the second case already exists in
the code or is named in the task. An abstraction "for the future" under a single
case is not extensibility, but an extra layer that everyone after you will have
to read. If you see that an extension is likely, but there is no second case
yet, say so in words in the report, not as an abstraction in the code.

### A fix in the shared library beats a workaround in the project

We do quality work, so the emphasis is always on reusability and extensibility,
not on a crutch that is faster to write. When the cause of a problem lies in a
shared library (`idf-kmm-core`, `kmp-common-components`), the right place for
the change is the library, not a workaround in the project. A workaround in the
project leaves the breakage alive, and the next project will run into it again,
which means the cost of the workaround is not zero, but one more such change
later.

Changing the library instead of the project is required when three conditions
hold at the same time:

1. the change in the library is simple;
2. **100%** confidence that it won't affect other screens and other projects,
   and that confidence is confirmed by a list of calling places, not a feeling;
3. it is the architecturally correct and extensible way, not bending the
   library to one particular case.

If at least one condition is not met, a workaround in the project is
acceptable, but then name in the report exactly which condition was not met.

Separately about confidence in wording. Don't write "better to do it in the
project" or "better to extend the core" as a ready conclusion. First list the
options with their consequences: a change in the library, a change in the
project, and intermediate ones if there are any; state for each the blast
radius and the cost of the release cycle, and only then give your
recommendation, marked as a recommendation. I make the decision.

### Readability

- The name says what the function does without reading its body. If you need
  to open the body to understand, the name is bad.
- The function fits entirely on the screen. If it doesn't fit, there is more
  than one responsibility inside.
- Abbreviations only those already accepted in the project. No `mgr`, `ctx`,
  `res` on your own initiative.
- Condition nesting no deeper than two levels, beyond that early return.

### Leave no comments in the code

Don't write comments until I ask. This applies to everything: explanations
above a function, `//` at the end of a line, KDoc and docstrings, TODO and
FIXME, separators like `// --- helpers ---`, and also comments describing your
own change ("added retry here"). The reason is that such a comment retells the
code I am reading anyway, goes stale at the very next change, and after that
starts lying.

There are exactly three exceptions to this:

1. I asked for a comment;
2. the project does it that way in this same layer, and then the rule "project
   style matters more" applies: repeat the form of the neighbouring files;
3. the comment is needed as part of working code: an annotation or directive
   (`@Suppress`, `// swiftlint:disable`, `// ktlint-disable`, a licence header,
   a generated marker).

Don't apply an exception silently. The fact that neighbouring files are densely
commented doesn't yet mean the second exception fired, because the explicit rule
"don't write comments" is stronger than a conclusion drawn from neighbouring
code. If you think an exception applies, ask before writing the comment.

Don't delete existing comments by others along with the change: they are
removed as a separate task and on request. If you think a place without a
comment is unclear, tell me that in words in the report, rather than leaving
an explanation in the code.

This rule has two caveats. First: a comment that your change made false is
fixed in the same change, otherwise it starts lying right in your diff. Second:
in the shared libraries (`kmp-common-components`, `idf-kmm-core`) KDoc on the
public API is mandatory by the team rule `kmp/api-stability/kdoc-mandatory`.
Therefore a new value of a public enum or a new public method gets KDoc in the
form of the neighbouring entries, and there is no need to ask separately.

### No needless spreading across files

- A new file only when the entity is needed from more than one place, or when
  the current file is already bigger than what is accepted in the project.
- Don't create a new directory or package for a single file.
- One class per file only if that is how the project does it, not by default.
- Don't spread related things across layers for the sake of symmetry. If the
  change fits entirely in one existing file, that is where it stays.

File size is also a reason to split, but by meaning, not mechanically. When a
UI file grows past roughly 150 lines, look at whether it contains independent
parts of the screen (a header, a summary row, a banner) and move each into its
own file in the same feature package, named after what it draws. A private
function at the bottom of the file remains the right choice for a small helper
with one consumer, as long as the file reads as a whole; when the file no longer
fits in your head, those same helpers move to neighbouring files of the same
package, not to shared modules.

A repetition of two or three lines in two places of one feature is written in
place, not extracted into a separate helper file. A separate file for such a
repetition makes the reader jump between files, and saves two lines.

The place of new code is determined by the number of its real consumers, not by
how reusable it looks. If a widget, a function or a set of styles is needed by
one feature, they live next to it: as a separate file in that feature's package,
and if the consumer is one file, as a private function at the bottom of that
file. For a single consumer don't start a new Gradle module, don't put code in
the shared components folder and don't add tokens to the design system or to
the core extensions of fonts and colours. Shared modules and core files are read
and built by all projects and features, so one-off content there clutters them
for everyone, and moving something out is justified only when the second
consumer already exists in the code or is named in the task.

### Grounding

If the task has an officially documented way (lifecycle, threading, config,
public API), do it that way and name the source. When there are several ways,
choose the documented one, not the shortest.

Strength of sources, in descending order:

1. official documentation of the product or library;
2. the sources of the library itself;
3. release notes and the issue tracker of its maintainers;
4. talks and articles by the library's authors;
5. blogs and Stack Overflow.

The fifth level is a hint about where to look, not a justification. Copying a
solution from there without checking it against the first or second level is
forbidden.

### When there is no conviction

Don't write code at random and don't pick an option by coin toss. Ask a
question, and ask it specifically: what exactly is unknown, which options you
see, how they differ in consequences, rather than "what's the best way to do
it?".

Do the same when there are several ways and the documentation singles out none
of them: name the options with their consequences and ask, rather than silently
choosing for me.

The exception is cosmetic trifles that don't change behaviour and that I haven't
discussed: which exact whitespace character, what name a private constant has.
Here take the simplest option, name it in one line in the report and don't build
an analysis around it, because time spent analysing a detail that doesn't
matter to me is wasted.

### Minimal diff

Change only what the task requires. Incidental refactoring, renaming,
reformatting and "while I'm here" are forbidden, because they mix two different
reasons for change into one commit, which means later one can't be reverted
without reverting the other.

Existing interface elements (icons, captions, buttons, spacing) are not removed
or simplified until explicitly asked. What looks superfluous is usually placed
deliberately, and its disappearance will be noticed not by the reviewer but by
the user.

If along the way you saw a real breakage nearby, name it in one line in the
report and leave it for a separate task.

### Synchronous pass

A signature change is not a change of one file. When changing the parameters of
a constructor or function, in the same pass synchronise all call sites, the DI
module where the object is assembled, stubs and fakes, test fixtures. The reason
is that the compiler won't catch everything: it doesn't check reflective DI and
test doubles, so the mismatch will surface at runtime, already after review.

The same applies to a behaviour change without a signature change. Before
changing what a function returns, list everyone who reads its result, including
the model fields it fills, not only the places it is called. One and the same
formatting function often feeds several fields, and if you check only the one
you are changing it for, the others will silently start showing something
different.

Before saying "done", re-read the changed places and make sure that signatures,
DI and call sites agree. Remove only the orphans your own change left behind:
unused imports, variables and functions that nothing references any more.
Dead code that was already there stays and is named in the report. A temporary
debug log gets a unique prefix such as `[DEBUG-a4f2]`, and before the report you
`grep` for the prefix until nothing is left.

### Moving to another host is a change of contract, not only of layout

When a change moves ready components into another container (another
`ComposeView`, fragment or Activity, another `UIHostingController`, a shared
scroll instead of a separate one, a new neighbour above or below in the same
composition), what changes is not only how the screen looks, but also what
these components silently rely on. A screenshot won't show this, because the
static picture matches, while behaviour breaks: scroll to the error, keyboard
handling, insets from the system bars, back, focus.

Therefore the plan for such a change must have a separate item "host contract",
and it is filled in before the code:

1. Read the sources of every embedded component, including components of the
   shared library, not only their signatures. Look for what depends on the
   host: `positionInRoot` / `positionInWindow` / `onGloballyPositioned`,
   `animateScrollBy` / `scrollTo` by a computed offset, `WindowInsets` and
   `imePadding`, `LocalView`, `BackHandler`, `navigationController`,
   `navigationBar.isHidden`, screen dimensions. A parameter like
   `scrollState: ScrollableState` in the signature is a signal that the
   component itself controls someone else's scroll and computes coordinates.
2. For each place found, write down what assumption about the host it makes
   ("the top of the composition coincides with the top of the list", "one
   hosting controller per screen", "the host itself provides the inset from the
   bar"), and whether that assumption holds in the new host.
3. For each screen, compile a list of behaviour on master, not only of
   appearance: what happens on a validation error, when the keyboard opens and
   closes, on back, on re-entry, with long content on a narrow screen. Each
   item of this list is a separate check after the change.
4. If an assumption breaks, that is part of the task's scope and of the plan,
   not something to be discovered by the tester. Broken current behaviour is
   the same kind of defect as a non-working new function.

If the source of an embedded component cannot be read, write that in the plan,
and consider its behaviour in the new host unverified.

### Commits and PRs

- Before creating a PR, read the repository's team rules (for example,
  `.claude/commands/pr.md`) and follow them in full: branch and title format,
  mandatory reviewers, assignee, labels, milestone. The hook that catches
  missed reviewers is a safety net, not a way to learn the rule.
- Don't do `--amend` and force-push until I explicitly ask. A fix after a
  commit is made as a new commit.
- Check the commit title length (usually up to 72 characters) before
  `git commit`, not after push, because a pushed title can no longer be fixed
  without `--amend`.
- Before push, look at `git show --stat HEAD`. Pre-commit hooks like
  `env-reset` do `git add -u` and mix in local environment files, and an early
  `git rm` slides into the next commit, and all of that later has to be
  reverted with separate commits.

### Heavy builds

Don't run full builds and long test runs without an explicit request; I usually
check the build myself, and your run takes minutes and adds nothing. Run
targeted things: a specific test class, the linter over the changed files. If
the change can be verified only by a full build, say so and ask.

Declining the build doesn't cancel the mandatory item about the fact of
verification: then write plainly that you didn't verify with a build and why.

### Context economy

Tokens spent on noise are tokens not spent on the task, so keep the main
context for decisions and push the noise out of it:

- Delegate verbose work to a subagent and take back only its conclusion: test
  runs, log processing, wide code searches, reading documentation. The
  question that decides it is "will I need this output again, or only the
  conclusion?".
- Filter command output before it reaches the context: `tail`, `grep`, `--stat`,
  `--oneline`. A 10,000-line log is read through `grep` for the error, not
  whole.
- Read big files by line range, not end to end. Open the whole file only when
  the task is about the whole file.
- A subagent's "done" is not a result. Before it goes into the report, check
  the diff yourself (`git diff`) and every finding by `file:line`; a finding you
  did not confirm is reported as unverified.
- Before `/clear` or a new session on the same task, write a short handoff
  note into the scratchpad: what is done, where the plan and the branch are,
  what to verify next, which skills to load. Reference files by path instead of
  copying them, and keep secrets out of it.
- When compacting, keep the list of modified files, the "not done" list and
  the verification commands with their last result. Right after a compaction,
  read `~/.claude/egor-ai/compact-state.md`: the PreCompact hook writes the
  branch, `git status` and `git diff --stat` there, so the working-tree state
  does not have to be rediscovered.
- Keep the prompt cache warm. By the Claude Code docs (prompt caching) the
  cache is prefix-based, and a model or effort switch, an MCP server added or
  removed, or a changed tool list invalidates it, while skills, `/rewind` and
  permission-mode changes do not. So pick model and effort at the start of a
  task and do not change them mid-way, and abandon a failed path with
  `/rewind` rather than `/compact`.
- A subagent brief covers one problem area and names: the files it may touch,
  the files it must not touch, the exact errors or test names, and the shape
  of the answer. Run subagents in parallel only when their areas share no
  files. Fix rounds one to three go back to the same subagent with the
  review findings; after three failed rounds stop and bring the question to
  Egor, because the cause is then in the brief or the design, not in the
  implementation.

### When there is no confidence: three plans

If confidence is below roughly 90% regarding the project's documentation, its
style and existing patterns, don't invent an approach. Propose at least three
short plans with the consequences of each and wait for the choice, because a
new approach that doesn't match what the project has adopted I will throw away
anyway, and the time will be wasted.
