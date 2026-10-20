---
paths:
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.swift"
---

## Mobile stack (KMP / Decompose / Compose / SwiftUI)

This section applies only in repositories that have Kotlin Multiplatform with
Decompose and Compose Multiplatform: CRDES (`flutter-card-es`), MMES,
MMMX (`android-mx`), `kmp-common-components`, `idf-kmm-core`. In all other
projects ignore it entirely.

The source of the rules is the team baseline from the MMMX `CLAUDE.md`,
consolidated from `AGENTS.md`. A mechanism confirmed by documentation is marked
with its source, and one explained from memory is marked as memory.

### Coroutines and dispatchers

- Dispatchers, `launch` and `withContext` live in the component. The use case
  stays thin and knows nothing about threads, because otherwise the same use case
  cannot be reused from a place with a different threading requirement.
- Switch context at the `launch(...)` point, not inside the body: then a single
  line shows what the whole coroutine runs on.
- Never update `_model` / `MutableValue` from `ioDispatcher`. Per the Decompose
  documentation (`docs/component/overview.md`) `Value` and `MutableValue` are
  thread-safe, but subscribing to them and updating them is recommended only on
  the main thread. Why exactly the UI breaks is not stated there; from memory,
  not verified: the subscriber receives the value on the thread where the write
  was made.
- Call `SlotNavigation.activate(...)` and all other navigation on the main
  dispatcher. Per the Decompose documentation (`docs/navigation/overview.md`)
  navigation is synchronous, therefore components are created and lifecycle
  callbacks are invoked on the thread it was called from, and navigation from a
  background thread gives unpredictable behaviour.
- Create `CoroutineExceptionHandler` in the component and pass it into
  `launch(...)`, rather than wrapping the coroutine body in `try/catch`.

### State and models

- One `isLoading` per model. Any action raises it, all entry points are gated
  via `if (_model.value.isLoading) return`. A separate flag per action
  (`isAcceptInProgress`, `isDeclineInProgress`) is forbidden.
- All mutable state of the component lives in `Model`, including the loaded
  payload. Do not introduce a `private var` next to `_model`.
- The public `Model` holds only what the UI draws. Orchestration state (an
  entered but not yet submitted value, parameters of the last load, a
  first-load flag) is kept internal.
- Before adding a field, check whether it can be taken from an existing domain
  model, computed in place, or covered by a small fallback
  (`orZero()`).
- Put values into the model already formatted, because the UI must not know the
  formatting rules.

### DI

- All dependencies via the constructor: use cases, dispatchers, formatters, the
  event tracker, the error monitor. `by inject()` is allowed only inside
  `childSlot` / `childStack` factories, where the object is created lazily.
- Give Decompose child components `childContext("...")`, not the parent
  context. Per the Decompose documentation (`docs/component/child-components.md`)
  every child needs its own `ComponentContext`, because components with a shared
  context and identical `StateKeeper`, `InstanceKeeper` or navigation keys
  may crash at runtime.
- After editing a constructor or a DI module, run the project's Koin test with
  `verify()`, if there is one (in CRDES and MMES it is `CheckKoinModulesTest`).
  Per the Koin documentation (`docs/reference/koin-test/verify.md`) `verify()`
  checks constructor parameters against the module declarations and fails on a
  missing definition, so it catches the DI mismatch that the compiler misses.

### Compose and SwiftUI

- Every sub-composable that reads `component.model` calls
  `subscribeAsState()` itself. Do not hoist the model into the parent and do not
  pass it down as parameters, because then the whole subtree recomposes, not
  the piece that changed. In SwiftUI every sub-view declares its own `@StateValue`.
- Take the smallest widget that gives the needed result. `IconButton`
  brings its own minimum size, padding and ripple and because of that shifts the
  layout, so when that gets in the way, use `Icon` / `Image` with `clickable`.
- Do not wrap in `Box` / `Spacer` "just in case" and do not repeat on the child
  a `padding` or a size that the parent has already set.
- One node with a chain of modifiers is better than several nested containers
  that each draw one layer. Every extra `Box`, `Row` or `ZStack` is a
  separate node that has to be measured and a separate level of indentation that
  has to be read, so nesting is worth keeping only where the child
  is really laid out relative to the parent. When collapsing containers into
  a chain, preserve the order, because it changes the result. Per the Compose
  documentation ("Order of modifiers matters") `clickable` before `padding` makes
  the padding clickable too, and after `padding` it does not. Typical replacements:
  - a ring around an avatar is `border` + `padding` + `background` on one
    node, not three nested `Box`es of different sizes with circles of different colours;
  - a clickable icon inside a circle is `clickable` on the same node, not an
    `IconButton` inside a `Box`, because `IconButton` brings its own minimum
    size of 48dp and stretches a smaller circle;
  - a gap between children is `Arrangement.spacedBy(...)` on `Row` / `Column` or
    a top `padding` on the lower neighbour, not a separate `Spacer`; pushing an element to
    the edge is `Modifier.weight(1f)` on the neighbour, not a `Spacer` with a weight;
  - in SwiftUI the same: a ring is `.overlay(Circle().stroke(...))` on the view
    itself, not a `ZStack` of several circles, a gap is `spacing:` on the stack or
    `.padding`, not an empty `Spacer().frame(...)`.
