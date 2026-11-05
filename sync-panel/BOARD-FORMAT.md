# Board format

The reference half of [`sync-panel`](SKILL.md): the item and its decision context, decision pages, the theme, the auto level, the page, the panels, the checker, the helper, the Loose-ends buttons, grill me, steering notes, report bundles, the folder. Everything here is created once and then edited by anchor.

## The item

One item is one `<li class="item">` carrying its data as attributes, with the human text inside. Attributes are the record; the page's script derives everything else and writes none of them. Agents change attributes only through the edit tool's anchored edits, never by reading the file and writing it back.

```html
<li class="item" data-id="L5" data-section="loose-ends" data-actor="owner" data-since="2026-10-28" data-changed="2026-10-28T17:17:00Z" data-rel="after:N1">
  <h3><a href="https://host/owner/repo/pull/845">Title as the owner would read it</a></h3>
  <p class="next"><b>owner</b> the one next action, after #845 and #851</p>
  <p class="links"><a href="https://host/owner/repo/pull/851">851</a> <a href="https://host/owner/repo/issues/840">840</a></p>
</li>
```

| attribute | meaning |
|---|---|
| `data-id` | stable, never reused. Prefix by first state (N / R / L / D); the edit tool assigns the next free number inside the same locked edit that inserts the item, so an agent never reads it and writes it in a later step |
| `data-section` | `needs-you` / `running` / `loose-ends` / `done`; must equal the `<section id>` it sits in |
| `data-actor` | who moves next: the owner, the coordinator, a named agent role, `lane`; `none` on Done |
| `data-since` | date the item first existed; kept on a move |
| `data-changed` | ISO UTC time of the last edit; stamped on every edit; the "changed" cell reads it |
| `data-due` | required on Running, optional elsewhere; the checker flags it once passed |
| `data-check` | required on Running, optional elsewhere: the command that proves the outcome exists (exit 0). Trusted input written only by the coordinator, never built from tracker or message text, because the checker runs it |
| `data-rel` | optional, space-separated `verb:ID`. `decides`, `unblocks`, `closes` point from this item; `after`, `needs`, `blocked-by`, `waits` point to it; `see` is undirected |
| `data-mechanism` | optional path of the item's `spell-it-out` page (the page links it as a `file://` URL) |
| `data-group` | optional theme id (`G1`, never reused): the item belongs to that theme record. One theme per item |
| `data-reply` | optional `text \| text` (`|` separates replies): the short replies the owner would type ("go release"), rendered as chips; a click sends the reply (The helper) |
| `data-options` | optional `A text\|B text`, with `data-recommend="A"`: the item's choices as chips, the recommended one starred; a click sends `A — text` (The helper) |
| `data-actions` | optional `Label=kind \| Label=kind`, written by the item's coding agent (a kind such as `explain` or `snooze:<date>`): extra buttons, each sending `action:<kind>` (The helper). The board renders only the buttons an item declares, plus the default Done on an item that declares no chips (The helper) |
| `data-ai-owner` | required in Needs you: the agent(s) waiting on the owner's answer, space-separated; shown as "for <name>" on the item; the helper sends each click to them |
| `data-complexity` | required in Needs you: `low`, `medium` or `high`, how much the decision needs beyond its brief and options (Decision context) |
| `data-category` | required in Needs you: `architecture`, `security`, `changes-ruling`, `irreversible`, or `other` alone, space-separated; who decides it at each auto level (Auto level) |
| `data-ruling` | required with `changes-ruling`: the owner ruling the decision would change, as a URL, a `file://` path with `:LINE`, or a short cite |
| `data-auto` | `AGENT LEVEL OPTION`, written only by the edit script's `decided`: the coordinator took this decision on its recommended option under that level (Auto level) |
| `data-auto-category` | written with `data-auto`: the categories the decision was routed on |
| `data-overridden` | the stamp of an auto decision the owner overrode, written by the edit script's `override`; the owner decides the item from then on |
| `data-lane` | required on Running: who works the item, `term:<handle>`, `via:<AGENT>` or `none`, written by the dispatcher with the edit script's `lane`; a move out of Running or a close drops it (Steering notes) |
| `data-deprio` | optional, Loose ends only: `YYYY-MM-DD`, written by the item's agent with the edit script's `deprio` and removed by `undeprio`; the item renders in the De-prioritized strip (Loose-ends buttons). A move out of Loose ends or a close drops it |

Inside: the `<h3>` title, linking the primary PR, issue or page (a Done title links the deliverable when one exists); then `<p class="next"><b>actor</b> next action</p>` for anything not Done; then, when the item cites more than one reference, `<p class="links">` with one `<a>` per further PR, issue, comment or page, so a `#NNN` written in the text always has a link to click. The script turns the title link and each anchor in the links row into chips in the link column (a link repeated in both appears once), removes the row, and leaves the title as text. A chip reads `#845` for a PR or issue, `#788 ↳` for a comment, the file's name for a local file or a file in the tracker (without a markdown, HTML, text or log extension), and the hostname for any other link; a file chip shows only its icon until the item is expanded, the name in its tooltip. The script also hides the `<b>actor</b>` prefix because the who column says it; adds the who, id, age and changed cells and the explain button (under **more**, absent on Done); tints rows whose actor is the owner; sorts rows on the page (due first, then oldest; Done newest first) without touching file order, so an added item goes at the end of its list.

**Local links** are absolute `file://` URLs, optionally ending in `:LINE[:COL]`, and stay that way in the file. At render time the script rewrites a link to a local text file (markdown, text, code, config, logs, or no extension) to the owner's editor URL scheme, such as `zed://file/`, keeping the `:LINE[:COL]` suffix and putting the original URL in the tooltip. Folders, images, PDFs and every other type keep `file://` for the default app; `.html` opens in the browser.

**Decision context.** A Needs-you item carries what the owner needs to decide without hunting through links: three body lines after the next action, in this order, each on one line so the edit script can rewrite it.

```html
  <p class="brief">One to three plain sentences: what this is, what is being chosen, what happens next.</p>
  <dl class="terms"><dt>X2</dt><dd><a href="file:///abs/path/report.md:120">one-line plain meaning</a></dd></dl>
  <p class="links"><a href="https://host/owner/repo/pull/851" title="what this link covers">851</a></p>
```

- **Brief**: shown when the item is expanded, above the chips. It picks up from the decision or work it continues (Decision pages, Continuity).
- **Terms**: every shorthand token in the item's options, next action or brief, each linked to the exact place it is defined (a file with `:LINE`, or a URL with an `#anchor`); shown expanded, under the brief, as "TERM: meaning".
- **Link notes**: the `title` on each links-row anchor says what that link covers; an expanded item shows each note beside its chip. A `title` on the `<h3>` link shows the same way and is optional. A tracker link (issue, PR, comment) is noted as the agents' record, for diagnosing and debugging the agents' work: `title="agents' record: the slice plan"`.
- **AI owner**: `data-ai-owner` (attribute table).
- **Complexity**: `low` when the brief and the options carry the whole decision; `medium` when a question needs its trade explained, or there are several; `high` when the answers interact or one is costly to reverse. At medium or higher the title links a decision page (next section).

