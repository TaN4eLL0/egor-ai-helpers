## Fixing crashes and bugs

When the task sounds like "it crashes", "падает", "doesn't work", "bug",
"regression", or comes with a stack trace, load the `fix-crash` skill before
reading any code and follow it to the end. The skill is the full protocol; the
part that must never be missing is repeated here:

- A change to the code is applied only at a confidence of **93% and above**,
  and the percentage is built from five verifiable items (cause established,
  fix removes that cause, blast radius known by readers on both platforms,
  regressions closed, not a deferred problem), never named by eye.
- Below the threshold the fix is not applied; instead go get data, ask
  specific questions, or propose a diagnostic step.
- If Egor orders the fix below the threshold, apply it, name the percentage
  and list what stayed unverified.
