---
paths:
  - "**/*.kt"
  - "**/*.kts"
  - "**/*.swift"
---

## Feature from a spec and Figma (mobile repositories)

This section applies in the same repositories as "Mobile stack": CRDES, MMES, MMMX,
`kmp-common-components`, `idf-kmm-core`. It is assembled from the corrections I
made after implementing CRDES-46599 (MCR banners, top-up, PA-MCR screens). Each of
them cost a separate round of "did it → showed it → redid it", so do these items
before the first demo, not after a remark.

### Before the first line of code

1. Read the spec rows for the screen ID in full: texts, buttons, transitions and
   the analytics section. If the scope in Jira is wider or narrower than in the
   spec row (for example, Jira says "redesign" while the row changes one number),
   ask before editing, because a rework based on the wider reading is later
   rolled back entirely.
2. Open the Figma node of every variant of the screen and component. If Figma
   does not open, check every path — MCP and `figma_client.py` — and only then
   say "unavailable". Do not guess values without the mockup; ask instead.
3. Read the regulations in `kmp-common-components/docs/regulations/` for the
   layers you touch before the code, not after: the after-the-fact check in
   CRDES-46599 found violations of ten rules at once.
4. Walk the flow with API requests under a test user: GET of the step, POST of
   the choice, GET after it. Look at the real `step`, `data`, `routes`, `stepBack`
   and redirects. Write the code against the stand's response, not against the
   contract description, because it is exactly this walkthrough that exposes
   hardcoded flow names and one-time redirects.

### Layout from Figma

- Check every component variant against its own node element by element: icon,
  radius, fill and its opacity, text style, paddings. A variant inherited from a
  neighbouring one (grey banner → purple) does not count as checked, because the
  new variant in the mockup may have no icon or may have a different radius.
- Take colour and opacity from the specific layer (variable + percentage), not
  from old dumps and not a "similar token". Before: tried `#F0E5F7`, then
  `secondaryContainer`. After: the layer has Secondary Vivid 8%.
- The visible gap is the sum of all sources: the card's padding, the top padding
  of the lower block, the inner padding of the neighbour. Compare the sum with
  Figma. Before: set `top = 20`, but the screen showed 36, because the card was
  already giving 16. After: `top = 4`, and 16 + 4 = 20.
- Gaps around the block being implemented are part of the task, even if they
  physically sit on a neighbour (for example, the `margin` of the amount input
  field above the banner). This is not a "breakage nearby" but part of the screen
  you are building.