**Badges**, in the changed cell, short and relative, allowed to wrap: `overdue 3 d`, `due 10-30`, `stale`, `check` (the item has an outcome check; the command is the tooltip). Nothing else.

## Decision pages

A Needs-you item of medium complexity or higher links a **decision page**: one private local `.html` page, in the board's folder or a bundle's entry page, that puts the item's open questions to the owner. It is the page the owner reads. Its order:

1. **The questions, plain**, under exactly that heading, `<h2>The questions, plain</h2>`, which the checker reads as the mark of a decision page. A title naming how many decisions and what they gate; a meta line ending in one continuity line (what is already ruled, linked; the page carries only what it leaves open); then the questions, numbered, each one plain sentence ending in "?", at most one sentence picking it up from what it continues, "Recommended:" the answer, "Blocks:" what waits on it. All of them on the first screen at 1280 × 800; questions that do not fit are two pages.
2. **Each explained.** Per question, in the same numbering: a heading naming the choice, one paragraph of at most five sentences on the trade (what each answer costs, whether it reverses, the precedent it follows).
3. **The material the questions touch**, only as far as they need it. One mechanism: its flow and rule, the page built with `spell-it-out` in its decide order, its path recorded as `mechanism`. A list, an audit or a comparison: the rows the questions turn on as a table drawn as `graph-it` says, the full material linked, the page held to `spell-it-out`'s render checks (its step 6) except the flow diagram.
4. **The agents' records** it came from (issue, PR, comment), each labelled as a record. They close the page as one visible line; a `spell-it-out` page also carries them in its Details.

- **Continuity.** Each question picks up from the ruling or work it continues, in plain words ("you ruled X; this asks Y"), so the owner places it beside what they already decided.
- **Ruled once.** Avoid restating previous decisions unless clearly central for the mechanism; when restated, briefly and once: one line naming the ruling, linked to where it was made.
- **Length** follows the complexity: parts 1 and 2 are bounded per question, part 3 by what the questions touch.
- **Page mechanics** (plain words, components introduced, phone width, both schemes, nothing remote) as `spell-it-out`'s [Contract](../spell-it-out/HTML-FORMAT.md#contract) says.

The head of an invented page, continuing an earlier ruling:

```html
<h1>Two decisions before per-route limits ship</h1>
<p class="meta">2026-11-03 · private · you chose per-route counting on 2026-10-30 (<a href="…">record</a>); this page carries only what it leaves open</p>
<h2>The questions, plain</h2>
<ol>
<li><p><b>When a route has no limit of its own, does it share the client's 100 a minute?</b></p>
<p>You chose to count per route; this asks what a route missing from the table falls back to.</p>
<p>Recommended: share the client's 100. Blocks: the table migration.</p></li>
<li>…</li>
</ol>
<h2>Each explained</h2> …
<h2>The mechanism these questions touch</h2> …
```

## The theme

Items that belong together, often because they are one decision for the owner, carry `data-group`; the theme is a record of its own, in its own section above Needs you, with a title and one next step:

```html
<section id="groups">
<h2>Themes</h2>
<ol class="groups">
<li class="group" data-gid="G1" data-actor="owner" data-changed="2026-10-30T17:42:56Z">
  <h3>Theme as the owner would name it</h3>
  <p class="next"><b>owner</b> the one next step for the whole theme</p>
</li>
</ol>
</section>
```

Members stay in the state they are in; the theme adds a view across states and leaves each item where it is. A theme whose work is done gets `data-state="closed"` and its id stays taken.

## The auto level

The board's **level** is one line under the header, written only by the edit script's `auto`:

```html
<div id="auto" data-level="security" data-changed="2026-11-04T16:00:00Z" data-source="click:<click id>"><b>auto: security</b> — you keep security, changes to your rulings, irreversible actions</div>
```

**One reading.** The edit script and the helper read the level only from that one line, at the start of its own line and outside a comment, its attributes first-wins, and only while the file's tags, commented-out ones included, carry `id="auto"` exactly once. Text that mentions the line, such as a brief about it, is not a tag and does not count, and neither does an attribute value that mentions it; a quoted value may hold `>`, and an id counts as the browser decodes it. Anything else reads as `off`, so a commented-out old line or a reordered attribute fails safe in every runtime. The checker reads the line both as the page does and as the edit script does, and flags `BAD AUTO LEVEL` when the two disagree; `auto` refuses to write until the line is one again.

**The table** is the whole rule. The edit script holds it once, as the function `route(categories, level)`, and the checker imports it. The page script mirrors the level names and the owner-kept sets, and the helper the level names; each mirror is its declaration, `NAME = <literal>;` exactly once, with nothing else in the file writing it, and the checker holds them to that.

| level | the owner keeps |
|---|---|
| `off` | everything |
| `architecture` | `architecture`, `security`, `changes-ruling`, `irreversible` |
| `security` | `security`, `changes-ruling`, `irreversible` |
| `decision-changes` (only decision changes) | `changes-ruling`, `irreversible` |
| `full-autopilot` | `irreversible` |