- The gap between blocks of a screen is set by the parent that lays those blocks
  out, not by the block itself. A block does not know who will be its neighbour, so
  an outer margin baked into its root becomes redundant or doubled on another
  screen, and it can be fixed only by editing the block itself. From this follows
  the division of responsibility:
  - a block (section, card, reusable component) does not put a top or bottom
    `padding` on its root and does not add a `Spacer` before or after itself,
    while the gaps between its own children it sets itself;
  - the gap between two blocks is the top margin of the lower block, set
    from outside at its call site. The upper block has no bottom margin, neither inside
    nor outside. This way the gap lives together with the block it separates: if
    the lower block is hidden by a condition, its margin disappears with it, whereas the bottom
    margin of the upper block would be left hanging at the end of the screen. Besides,
    every gap keeps exactly one source, and it does not double
    when somebody adds a margin from the other side;
  - in Compose a block takes `modifier: Modifier = Modifier` as its first
    optional parameter, applies it to the root first in the chain, and adds its
    internal modifiers after it. The parent passes
    `Modifier.padding(top = ...)` there. Per the Compose component API guidelines (section
    "`modifier` parameter") the parameter modifier is responsible for the external behaviour and
    appearance of the component, and the implementation only for the internal ones. Therefore a margin in
    the default value (`modifier: Modifier = Modifier.padding(8.dp)`) is
    a mistake, since it disappears as soon as the caller passes its own modifier.
    Equal gaps the parent sets via `Arrangement.spacedBy(...)`, and
    different ones, as is usual in a mockup, via `padding(top = ...)` on each
    block with its own value, removing `spacedBy`;
  - in SwiftUI the parent sets `VStack(spacing: 0)` and attaches `.padding(.top, ...)`
    at the call site of the lower block, and there is no `.padding(.bottom, ...)` either on the root
    of the block or at its call site;
  - the margin is attached to the node that holds all states of the block: skeleton,
    content, empty, and not to one branch of an `if/else`. Otherwise during loading
    the blocks stick together, and after it the content jumps by the margin amount. In Compose
    this is the `modifier` of the shared container such as `AppSkeletonContainer`, in SwiftUI
    `.padding` on `Group { if … else … }`. This works because per the
    Apple documentation a modifier on `Group` is applied to each of its members, and
    therefore to the branch that is currently shown.
- Give a decorative icon `contentDescription = null`, and a clickable element
  without text a meaningful description. An empty string instead of `null` is read
  by a screen reader as an unnamed element, not skipped.
- Do not `return` inside a Composable to skip a branch that is supposed to
  animate: the node then disappears from the composition and `AnimatedContent` loses
  the animation. Write `if/else`, with `{}` in the empty branch.
- In SwiftUI distinguish two states of one view by a modifier value
  (`.opacity(isExpired ? 0.5 : 1)`), not by an `if/else` branch. Per WWDC21 "Demystify
  SwiftUI" a branch gives the view a new structural identity, because of which state is
  lost, animation breaks and performance drops. A branch is needed only
  when these are really different views, for example skeleton and content.
- If the style name in the mockup matches a token of the project theme (for example,
  `plazo/body/medium` and `bodyMedium`), use the token as is, even when
  this text in the mockup has a different weight, size or line height. The text style in
  the project is set by the design system, therefore a deviation of one property from
  a named style is an inaccuracy of the mockup, not a requirement. From this it follows
  that nothing is added on top of the token: neither `fontWeight = ...` and `copy(...)` in
  Compose, nor `.fontWeight(...)` in SwiftUI. Text with the `labelLarge` style and weight
  W600 in the mockup gets simply `labelLarge`.
- Take paddings and gaps from the mockup as they are and do not align "by eye", and
  if the text in Figma diverges from the specification, trust the specification.
- If the text in the mockup has no named style, carry over its properties
  entirely, all at once: typeface, size, weight, line height, letter
  spacing and colour. Checking one colour or one size is not enough, because
  the remaining properties are then taken by default and diverge from the mockup
  unnoticed. If the theme has a ready style with the same values, use it.
  On iOS the token in both cases is set through the text helper
  (`.bodyMedium()`), not through the bare typeface (`.font(.bodyMedium)`): the bare
  typeface sets only the font and size, and loses the letter spacing and line
  height.
- Every KMP screen has a corresponding SwiftUI view. KMP without iOS is half the work.
  When adding or moving Swift files, synchronise
  `iosApp.xcodeproj/project.pbxproj` and the group path.

### Navigation, formatting, GraphQL

- Do navigation through the existing `Directions` and `safeNavigate(...)` and through
  the already available deeplink / post-init flows, not around them.
- A navigation `Config` is an immutable `@Serializable` `data class` or `data object`
  with `val` only. Per the Decompose documentation (`docs/navigation/overview.md`)
  the configuration stores the child's arguments, not dependencies, because it
  is saved by `StateKeeper` for restoration after process death; dependencies
  are passed in the child factory. Configurations within one `Child Stack` must
  differ by `equals`. Two navigations of the same kind in one parent must have
  different `key`s, because on a repeated key Decompose throws an exception
  (`docs/navigation/stack/overview.md`).
- Format only with the project's formatters (in MMMX these are `MXDateTimeFormat` and
  `MXDecimalFormat`), do not write your own. If the UI adds the currency symbol, do not add
  it again in the component.
- GraphQL: one operation per `.graphql` file, a thin use case, a DI wrapper with
  `withBreadcrumbsLogging(...)`, `apolloClient().andThen { ... }`,
  `dataAssertNoErrors`. There must be no formatting or navigation in a GraphQL use
  case. Update the cache after a mutation via `FetchPolicy.NetworkOnly`.
- A string is added simultaneously to KMP `composeResources/values/strings.xml` and to
  iOS `.strings` (plus `.stringsdict` for plurals). In CRDES and MMES
  there is a third layer, Flutter `es.json` and the generated `L`; do not mix two
  localization systems in one layer. Half-done localization ships to prod
  with the English fallback.