- Interactions and animations from the mockup (prototype, designer's notes) are
  part of the design, not an option. A composite element (a button with a badge)
  animates as a whole. In Compose `graphicsLayer { alpha < 1 }` renders the layer
  into an offscreen buffer by its bounds and clips children that stick out, so
  put alpha on the node that includes the badge, and check the press frame on a
  device.
- A layout change is made on both platforms by default — Compose and SwiftUI —
  and is checked as a pair. If the change concerns only one platform, say so
  explicitly.

### Tokens and colours

- A new colour for a single screen is not introduced either as a literal or as an
  extension like `ColorScheme.secondaryVivid`. Find a free M3 slot (`primaryFixed`,
  `tertiary`, etc.), agree it with me and change it in three places at once:
  Compose `Colors.kt`, iOS `Colors.xcassets`, Flutter `AppColor`. Move the old
  readers of the slot in the same pass, otherwise their colour silently changes.

### Assets

- Export the image node itself together with its effects (blur, shadows), not a
  crop of the screen render: a crop cuts the edges and loses the blurred
  background.
- Take the format from the neighbouring assets of that platform: in KMP `webp`,
  on iOS whatever already lies in that catalog (`png` 1x/2x/3x or `pdf`). Convert
  before adding to the project.
- After adding, compare the image 1:1 with Figma on a device: edges, background,
  sharpness.
- Do not refute a visual defect I am talking about with your own screenshot.
  Reproduce it under my conditions (device, density, theme) and fix it.

### Step engine and backend contract

- One spec screen — its own component. Introduce shared code only if the screens
  match almost entirely; otherwise you get one component with an `if` on state
  that three screens change at once.
- The standard step button is `DefaultContinueSubComponent`, as in the PA-PT and
  BNPL steps, not your own button that navigates by itself.
- Do not hardcode state that the contract returns (action availability, date,
  text), even temporarily. Texts that the backend sends (`params.message`,
  `params.message2`) are taken from params, not from local strings.
- After a POST to a flow, do a GET of the same flow, as the step engine does.
  Without the GET the backend's one-time redirect stays hanging and fires on the
  next entry.
- Send the step result to the flow the step came from. Check the behaviour of
  close, back and "Ahora no" separately for every entry point to the screen: the
  same top-up from the banner and from PA-MCR-2.1 must behave differently.
- Do not embed a special case of one flow as `if (flowName == X)` in the shared
  navigation function — pass a separate callback or parameter.
- A formatter with a pattern and `Locale` (`DecimalFormat`, `DateTimeFormat`)
  comes through the constructor from DI and is named by its purpose
  (`limitFormat`, `retryDateFormat`), not created inside the component.
- `requireNotNull(x)` and `checkNotNull(x)` always with a message:
  `requireNotNull(stepDataEnricher) { "stepDataEnricher must be set before select()" }`.

### Analytics

If the spec requires events in DWH or `user_behavior_events` ("all CTAs and back
actions"), before the code build a table "spec element ID → event name" for all
CTAs and all back paths: the toolbar arrow, Android system back, swipe on iOS.
Make the events in the same pass as the screen, put the table in the PR
description and link to it in the report, because it does not fit in the five
lines of the report. Analytics postponed "for later" surfaces only when someone
starts looking for it in DWH.

### SwiftUI

- `foregroundStyle`, not `foregroundColor`: in the SDK it is marked `renamed:
  "foregroundStyle(_:)"`. There is one exception — the `Text + Text`
  concatenation with a target below iOS 17. There `Text.foregroundColor` is
  needed, because `foregroundStyle` returning `Text` appeared only in iOS 17.
- Pass a colour asset as an implicit member: `.background(.onPrimary)`, not
  `Color.onPrimary` and not `Color(.onPrimary)`. Be careful with `.primary`,
  `.secondary` and `.tertiary`: these names coincide with
  `HierarchicalShapeStyle` and without an explicit type resolve to the system
  style.
- Load images through asset symbols: `Image(.imgMcrInitial)`, not
  `Image("img_mcr_initial")`.
- Pass the string key as a literal: `Text("key", tableName: "Table")`, not
  `Text(LocalizedStringKey("key"), ...)`. Type a component parameter that takes
  a key as `LocalizedStringKey`, not `String`.

### Gradle

Before editing a module's `build.gradle.kts`, read its convention plugin
(`plazo.kmp.compose` and the like) and do not declare dependencies it already
brings. Remove a dependency that looks unused by `grep` only after the module
has compiled without it.

### Strings

Take the text verbatim from the spec row. The key is the same on KMP and iOS, and
the line breaks are in the same places on both platforms.

### Checking on the stand and the device

- Before entering the app and before any conclusion about the backend, check
  which host the build goes to: the `Using baseUrl` line and the request log,
  separately on each platform. Debug host settings survive a reinstall, so
  "built for the stand" does not yet mean "goes to the stand".
- Generate the test user directly in the target state. First look at the
  scenario options (`view/scenarios`), and only then say it cannot be done.
  Before handing over to me, check the state with an API request: banners, the
  current step. If the generator fails on an integration, propose a stub in
  Environment Control. That changes the whole stand for everyone, so enable it
  only with my consent.
- Put the stub on exactly the screen I am checking, and clarify the screen if
  unsure. While the stub is in the build, every report starts with a note about
  it. Having removed the stub from the code, rebuild and reinstall the build in
  the same step, otherwise the old stub remains on the device and I will see
  duplicates.
- Do not touch the device or the emulator while I am working on it. If unsure
  whether it is free, ask.
- Do not keep polling the backend for longer than five minutes without changes:
  stop, say what you see, and ask whether to keep waiting.
- Before the demo, compare the screens with Figma and the iOS ↔ Compose pair
  yourself, without waiting for me to send a screenshot with a discrepancy.

### PR and review

- After every batch of commits to an open PR, update its description: checklist,
  verification, Figma links and screenshots, as the regulations require.
- Reply to every review comment briefly: "Fixed in <sha>" or one phrase on why
  not. Fix valid remarks.
- Check the findings of subagents and review bots yourself by file:line before
  passing them to me. Call a finding you did not confirm unverified.