- **Route**: an item is the owner's when any of its categories is kept at the level; otherwise the coordinator's. An unknown or missing level reads as `off`, and an unknown category, or none, as the owner's. The edit script's `route CATEGORY...` prints `owner` or `coordinator`.
- **Categories**: `architecture` for structural decisions; `security` for guardrails, isolation and server configuration; `changes-ruling` when the decision would reverse, supersede or narrow a recorded owner ruling, or when the agent cannot tell, with `data-ruling` naming it; `irreversible` for actions that cannot be taken back or that leave the owner's hands (publishing a package, spend above a standing cap, deleting data, promoting a release), which every level keeps; `other` for the rest.
- **An auto decision**: the item goes where the decision points, with its options and recommendation, brief, complexity and AI owner, and the edit script's `decided ID AGENT "why"` writes `data-auto`, `data-auto-category` (the categories it routed on) and the note `<p class="auto-note">`, one sentence on which option was taken and why. From then on `category` refuses the item, and the checker flags it when its categories differ from the recorded ones. A category changed before `decided` is visible only through the badge, which names the categories the decision was taken as: that is a trust boundary, not a check. In the same locked edit it re-reads the level and the item's categories, and exits 3 when the owner keeps the item, so a level moved meanwhile sends it to Needs you. It refuses an item in Needs you, an item missing its decision context, and an item carrying `data-overridden`. A move or close carries the stamp and the note, and a close keeps a stamped item's options so an override returns the whole decision.
- **The slider**: the page renders the line as five stops above the band, the current one filled, with what the owner keeps at that level and when and how it was set. A click sends `POST /level` with `{cid, level, version}` (version is the line's `data-changed`); the helper validates the level against the table, records the click under the item id `auto`, sends it to the coordinator with the wake and the command to run, and leaves the board file alone. The coordinator applies the newest level click only: `auto LEVEL CID` takes a click that is the last level click in the inbox and newer than the current line, records `data-source="click:CID"`, and refuses an older one, so an old click id never brings back a level the owner has since lowered; re-applying the click the line names changes nothing. The level is set only from the owner's click or the owner's words: a level the owner typed is `auto LEVEL --typed "the owner's words"`, the words kept on the line (`data-quote`) and shown beside it, and `off` alone needs none. The page shows the click as pending, with not delivered and retry as for every click, until the line names the click or was written after it at that level; a line written after it at another level shows the click as superseded, naming the board's level. The helper takes one JSON object whose fields are strings, and a version that is a `data-changed` stamp or empty.
- **Override**: a stamped item shows its stamp as a badge ("decided by AGENT under auto=LEVEL as CATEGORIES: OPTION, its text"), its note, the note field and an **override** button, and no option chips, since the decision is taken; row view adds a short badge beside the age. The answer `override` is the one answer a stamped item takes, in any section, Done included; it goes to the coordinator with the wake and a `sync-override` payload carrying the stamp. The coordinator undoes what the decision started where it can, then runs `override ID`: the item returns to Needs you with the owner as actor, its decision context, `data-overridden` in place of the stamp, and the note saying what was overridden.
- **Older helper**: the helper announces `auto-level` among its features; on a helper without it the stops and override are disabled with a visible note. The `file://` page copies `auto: LEVEL` or `<id>: override` (The helper, No silent copy).

## The page

One `index.html`, no build step. A `<meta http-equiv="refresh" content="60">` keeps it current; state survives the refresh: per viewer in local storage, each section's view and collapsed state and the open help panel; in session storage, the scroll position, the expanded items and the graph overlay's zoom. Every storage access sits in try/catch, and without storage the defaults render. Parts, top to bottom:

1. **Header**: title, who the board serves, the refresh interval, the last-checked stamp the checker writes, "N new, moved or yours changed since HH:MM" with a **mark seen** button, and "helper on" or "helper offline".
2. **Auto level**: the five-stop slider (The auto level). **Band**: the Themes panel across the top while any theme is open, then three panels (next section), each with a one-line heading that names the question it answers.
3. **Four sections**, `<section id="needs-you">` through `done`, each an `<h2>` (the script appends the count and a `rows | tiles` toggle; clicking the heading collapses the section) over a column-header row and an `<ol class="items">`; without the script they render as one plain table.
   - **Tiles**, the default in Needs you: id and title, due or age in the corner, the next action, the reply and option chips, one meta line (link chips, relations, edited age, the changed dot) and a **more** button for the rest (mechanism glyph or explain button, outcome check, full link labels).
   - **Rows**, the default elsewhere: one line each (id, title, who, due or age, the dot), which a click expands in place to the next action, chips, links and relations.
   - Tiles pack masonry-style: each spans as many 1 px grid rows as its measured height (no row gap, the spacing inside each span), and a resize observer repacks a section whenever a tile changes size. The grid's forward-only auto-placement lets a short tile start in the gap under a shorter neighbour but never above a tile that sorts before it, so reading and keyboard order stay the sort and theme order; CSS columns would pack tighter and break that order. Rows view drops the spans, and without the script tiles take their natural height (`align-items: start`) and never overlap.
   - In Needs you, an item whose answer was delivered (sent or seen; neither failed, answered an older version, nor edited after the answer) steps into a collapsed strip at the bottom, "Answered, waiting on the agent (N)", one dimmed line each with its answer and state, until its AI owner moves it. The section count covers only the items still to answer.
   - In Needs you, every expanded item gets a **grill me** button (Grill me).
   - In Running, every expanded item gets the **include feedback** box and the notes sent on it (Steering notes).
   - In Loose ends, every item gets the kick-off and de-prio buttons, and a de-prioritized item steps into a collapsed strip at the end (Loose-ends buttons).
   - The who column is dropped in Needs you, where the owner is the actor by definition, and in Done, where nobody is; in Running and Loose ends, when no item left visible by the theme filter has an actor.
   - An empty section collapses to its header and one line. Done shows the last 24 hours; older Done items sit behind one "N more" row.
4. **How this page works**: a collapsed `<details>` with the item schema, the state flow as a small diagram, and the panels table below.
5. The vendored diagram library and the page's own script, a file in `assets/` (the helper's CSP allows no inline script), which reads the DOM once and renders from it.

Stylesheet in `assets/`: tokens on `:root`, dark by `prefers-color-scheme`, the owner's tint as its own token, column widths in one grid template shared by the header row and the rows, a phone breakpoint that turns each row into a meta line (who, id, link, age, changed) over the title and next action, and hides the band's charts. No web fonts, no remote request of any kind.

## The panels: which form answers which question

Per panel, the form below, drawn as `graph-it` ([FORMS.md](../graph-it/FORMS.md)) says. The board's own questions and the forms that answer them:

| question | form | reason |
|---|---|---|
| what must I do? | the owner's rows, tinted, Needs you first; no chart | position is the most accurately read channel; a list in priority order needs no decoding |
| who waits on whom? | a count matrix, one row per actor present by open state; clicking a cell filters the rows; the owner's cells outside Needs you marked | a handful of integers; a chart adds ink, not precision |
| how long open? | one bar per open item on a shared day axis, a now line, a tick at `due` | length on a common baseline is the next best channel; dots would hide duration. Weak while every item is a day old; it earns its place as items age |
| what unblocks what? | chips on the rows always, for every relation; in the panel only links between open items count and are drawn (an end in Done or off the board drops the edge): a node-link graph while there are at most twelve, an adjacency matrix beyond; its **expand** button opens a full-screen overlay that always draws the node-link graph, with zoom, pan, fit, and Esc to close (focus returns to the button) | node-link reads for sparse chains and becomes a hairball past a dozen edges; a matrix stays legible at any density but hides paths, which the overlay gives back |
| what belongs together? | the Themes panel (one row per open theme: counts per state, done of total, next step; a click shows only its items); a stripe on each member; inside each open state, members kept adjacent under one label row, which in Needs you reads "one decision" when the theme's next step is the owner's; a theme chip only on a member that has no label row | adjacency and a shared colour group without moving items out of the state the owner acts on; one decision row replaces several. Closed themes stop striping |
| what changed since I looked? | a dot on each item that is new, changed state, or is the owner's and was edited since the last **mark seen**, and the count in the header | the 60 s refresh makes an automatic "last visit" meaningless, so the mark is the owner's own; it records what the page showed when it loaded, so an edit landing while the owner reads still counts. Coordinator housekeeping on other rows stays undotted |
| what do I answer? | reply, option and declared-button chips (or the default Done) under the next action, the recommended option starred; a note field on the expanded item; after a click, its state (The helper) | a click replaces retyping a reply the board already knows, and the state says whether it arrived |
| counts by category | numbers in the section headers and a one-line flow (opened, closed, touched in 24 h; stale and overdue each shown only when non-zero) | three numbers read faster than three areas |

An inbound verb (`after`, `needs`, `blocked-by`, `waits`) is rendered reversed and relabelled (`before`, `needed by`, `blocks`, `awaited by`), so the graph keeps FORMS.md's arrow direction; `see` is drawn as a line with no arrowhead, and as an open circle in the matrix.

## The checker

`check.py`, standard library only, no network. It parses `index.html` with the HTML parser, collecting every element with `data-id` (and every theme with `data-gid`), the `<section id>` enclosing it, its title text, its next-action text, its links, and its brief, terms and link notes; a void tag such as `<br>` closes itself. Flags, one line each with the id (and the line number where the parser has one):

