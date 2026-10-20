## Fixing crashes and bugs

Everything from the "Communication style" section keeps applying. Here is an
additional requirement that kicks in when the task sounds like "it crashes",
"it falls over", "it doesn't work", "bug", "regression", or when I bring a
stack trace.

### Threshold for applying

Apply a change to the code only at a confidence of **93% and above**. Confidence
is not "it should help", but the combination of four statements:

1. the change removes the **cause**, not the symptom;
2. it doesn't break anything else;
3. it doesn't create new crashes and bugs;
4. nobody will have to come and fix something right after it.

If at least one of the four is in question, the threshold is not met. Then do
**not apply** the change; instead do one of three things: go get data
(documentation, the library's sources, the issue tracker, an internet search),
ask me specific questions, or propose a diagnostic step (a log, a metric, an
attempt to reproduce) instead of a fix.

Fixes in the "try it, maybe it helps" genre are forbidden entirely. If I have
explicitly told you to apply at a confidence below the threshold, apply it, but
name the percentage and list what remained unverified.

### How the percentage is calculated

The percentage cannot be named "by eye": that is exactly the made-up number that
the "Reliability" section forbids. It is assembled from five items, and for each
one you must be able to say what confirms it. If you can't confirm an item, it
doesn't count, however plausible it looks.

| Item | What confirms it |
|---|---|
| The cause is established, not assumed | Stack trace, log, reproduction, reading the code with the file and line named |
| The change removes exactly this cause | An explanation of the mechanism: it was like this, now it is like this, why the crash is no longer possible |
| The blast radius is known | A list of all readers of what changed on both platforms: `grep` over callers in Kotlin and in Swift, not "seems like nobody else" (see below) |
| Regressions are closed | Which tests cover the changed place, whether they were run or not, and with what result. Without tests, only the screens you saw yourself after the change |
| It is not a deferred problem | Not a `try/catch` on top of the symptom, not a suppressed warning, not a `?:` instead of working out where the null came from |

Give the estimate in one line before the change, with a breakdown of the
uncovered items. For example:

> Confidence 96%: the cause is in `Client.kt:42` (NPE on an empty response, it
> is in the stack trace), the change returns an error instead of dereferencing,
> two callers, both in `SyncWorker`, covered by `ClientTest`, ran it: 18 passed.
> Nothing uncovered.

Or like this, when the threshold is not met:

> Confidence 70%: I see the cause from the stack trace, but I don't know the
> blast radius: `parse()` is called from six places, and I haven't checked how
> three of them behave on an empty response. I am not applying the change.
> Clarify: should `parse()` accept an empty response at all, or should an empty
> response be cut off higher up?

### The blast radius is counted by readers, not by calls

The blast radius of a change is everyone who reads what changed, not only the
place the change is made for. In a KMP project one thing almost always has
several readers. A Koin module from `commonMain` is built by both Android and
iOS, so a feature added for an Android screen will also appear on the iOS
screen, which possibly already draws the same thing itself. The step's data is
read by the UI, the validator and the submission to the backend, so an extra
field in it breaks the submission even though the UI looks right. The inset
from the system bars is set by both the host Activity and Compose, so a second
source of inset creates states in which there is none at all.

From this follow four mandatory steps before the change:

1. List all readers of what changed on both platforms: `grep` by the name of
   the feature, field, module or modifier, both in Kotlin and in Swift, not
   only by the function name.
2. For each reader, write in one line what it will see after the change.
3. If one thing (a bar, an inset, a scroll to the error) is already drawn or
   computed by two places, don't add a third; reduce them to one source. Two
   sources that update at different moments are the cause of the bug, not its
   background.
4. Check not only the fixed screen, but also the other readers, and the step
   that comes after the fixed one, because breakage from a shared thing most
   often shows up not where it was fixed.

A reader you didn't check doesn't count, and then the item "The blast radius is
known" is not met, which means the threshold is not met. A screen you couldn't
reach (for example, the steps after the SMS code or scoring) name in the report
as unverified, in words, rather than hiding it behind a general "verified".

### What not to do when analysing a crash

- Start with the change. First the cause, then the change.
- Fix several places "just in case" when the cause is established in one.
  Every extra change widens the blast radius and lowers confidence.
- Replace the analysis of the cause with suppression: `try/catch` without
  handling, `!!` → `?:`, a null check without an answer to the question of
  where the null comes from.
- Silently change behaviour beyond the crash: refactoring nearby, renames,
  "while I'm here". That is a separate task and a separate decision.
- Name a percentage without the breakdown by items.
- Make a failing test pass by weakening it: `@Ignore`, a commented-out
  assertion, a loosened expected value. A failing test is investigated as a
  bug, because the test is the only thing that says the fix works.
- Attempt a fourth fix after three failed ones. Three misses mean the cause
  is not where you are looking, so stop and discuss whether the architecture
  itself is wrong before touching the code again.

### A regression test must fail without the fix

A test written for the fix proves something only if it fails on the old code.
So after writing it, revert the fix, run the test and see it red, then restore
the fix and see it green; that pair of runs goes into the report as the fact of
verification. If no test seam reproduces the real pattern of the bug, say so
in the report instead of writing a shallow test that passes either way.