- `DUPLICATE id`: the same `data-id` twice, counting the archive pages (whose ids also count as existing for `BAD REL`)
- `SECTION MISMATCH`: `data-section` differs from the enclosing section
- `BAD data-changed` / `BAD data-due`: unparsable
- `OVERDUE`: `data-due` passed
- `NO NEXT ACTION`: a Needs-you item with no next action, or one that only names the actor
- `NO CHECK`: a Running item without `data-due` or without `data-check`
- `UNLINKED REF`: a `#NNN` in an open item's title or next action that no link in the item points at (`/pull/NNN` or `/issues/NNN`); Done items are exempt
- `BAD REL`: a `data-rel` entry that is not `verb:ID` with a known verb and an existing id
- `LONG NEXT`: an open owner row whose next action is longer than 15 words
- `BAD OPTIONS`: `data-options` that does not parse as `LABEL text|…`, or a `data-recommend` that is not one of its labels
- `BAD ACTIONS`: a `data-actions` entry that would show no working button. Valid is `Label=kind` with a non-empty label and a kind of one lower-case letter then up to 40 word characters, `:`, `.` or `-`
- `ACTIONS RULE DRIFT`: the page script or the helper no longer carries that rule verbatim. The checker holds it once and the two mirror it, so nothing the checker passes is refused by the board or the helper
- `GROUP UNKNOWN` / `DUPLICATE gid`: an item naming a theme that does not exist; a theme id used twice
- `GROUP NO NEXT` / `GROUP DONE`: an open theme with no next step; an open theme with no open item (close it)
- `GROUP MISPLACED`: a theme record outside `<section id="groups">`, where the page cannot see it
- `GROUP CLOSED`: an open item tagged into a closed theme
- `GROUP MISSING`: an open item with no `data-group` whose `data-rel` targets a member of an open theme, or whose title names one as a whole word (the next action is not searched: it routinely lists other ids); tag it or reword it
- `NO BRIEF` / `NO AI OWNER`: a Needs-you item without a brief, or without `data-ai-owner`
- `NO COMPLEXITY` / `BAD COMPLEXITY` / `NO DECISION PAGE`: a Needs-you item without `data-complexity`; a value other than `low`, `medium` or `high` on any item; a medium or high Needs-you item none of whose local `.html` pages (title, links row, `data-mechanism`; the board excluded) exists and carries the questions heading (Decision pages)
- `LINK WITHOUT NOTE`: a links-row anchor on a Needs-you item with no `title`
- `UNDEFINED TERM`: a shorthand token in a Needs-you item's options, next action or brief that its terms do not define. Shorthand is an upper-case group of one to four letters followed by digits (optional hyphen, optional bracketed suffix: `X2`, `QA-4`, `K5(b)`) or by a bracketed suffix alone (`AB(c)`); two joined by a dash are one range token, defined as a range or at both ends. Item ids, theme ids and agent names are excluded, and `#NNN`, dates and version strings cannot match. Model and hash names match too; a one-line definition costs nothing
- `BUNDLE …`: the seven report-bundle flags (Report bundles)
- `DEPRIO OUTSIDE LOOSE ENDS` / `BAD DEPRIO`: `data-deprio` on an item outside Loose ends, or a value that is not an ISO date
- `BAD ID`: an item id outside plain letters, digits and dashes, at most 24 long, which the helper refuses
- `DUPLICATE ATTRIBUTE`: an attribute an item carries twice; the browser and the helper read only the first
- `NO AUTO LEVEL` / `BAD AUTO LEVEL`: no level line (it reads as off); a level outside the table, two level lines, `id="auto"` in the text more often than the page sees it, or the page and the edit script reading different levels
- `NO CATEGORY` / `BAD CATEGORY` / `NO RULING CITE`: a Needs-you item without `data-category`; a category outside the list on any item, or `other` beside another; `changes-ruling` without `data-ruling`
- `BAD AUTO`: a stamp that is not `AGENT LEVEL OPTION` with a level from the table, whose option is not one of the item's, or without `data-auto-category`
- `AUTO MISMATCH`: a stamp whose level keeps one of the item's categories for the owner, or an unknown one, an item with none, or categories that differ from the recorded ones: as far as the file can tell, the decision was not the coordinator's to take
- `AUTO IN NEEDS YOU` / `AUTO NO NOTE`: a stamped item in Needs you; a stamp without its note
- `AUTO RULE DRIFT`: the edit script's table missing or no longer a superset ladder, or a mirror in the page script or the helper that is not its declaration with the literal, exactly once, with nothing else writing it: no second declaration, assignment, index or property assignment, mutating call or alias, directly or through up to two accessors (`KEEPS.security.splice(0, 1)`, `KEEPS.security[0] = ...`)
- `NO LANE` / `BAD LANE`: a Running item without `data-lane`; a lane outside the three forms, a `via:` agent the routing file does not name, a `term:` handle that is one of the routing file's terminals (an owner-facing one, recorded as `via:` instead), or a lane outside Running
- `STALE`: `data-changed` older than three days on an open item

Then one report line per `data-check` (`CHECK <id>`: DONE when it exits 0, OVERDUE when it fails past `due`, else pending, and whether it ran without a shell or through `sh -c`; a command with no shell metacharacter runs without one, under a timeout either way); then the lane-deadline ledger the coordinator keeps, whose overdue lines also count as flags; then the counts per state. Exit 1 on any flag. `--stamp` rewrites the last-checked line through the same anchor tool used for items, falling back to a direct write. The mutation run that proves it: a scratch copy with one planted instance of each defect, all flagged, exit 1.

## The helper

A local server with no dependency beyond its runtime, started and stopped by hand through a lifecycle script (`start`, `stop`, `status`), never as a login item. It serves the board folder at `http://127.0.0.1:PORT/`, so the board opens there with none of `file://`'s limits, and adds `POST /click`, `POST /retry`, `POST /feedback` (Report bundles), `POST /level` (The auto level), `POST /steer` (Steering notes) and `GET /state` (fetched at each page load). It never writes the board file: its writes are appends to the inbox, the one-time bootstrap file (rewritten on each use) and the session file.

- **Self-reload**: the process the lifecycle script starts is a supervisor that runs the helper as a worker child and watches the helper's code file. When the file changes and passes a syntax check, it swaps the worker; a broken edit is logged and the running worker stays. The session secret, the page token and the pending one-time URL persist in a mode-600 session file, written atomically, so the owner's cookie and open page survive a reload; `start` writes fresh secrets and `stop` deletes them. The supervisor's own code is not reloaded. The page retries a send that gets no HTTP answer, a few times, with the same click id, which covers the moment a reload takes.

- **Routing file**: each AI-owner name to its mailbox address and, for the wake, an optional terminal handle (an address that is itself a terminal handle serves), plus the coordinator's name and the helper's own sender label. The helper sends under that neutral label and starts with a clean environment, so it never acts as the agent that launched it.
- **Inbox**: one JSON event per line, append-only: `click` (an answer, or feedback on a report section), `sent` (with the mailbox message id), `send-failed` (with the error), `retry`, `seen`, `woken`, `wake-failed` (with the reason).
- **Wake**: after each delivered owner copy, never the coordinator's notice, the helper types one fixed line into that agent's terminal through the mailbox system, telling it to check its mailbox. One attempt per copy; a failed or skipped wake (no terminal handle, or one that fails validation) is recorded as `wake-failed` and leaves the click sent.
- **States**, in the expanded item and as a short badge in row view:
  - sending: until a copy is confirmed, never shown as sent;
  - sent: the answer and its time, with "agent not woken" after a `wake-failed`, and "unread 30+ min" in the warning colour once a copy has stayed unread that long;
  - seen: by whom and when, from the mailbox's read receipt, which the helper polls while a sent message is unread; it means handed to the agent, and says nothing about acting;
  - not delivered: to whom, with a **retry** button;
  - answered an older version: the click's version differs from the item's `data-changed` at the moment of the click;
  - resolved: the item left Needs you, or was edited after the answer.
- **Note**: a text field on the expanded item, at most 500 characters, kept across the refresh, sent with whichever button is pressed.
- **Default Done**: a Needs-you item that declares no reply, options or actions gets one **Done** button with the note field, so a task the owner performs can be answered, with any detail in the note. The helper accepts `Done` only for such an item. It announces its features in the page it serves, and the page offers a feature only when announced, so a page newer than its helper never sends what the helper would refuse.
- **Linked files**: a page served over http cannot open `file://`, so the helper serves the non-text local files the board links, from one `reports/` folder; the edit script copies a linked non-text file there and links the copy, a snapshot, refusing a symlink, a non-regular file and anything on a hidden path. Text files open in the editor either way.
- **No silent copy**: on the helper page a refused send shows "not sent: <reason>" in the danger colour, opens the item and keeps the note, and copies nothing. Only on the `file://` page, or when the helper does not answer at all, does a click copy `<id>: <answer>` and the note to the clipboard, and the item then says "helper offline: copied, paste it to the agent". The `file://` page carries a banner saying clicks are not sent from it, with a link to the helper page.

**Security baseline**, each requirement proved by a mutation (SKILL.md, Clicks reach the AI owner):

- **Loopback only**: bound to 127.0.0.1, and every request's `Host` equals `127.0.0.1:PORT` exactly, against DNS rebinding.
- **Session cookie**: every route but a health check and the bootstrap needs it; it is `HttpOnly; SameSite=Strict` and set only by a one-time bootstrap URL, which the helper keeps in a mode-600 file and rotates on each use, and the lifecycle script prints.
- **Per-start token and Origin**: a random token, rotated at each start, held only in the mode-600 session file beside the session secret and the pending one-time URL (never in the board file, a URL or a log) and injected into the page the helper serves; required on every POST and on `/state`. Every POST also carries an `Origin` equal to the helper's own.
- **Input**: an open item's id, of plain letters, digits and dashes at most 24 long on every click (an id reaches message bodies, so any other id is refused), an answer that item declares (reply, option or action, or `Done` when it declares none, or one of the four Loose-ends answers when it sits in Loose ends, or `grill` when it sits in Needs you, or only `override` when it carries `data-auto`, the one answer a Done item takes), a Running item with a `term:` or `via:` lane on `POST /steer`, a level from the table on `POST /level`, a note within its cap, a body within a size cap, JSON only.
- **Owner list**: the helper reads `data-ai-owner` once per name, keeping each name's first position, and refuses a list of more than eight distinct names (400, naming the count), for answers, report feedback and grill me alike, so a board edit cannot fan one click into a send per listed name.
- **File serving**: a file is served only when the board links it, its real path (every symlink resolved) lies inside the reports folder, and it is a regular file; a served file gets a sandbox CSP so it cannot act as the board. The hidden-path refusal sits in the edit script's copy step (Linked files).
- **Strict CSP on the board**: `script-src 'self'` with no inline script, `frame-ancestors 'none'`, `X-Frame-Options: DENY`.
- **First-wins attributes**: an attribute an item carries twice is read first-wins, as the browser reads it, so an item can never render with one section or actor and route by another; the checker flags the duplicate.
- **Argv-only process calls**: every mailbox and terminal call is an argument array; request content reaches no shell. The wake's terminal handle must match the mailbox system's plain handle shape, and the item id it types must be plain letters, digits and dashes.
- **Idempotent clicks**: each decision carries a client id that a double click or a retry reuses, and the helper records and sends a known id once. An id already used for an answer is refused for feedback, and the reverse (400). Each mailbox send carries a deterministic request id, so an ambiguous retry is replayed rather than duplicated.
- **Delivery resume**: a delivery cut off by a reload (a click recorded, no `sent` or `send-failed` for a recipient) is re-delivered by the new worker at boot and when the page replays that click id, to the recipients recorded with the click when it was made, never to names the routing file gained since; the same request id makes the mailbox replay a copy that did go out instead of sending it twice. Resume only finishes recorded clicks and constructs none. A copy recorded as sent whose wake has no outcome gets that wake, once, at boot, on a replay and on retry, under the same deterministic request id, and the mailbox copy is not sent again for it.
- **Visible delivery failure**: every send ends as `sent` or `send-failed`, in the inbox and on the page; a malformed mailbox reply is logged and keeps the helper running, and the receipt poll runs at most once every few seconds however often `/state` is fetched.
- **Lifecycle identity**: `stop` kills only a process whose command line is the runtime running this helper, so a recycled PID survives. The worker exits when its supervisor is gone, deleting the secret files only while they still hold its own. `start`, `stop` and `status` never trust the pidfile alone: each also checks whether the port answers, and none reports success while another process holds it.
- **Known residual**: cookies are not port-scoped, so the browser also sends the session cookie to any other server on 127.0.0.1 the owner opens; `HttpOnly` keeps page scripts from it, but that server could log it. The cookie stays valid across reloads for as long as the supervisor runs; only stop then start rotates it.

## Loose-ends buttons

A Loose-ends item can be started, sent for a grilling round, or set aside from the board. Three buttons sit on every expanded Loose-ends item, with the note field (the note travels with the click), plus **restore** on a de-prioritized one:

| button | answer sent | goes to | wake |
|---|---|---|---|
| kick-off | `kickoff` | the item's `data-actor` when the routing file lists it, else the coordinator | yes |
| kick-off grilling round | `kickoff:grill` | same | yes |
| de-prio | `deprio` | same | no |
| restore | `undeprio` | same | no |

- **Where they are accepted**: the helper accepts these four answers only for an item whose `data-section` is `loose-ends`, and refuses them on any other item (400), as it accepts `Done` only for a chip-less Needs-you item. An item needs no `data-ai-owner` for them; the route is the actor.
- **The coordinator** gets the usual notice-only copy, skipped when it is the recipient. Only the two kick-offs wake the agent.
- **The split button**: "kick-off" is the primary button, with a narrow attached caret; hovering or focusing the pair shows "kick-off grilling round" directly below it, and a tap on the caret toggles it, so keyboard and touch reach it too. "de-prio" is a separate, quieter button.
- **De-prioritized strip**: a de-prioritized item renders in a collapsed strip at the end of Loose ends, "De-prioritized (N)", greyed but readable, each with a **restore** button. It is left out of the section count.
- **Precedence**: the page shows an item de-prioritized when it carries `data-deprio`, OR when the helper holds an owner `deprio` click newer than the item's last edit (`data-changed`) with no later `undeprio`. The latest owner click wins while it is newer than the item's last edit; once an agent edits the item after the click, the attribute decides. The `file://` page reads the attribute alone.
- **Kick-off on the item**: after a kick-off the item keeps its place and shows "kick-off sent HH:MM · seen by <agent>" (or "grilling round sent"), "not delivered" with retry, and "answered an older version" when the click came from a page older than the item, as for answers. The badge goes once the item leaves Loose ends.
- **Older helper**: the helper announces `loose-ends-actions` among its features. On a helper without it, the buttons are disabled with a visible note, and nothing is copied to the clipboard.

**What the receiving agent does**, within its next turn:
- `kickoff`: start the item's next action now, and move the item to Running with `data-due` and `data-check`.
- `kickoff:grill`: run steps 1 to 4 of the grilling round (Grill me) against the item's design, with step 5's override when nothing is left for the owner, then move the item to Needs you with `ai-owner` set to yourself. The decision page may be the entry page of the item's report bundle (Report bundles) when the owner should comment on it by section; either way it carries the questions heading, so the checker finds it. The owner answers by the item's chips, or by section feedback on a bundle.
- `deprio` / `undeprio`: run the edit script's `deprio ID` / `undeprio ID`, and nothing else. That makes the page and the `file://` page agree durably.

**Edit script**: `deprio ID` sets `data-deprio` to today's date and `undeprio ID` removes it; both refuse an item outside Loose ends. The checker's `DEPRIO OUTSIDE LOOSE ENDS` and `BAD DEPRIO` flag what a hand edit could leave behind.

## Grill me

The owner can ask for a grilling round on any decision waiting on them. Every expanded Needs-you item carries a **grill me** button after its chips or the default Done, quieter than them, with the note field (the note travels with the click):

| button | answer sent | goes to | wake |
|---|---|---|---|
| grill me | `grill` | each AI owner the routing file lists; with none left, the coordinator | yes |

- **Where it is accepted**: the helper accepts `grill` only for an item whose `data-section` is `needs-you`, and refuses it on any other item (400, naming the item's section). `grill` is the board's own answer: a declared reply of that name sends the grill request on a Needs-you item and is refused elsewhere.
- **Recipients**: the item's `data-ai-owner` names, read as the security baseline's Owner list says (The helper); a name the routing file does not list is dropped. The coordinator gets the usual notice-only copy, skipped when it is a recipient.
- **A request, not an answer**: the item keeps its place and its count, never enters the answered strip, and keeps its chips or the default Done, because the decision is still the owner's. The request has its own line beside any answer's, "grilling round requested HH:MM · seen by <agent>", with sending, agent not woken, requested on an older version, and not delivered with **retry**, as for answers; row view shows a short badge beside the age.
- **Cleared**: once an owner copy is seen and the item's `data-changed` is later than the click, the line and the badge go, and the item's changed-since-you-looked dot shows the new content. Both halves count: the seen copy is the mailbox's own record, which a board edit cannot write.
- **Older helper**: the helper announces `needs-you-grill` among its features. On a helper without it, the button is disabled with a visible "helper too old" note, and nothing is copied to the clipboard. Offline it copies `<id>: grill` like every button (The helper, No silent copy).

**The grilling round** is what the receiving agent does on `grill`, within its next turn:
1. Run the `grilling` skill on the item's decision yourself. Answer every question the code, records or docs answer, and continue from the owner's prior rulings rather than re-asking them. The skill's wait for the user does not apply: you play both roles, and what neither you nor the records settle becomes the page's questions.
2. Deliver or refresh the item's decision page (Decision pages): the questions first, plain, each with its recommendation, what it blocks and its continuity; then each explained; then the material. Proportionate to the decision.
3. Set `data-complexity` to medium or higher and link the page as the item's title.
4. Rewrite the brief and options to the questions that remain, and reply on the item.
5. Leave the item in Needs you. When the round leaves nothing for the owner to decide, say so in the brief and recommend Done, then set complexity low and drop the link: this overrides step 3.

## Steering notes

The owner can steer the agent working a Running item while it works. Every expanded Running item carries an **include feedback** box: a line saying where the note goes, a text field of 2000 characters kept across the refresh, and a send button.

**The lane** is `data-lane`, written by the dispatcher when it dispatches the work, in one of three forms:

| `data-lane` | who works the item | where a note goes | wake |
|---|---|---|---|
| `term:<handle>` | an agent with a terminal of its own, by the runtime's handle | a mailbox message to that handle | one fixed pointer typed into its terminal |
| `via:<AGENT>` | an agent with no terminal of its own (a subagent), or any owner-facing agent; AGENT is a routing-file name | AGENT's mailbox | none: AGENT forwards the note with its own tool |
| `none` | nobody, for now (waiting on CI, a merge, the owner) | nowhere: the box is disabled and says why | — |

A terminal the routing file names belongs to an owner-facing agent, so the dispatcher records that lane as `via:<AGENT>`, and a steering note never types into it. The helper reads the routing file afresh before each send, a retry or a resume included, and refuses the send when the lane has become owner-facing; it reads it again right before the pointer and then always withholds the pointer, though a mailbox message already in flight may still arrive. Either way the item shows the reason as text, asking for the lane to be recorded as `via:<AGENT>`. The edit script's `lane ID VALUE` writes the attribute on a Running item only, checking the form; a move into Running keeps it, a move out of Running and a close drop it.

**The answer**: `POST /steer` with `{cid, id, version, note}`, under the cookie, token, Origin, click-id and version rules of every click. The helper accepts it only for a Running item whose lane is `term:` or `via:` (400 otherwise, naming why), with a note of 1 to 2000 characters, control characters other than line breaks removed.

**Delivery** keeps the note's text in the mailbox body, indented, and out of every terminal:

- `term:` — one message to the handle, then the pointer: `You have sync-board a steering note on <id> from the owner: run <mailbox check>.`, as an argument array. An idle agent takes the pointer as a prompt and reads its mailbox at once; a busy one takes it as its next prompt, after its current step. A handle outside the runtime's plain shape is recorded `send-failed` and `wake-failed`, with nothing run.
- `via:` — one message to AGENT's address, asking it to forward the note word for word to the lane it runs.
- The coordinator gets the usual notice-only copy, skipped when it is the `via:` agent.

The pointer is the helper's existing wake, which lands in both states and creates no orchestration state; a dispatched task would add a second assignment beside the one the lane already holds.

**On the page**, under the box, every note sent on the item, newest first, read from the inbox, the earlier ones past the newest five behind one toggle: its time, its text, and its state (sending, sent to the handle or agent, woken or not woken, seen once the mailbox marks it read, not delivered with retry, and "sent on an older version" when the page was older than the item). The latest note's state is a short badge beside the age. The helper announces `steer-notes` among its features; the `file://` page copies `<id>: steering note: <text>` and says so. The notes are the board's record of what was said: they live in the inbox, and the board file stays as the edit script leaves it.

**What the receiving agent does**: reads its mailbox, takes the note into its current work with the owner's words governing, and acks the delivery, which the page then shows as seen. A `via:` agent forwards the note word for word to the lane it runs, then carries on.

## Report bundles

A **report bundle** is a folder of pages the owner reads from one board item, with comments per section or on selected text that reach the item's AI owners like a click, many in one submit. This section is the whole contract: a lane builds and publishes a bundle from it alone.

**The design.** Report pages stay sandboxed, in an opaque origin, so no script a lane writes can read the board's token or post as the owner. A **wrapper** page the helper writes frames the report and does all the sending, and the owner types every note in the wrapper. **A page can point at a section, or at a quote of its own text that the helper verifies; it can never send a note or a decision.**

**The folder.**

```
my-report/
  bundle.json      the manifest (required)
  summary.html     pages; every section the owner may comment on is an element with a stable id
  details.html
  style.css        vendored assets; a diagram library is copied in, never loaded from the network
```

Allowed files, with exactly these lowercase extensions: `.html .css .js .svg .png .jpg .webp .woff2 .json`. Regular files only, with no symlinks and no hidden files or folders; subfolders are fine. Caps: 20 MB in total and 500 files.

**`bundle.json`.**

```json
{ "title": "Design review", "entry": "summary.html",
  "pages": [
    { "file": "summary.html", "title": "Summary", "sections": [ { "id": "verdict", "title": "Verdict" } ] },
    { "file": "details.html", "title": "Details", "sections": [ { "id": "risks", "title": "Risks" } ] } ] }
```

- `pages`: required and non-empty. Each page has a relative `file` ending in `.html`, with no `..`, and its `sections`.
- A section `id` matches `^[A-Za-z][\w-]{0,63}$` and exists in that page as `id="…"`.
- `entry`: optional, the first page by default; it is the page the item links. `title`: optional; it labels the link, which otherwise reads the bundle's folder name.

**Pages.**

- Plain HTML. Pages link to each other by relative links and anchors (`details.html#risks`), which work inside the frame.
- No network load of any kind: no remote `src` / `srcset`, `<link href>`, CSS `url()` / `@import`, script `fetch` / `import` / `WebSocket`, and no forms. A plain `<a href>` to an outside page is a link, not a load, and opens a new tab; a code cite takes `graph-it`'s Cite form and opens in the owner's editor, because the frame keeps `allow-popups`. The served CSP blocks every load anyway.
- Scripts run sandboxed, with no access to the board, its cookie or token, the parent page or the network. `localStorage` and `sessionStorage` throw there, so wrap any use in try/catch.
- An optional "comment on this section" button may send exactly this message, and nothing else:

  ```js
  parent.postMessage({ type: 'sync-feedback', section: 'risks' }, '*');
  ```

  The wrapper then adds a draft comment for that section and focuses its note field. It lists every section anyway, so a page needs no script to get feedback. This message is all a lane's own script may send; quotes come only from the helper's selection script (Comments and selected text).
- The helper adds one script tag to every page it serves (Comments and selected text). Do not rely on it, and ship nothing under `__sync/`, which is never served from the bundle. Keep every section's text in the HTML itself: a quote is checked against the page file, so text a script writes at run time cannot be quoted.

**Publish.** `<edit script> bundle ID DIR` copies the folder to `reports/<sha8>-<name>/` (folders 700, files 600) and links the item to the entry page, labelled with the bundle title. It refuses a folder or manifest that breaks the rules above, naming the file, and an item that already links more than one bundle (one bundle per item). A refusal changes nothing: every check runs before anything is copied. It does not check pages against their HTML: an `entry` that names no listed page falls back to the first page, and a section id missing from its page is caught only by the checker (`MISSING SECTION`). Publishing again with changed content replaces the item's bundle in place, removing the old folder unless another item links it; the same content changes nothing.

**What the owner sees.** On the helper page the item's link opens the wrapper, `/r/<bundle>/<page>?item=ID`: the page list, the report in a sandboxed frame, and a **Comments panel** beside it (about 340 px; below the report on a narrow screen, with no sideways scroll at phone width):

- a header with the draft count, **Collapse all / Expand all** and **Hide panel** (the report takes the full width; a "Comments (N)" tab brings the panel back);
- every manifest section of every page, each with **+ comment**;
- draft cards: the target (page and section, which scrolls the report there or opens that page), the quoted text for a text comment, a note field (2000 characters) and remove; collapsed, a card is one line;
- **Submit all (N)**, then a greyed, collapsible **Sent** group: each batch with its time, comment count, "seen by …", and **retry** when a copy was not delivered.

A card comes from **+ comment**, from the page's own section button, or from selecting text in the report and pressing **Comment on selection: "…"**, which sits at the top of the panel, or on a narrow screen in a bar fixed to the bottom of the viewport while the selection is pending, so the owner reaches it without scrolling past the report. Drafts span pages and reloads, kept per viewer in the wrapper's own storage (item plus bundle), as are the collapse state and panel visibility; nothing else depends on them. **Submit all** sends every draft in one request with one click id: one message to each AI owner, one wake, one coordinator notice. An empty draft is refused by number and target, never dropped; a refusal keeps every draft and says why; on success the drafts move to Sent. A retry of the same drafts reuses the click id. The item then shows "feedback (N comments) · sending…", then "· sent HH:MM", then "seen by …". Feedback is a comment, not an answer: the item stays where it is and never enters the answered strip. A Done item's report stays readable, and its wrapper shows no panel. On the `file://` page the link opens the entry page directly, with no feedback.

**Comments and selected text.** A report page is an opaque origin, so the wrapper cannot read its selection. The helper therefore serves its own small script at `/b/<key>/<bundle>/__sync/select.js` (a helper file, never one from the bundle, under the report's CSP) and injects one `<script src>` tag for it before the last `</body>` of every bundle HTML page it serves. It carries nothing secret, and runs beside the page's own scripts, which can forge what it sends. Three messages:

- **`{type: 'sync-select', section, quote}`**, frame to wrapper: when a selection settles inside a section, the section it starts in, with the selected text whitespace-collapsed and cut to 300 characters; both fields empty when the selection clears. The wrapper shows **Comment on selection** for it, and the owner's click makes the card.
- **`{type: 'sync-mark', sections: [ids], marks: [{section, quote, n}]}`**, wrapper to frame: the manifest's section ids, so the script knows which ids are sections, and the drafts' quotes, which it highlights with the CSS Custom Highlight API and no change to the page's DOM beyond one `<style>` element.
- **`{type: 'sync-goto', section, quote}`**, wrapper to frame: scroll to that section, and to the quote when given.

Wrapper-to-frame messages use target origin `'*'`, since the frame's origin is opaque, and carry only section ids and quotes the page already shows, never the token or a note.

**Quote verification.** The helper refuses a comment whose quote does not occur in that page's file, read as the browser's HTML parser reads it:

- it removes comments and the `head`, `script`, `style`, `noscript`, `template`, `iframe`, `noembed` and `noframes` elements;
- it cuts tags in one linear pass with the tokenizer's grammar: `<` starts a tag only before a letter, `/`, `!` or `?`; a tag ends at the first `>` outside an attribute value quoted right after `=`, so `<y "z>` ends at its `>`; `<!`, `<?` and `</` before a non-letter end at the first `>`; a tag with no end swallows the rest of the file. A regex with nested or unbounded runs is not acceptable here: on a `>`-less tail it goes quadratic, and one comment blocks the helper for as long as the scan takes;
- it decodes entities with the full HTML5 named-character table, legacy names without `;` by their longest prefix, and numeric references with the parser's windows-1252 and U+FFFD rules;
- it removes all whitespace and folds case on both the page text and the quote, since a browser selection adds line breaks between blocks and may apply `text-transform`.

A match anywhere on the page is enough. So text hidden by CSS can be quoted, being in the file, and text a script writes at run time is refused, visibly, with the comment's number.

**The request.** One `POST /feedback` per submit:

```json
{ "cid": "<click id>", "id": "<item id>", "bundle": "<sha8>-<name>", "version": "<data-changed>",
  "comments": [ { "page": "summary.html", "section": "verdict", "note": "…" },
                { "page": "details.html", "section": "risks", "quote": "the selected words", "note": "…" } ] }
```

- 1 to 30 comments, each with exactly the keys `page`, `section`, `note` and an optional `quote`; the page and section from the bundle's manifest.
- A note of 1 to 2000 characters, control characters other than line breaks removed; a quote of at most 300 characters, whitespace collapsed.
- A body of at most 256 KB on this route, enough for the largest batch these caps allow (30 × 2300 characters at 3 bytes each, plus keys), so an over-limit comment is always named; every other POST keeps its own smaller cap.
- Over a limit: 400 naming the comment's number (413 for the body). An older single-comment body (`page`, `section`, `note` at top level) may be accepted as a batch of one.

**What the AI owner receives.** One message per submit, headed `<id>: feedback, N comments on <bundle title>`. The body is a numbered list: each comment's `<page>#<section>`, then `on "<quote>"` when it has one, then the note on indented lines, followed by the item version, the time, the click id, and the line that feedback is a comment, not a decision. The payload:

```json
{ "kind": "sync-feedback", "id": "<item id>", "bundle": "<bundle>", "version": "<data-changed>", "cid": "<click id>", "at": "<time>",
  "comments": [ { "page": "…", "section": "…", "quote": "…", "note": "…" } ] }
```

with `quote` only on a text comment. Then the wake; the coordinator gets a notice-only copy. Delivery, retry, resume and visible failure are the click path's (The helper).

**What the receiving agent does.** Feedback is a comment, not an answer, so it moves nothing by itself. Read every comment in the batch, each against its section and quote, and reply on the item: by its brief or next action, or by republishing the bundle with the change (Publish), which keeps the item's link in place.

**Checker flags** (`BUNDLE …`):

- `MISSING`: an item links a bundle folder that is not there.
- `NO MANIFEST`: a bundle without `bundle.json`.
- `BAD MANIFEST`: a manifest that breaks the rules above.
- `MISSING PAGE` / `MISSING SECTION`: listed in the manifest, absent from the folder or from the page's HTML.
- `REMOTE URL`: a remote load, as defined under Pages, in any `.html`, `.css`, `.js` or `.svg` file. Advisory for security, since the CSP is the control; like any flag it still fails the checker run.
- `MULTIPLE`: an item linking more than one bundle.

**Security requirements**, each proved by a mutation (SKILL.md, Clicks reach the AI owner):

- **Report serving**: at `/b/<key>/<bundle>/<path>`, with `sandbox allow-scripts allow-popups` and no `allow-same-origin`, `connect-src 'none'`, `form-action 'none'`, and `frame-ancestors` set to the helper's own origin, so only the wrapper can frame it. Only for a bundle some item links, only from inside that bundle's folder (real path, every symlink resolved), and only allowed types and regular files; every escape, raw or encoded, is a 404.
- **Per-bundle key**: `<key>` is an HMAC of the session secret and the bundle name. It stands in for the session cookie, which a sandboxed page's own subresource requests do not carry, since to the browser they are cross-site. It rotates when the helper stops and starts, and appears in no board URL and no log.
- **Wrapper**: needs the session cookie, like the board, and cannot itself be framed (`frame-ancestors 'none'`).
- **The two messages**: the wrapper acts on a message only when its source is its own report frame and its data is a plain object with exactly the keys of one shape: `type: 'sync-feedback'` and a string `section`, or `type: 'sync-select'` and strings `section` and `quote`. The section must be an own property of the manifest's section map, and a quote at most 300 characters; it ignores everything else. It renders every manifest string and every quote as text, and a quote travels in its own field, never in the note.
- **Injected script**: served only under its own `__sync/` path, never from the bundle (any other `__sync/` path is a 404); one tag per HTML page, none in other file types; no token, cookie or note in the script or the page.
- **Quote verification**: a quote that is not in the page's file is refused (400), whatever the client accepted; the client check is for the owner's sake, and this is the control. It refuses invisible text from malformed markup (`<y "z>`), an attribute value or an `iframe`'s content; it accepts text with named entities (`caf&eacute;`). It runs in time linear in the page: a 500 KB page with a `>`-less tail answers in well under a second, and the helper keeps answering throughout.
- **`POST /feedback`**: Host, Origin, token and cookie as for a click, and an idempotent click id; an open item that links that bundle; a page and section from that bundle's manifest for every comment; the comment count, the key shape, the note and quote caps and the 256 KB body cap, each refused on its own.
- **One batch, one send**: a replayed click id answers `duplicate` and sends nothing more; a delivery cut off mid-batch resumes as one message.

## The folder

```
<private dir>/sync/      700
  index.html             600   the record and the page
  README.md              600   the edit protocol: ADD, MOVE, CLOSE, ARCHIVE, with worked examples
  check.py               600
  assets/style.css       600
  assets/<diagram-lib>   600   vendored, version and checksum recorded in README.md
  backups/               700   dated copies taken before any restructure
  archive/               700   one page per month of archived Done items, same item markup
  <edit script>          600   optional: wraps the anchor tool for ADD / MOVE / CLOSE, themes, links, replies, options, decision context, `deprio` / `undeprio`, the auto level's `auto`, `route`, `category`, `ruling`, `decided` and `override`, and `lane`; `add` refuses an id already on the board, `links` merges into the links row, and `links --replace` prints each href it drops
  assets/<page script>   600   the page's script, kept out of index.html for the helper's CSP
  <helper>               600   the click helper (The helper)
  <bootstrap file>       600   the helper's current one-time URL; deleted on stop
  <session file>         600   session secret, page token and pending one-time URL, kept across reloads; deleted on stop
  <lifecycle script>     600   start / stop / status; its pidfile and log beside it, 600
  <routing file>         600   AI-owner name to mailbox address and optional terminal handle, the coordinator, the sender label
  inbox.jsonl            600   the helper's append-only event log
  reports/               700   the only folder the helper serves linked files and report bundles from
```

Back up `index.html` and the stylesheet before a restructure. The Done list is bounded by the **archive window** (default 14 days): a Done item older than that moves to `archive/<yyyy-mm>.html`, where its id stays taken.
