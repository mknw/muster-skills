# Board format

The reference half of [`sync-panel`](SKILL.md): the item and its decision context, decision pages, the theme, the auto level, the page, the panels, the checker, the helper, the Loose-ends buttons, grill me, steering notes, report bundles, the folder. Everything here is created once and then edited by anchor.

## The item

**The record has one format per era.** Through S8 the live record is `index.html`: one item is one `<li class="item">` carrying its data as attributes, with the human text inside. At the **S9 cutover** `board.json` replaces it as the record — same items, same fields, one JSON object per item instead of one `<li>` — and from then on `index.html` is a page the renderer writes from the record, never the record itself. The JSON back end is built and proved on scratch copies through S1–S8 (the migration converts, the round trip renders back and compares); the same edit commands flip stores when `board.json` lands beside the board, so no agent changes how it works. The checker runs on either record: the same flags, on fields instead of attributes.

The JSON record's item is the attribute table below with the `data-` prefix dropped; a field the HTML record leaves absent is `null`. The space-separated multi-values (`rel`, `ai-owner`, `category`, `auto-category`) become arrays; the body lines become fields (`title`, `next`, `brief`, `auto-note` plain strings; `terms` and `links` arrays of `{term, meaning, href}` and `{href, note}`); the level is the per-project `levels` map (Auto level). The record's root carries `{schema, levels, themes, items, checked}`; Done items past the archive window live in `archive/<yyyy-mm>.json`, one file per month, ids taken exactly as on the archive pages. The field list is the edit tool's `ITEM_FIELDS` — one declaration, both stores, the migration and the renderer included.

Attributes are the record; the page's script derives everything else and writes none of them. Agents change attributes only through the edit tool's anchored edits, never by reading the file and writing it back.

```html
<li class="item" data-id="L5" data-project="…" data-section="loose-ends" data-actor="owner" data-since="2026-10-28" data-changed="2026-10-28T17:17:00Z" data-rel="after:N1">
  <h3><a href="https://host/owner/repo/pull/845">Title as the owner would read it</a></h3>
  <p class="next"><b>owner</b> the one next action, after #845 and #851</p>
  <p class="links"><a href="https://host/owner/repo/pull/851">851</a> <a href="https://host/owner/repo/issues/840">840</a></p>
</li>
```

| attribute | meaning |
|---|---|
| `data-id` | stable, never reused. Prefix by first state (N / R / L / D); the edit tool assigns the next free number inside the same locked edit that inserts the item, so an agent never reads it and writes it in a later step |
| `data-project` | required on every item, Done included: a name from the routing file's `projects` list; set with the edit script's `project ID NAME` or `add ... --project NAME`; moves and closes carry it (Projects) |
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
| `data-lane` | required on Running: who works the item, `term:<handle>`, `herdr:<pane-id>`, `via:<AGENT>` or `none`, written by the dispatcher with the edit script's `lane`; a move out of Running or a close drops it (Steering notes) |
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

## Projects

Use one board for all of the owner's projects. Every item carries `data-project`; the page renders it as text beside the title. The routing file's `projects` list declares the names, and `project_agents[project]` holds that project's `agents` map and `coordinator` name. A role name may resolve to a different address in each project. Configure `default_project` explicitly for board-wide level changes and for `add` when its project is omitted; a single declared project may be inferred on `add`, while an ambiguous choice is refused. The project filter is optional; the item label is required.

Resolve an item click through that item's project before sending. Its owner copies and notice use only that project's map and coordinator. An agent name outside that map falls back to that project's coordinator, even if another project's map contains the name; deduplicate those fallback owner copies and skip a duplicate notice. Apply this to answers, report feedback, grill, loose-end actions, override and `via:` steering. A direct worker lane still uses its recorded handle/pane, with the owner-facing guard checked against every configured agent pane. A missing or unknown project refuses new delivery. Persist the project with the click so retry/reload finishes the original delivery if the item is later re-tagged.

The edit script's `project ID NAME` validates the declared name before its locked edit. `add ... --project NAME` sets it at creation; move and close retain it. The checker flags `NO PROJECT` for a missing field and `BAD PROJECT` for an undeclared name. At migration, list current open items and propose each one's project for coordinator confirmation; the author works on a scratch copy. An older flat routing map may define the explicitly chosen default during migration, and unscoped historical deliveries belong to that default only. New server configuration should provide every project map explicitly. A Herdr-only deployment needs no Orca executable; retain the Orca adapter for deployments that still use it.

Done when the new flags are planted then fixed, same-named roles in different projects reach different fixture recipients, unknown names reach only their project's coordinator, notices stay in scope, and replay/resume retains the recorded project.

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

The board's **level** is per project (L109): one level line per project the routing file declares, written only by the edit script's `auto LEVEL CID [--project P]` (the line with no `data-project` is the default project's; the default project's line keeps the pre-L109 readable text, no suffix, every other project's names its project):

```html
<div id="auto" data-project="security-tooling" data-level="security" data-changed="2026-11-04T16:00:00Z" data-source="click:<click id>"><b>auto (security-tooling): security</b> — you keep security, changes to your rulings, irreversible actions</div>
```

On the JSON record (S9) the level is the record root's `levels` map, one entry per declared project, each `{level, changed, source, quote}`; a legacy single `auto` object converts with `auto --convert`, the owner's line kept verbatim. A click, `route` and `decided` all resolve the item's own project, and an unknown project reads as off.

**One reading.** The edit script and the helper read a project's level only from its one line, at the start of its own line and outside a comment, its attributes first-wins, and only while the file's tags, commented-out ones included, carry `id="auto"` for that project exactly once. Text that mentions the line, such as a brief about it, is not a tag and does not count, and neither does an attribute value that mentions it; a quoted value may hold `>`, and an id counts as the browser decodes it. Anything else reads as `off`, so a commented-out old line, a duplicate or a reordered attribute fails safe in every runtime. The checker reads the line both as the page does and as the edit script does, and flags `BAD AUTO LEVEL` when the two disagree; `auto` refuses to write until the line is one again. On the JSON record the field is the one reading by construction: the checker flags the map against the routing file and the ladder (`NO AUTO LEVEL` for a project without its entry, `BAD AUTO LEVEL` for a level the ladder does not name, `BAD AUTO PROJECT` for an undeclared project's entry).

**One rules file.** The table is the whole rule, and it lives in `rules.json` beside the board (S2): the ladder (`auto.levels` / `auto.categories` / `auto.keeps`, monotone — each level keeps a superset of the next), the action-kind rule, and the transport/lane rules (`transport.transports`, `transport.herdr-id`, the lane patterns). The edit tool, the checker, the helper and the page all LOAD the same file; no runtime holds a table of its own, and a runtime that stops loading the file is the defect — every consumer fails loudly (the edit tool refuses every op, the helper refuses to start, the page shows its failure, the checker flags it). `rules.json` is a shared contract with the app side, change-controlled with both owners; the migration writes it beside `board.json` at conversion.

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
2. **Auto level**: the five-stop slider (The auto level). **Band**: the Themes panel across the top while any theme is open, then the panels (next section), each with a one-line heading that names the question it answers.
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
| who works where, on what model? | the agent-tree panel: the VM level, then the container level (docker, incus), then each routed project's worktrees, then the live agents nested under the worktree their cwd sits in (runtime · model · the Running item id it works, `task`), drawn as a tree; every level reads a live source, and an unreadable one shows as an absent line with a fixed reason, never as an empty level and never with the source's own error text | containment is nesting, which a tree shows without decoding; a box diagram would imply flow between the levels, and there is none; the live sources are `systemd-detect-virt` (VM), `docker ps` / `incus list` where the CLI exists and the serving user may use it, `git worktree list --porcelain` per routed project at the conventional `~/Code/<project>` probed for existence, `agent.list` over the helper's own herdr socket, and each runtime's own settings for the model (unreadable is `unknown`, never scraped from pane output); the task shorthand joins a Running item's `data-lane` to the live pane (`herdr:<pane>` directly, `via:<AGENT>` through that agent's route), and an agent no Running item names shows without a task id |

An inbound verb (`after`, `needs`, `blocked-by`, `waits`) is rendered reversed and relabelled (`before`, `needed by`, `blocks`, `awaited by`), so the graph keeps FORMS.md's arrow direction; `see` is drawn as a line with no arrowhead, and as an open circle in the matrix.

## The checker

`check.py`, standard library only, no network, reports and never moves an item. One checker, two records (S2's successor): a `board.json` beside the board (or named by `--index`) engages the JSON record — the same CLI, the same output discipline, the same flags, one flag per line with the id — and its absence keeps the HTML record this section always described. Through S8 the HTML checker is the deployed authority; the JSON mode is proved on scratch copies and lands at S9 with the migration. The HTML mode parses `index.html` with the HTML parser, collecting every element with `data-id` (and every theme with `data-gid`), the `<section id>` enclosing it, its title text, its next-action text, its links, and its brief, terms and link notes; a void tag such as `<br>` closes itself. The JSON mode reads `board.json` first-wins on duplicate keys, and every `archive/*.json` month. The two modes share one flag implementation, so a defect earns the same flag on either record.

**The JSON forms of the HTML-specific flags.** `DUPLICATE ATTRIBUTE` becomes duplicate JSON keys, refused at parse, first value read; `SECTION MISMATCH` becomes the section field's own value (in JSON the field *is* the placement — an item outside the four sections, or an archive month holding a non-Done item, is the flag); `GROUP MISPLACED` retires with the placement it policed (the themes array is the record's one placement; the migration refuses the HTML shape). New, JSON-only: `BAD SCHEMA` (a record that is not the schema's own shape, refused loudly rather than a silent HTML fall-back) and `UNKNOWN FIELD` (an item, theme, level entry or root key the merged schema has no field for — fix it by hand).

Flags, one line each with the id (and the line number where the parser has one):

- `NO PROJECT` / `BAD PROJECT`: an item has no `data-project`, or its name is absent from the routing file's `projects` list (Projects).
- `DUPLICATE id`: the same `data-id` twice, counting the archive pages (whose ids also count as existing for `BAD REL`)
- `SECTION MISMATCH`: `data-section` differs from the enclosing section (on the JSON record: a section value outside the four, or an archive month holding a non-Done item)
- `BAD data-changed` / `BAD data-due`: unparsable
- `OVERDUE`: `data-due` passed
- `NO NEXT ACTION`: a Needs-you item with no next action, or one that only names the actor
- `NO CHECK`: a Running item without `data-due` or without `data-check`
- `UNLINKED REF`: a `#NNN` in an open item's title or next action that no link in the item points at (`/pull/NNN` or `/issues/NNN`); Done items are exempt
- `BAD REL`: a `data-rel` entry that is not `verb:ID` with a known verb and an existing id
- `LONG NEXT`: an open owner row whose next action is longer than 15 words
- `BAD OPTIONS`: `data-options` that does not parse as `LABEL text|…`, or a `data-recommend` that is not one of its labels
- `BAD ACTIONS`: a `data-actions` entry that would show no working button. Valid is `Label=kind` with a non-empty label and a kind of one lower-case letter then up to 40 word characters, `:`, `.` or `-`
- `ACTIONS RULE DRIFT`: the action-kind rule no longer loads, or a runtime stopped loading `rules.json` or declared its own rule again (the load checks below)
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
- `DUPLICATE ATTRIBUTE`: an attribute an item carries twice; the browser and the helper read only the first. On the JSON record: duplicate JSON keys, refused at parse, the first value read
- `NO AUTO LEVEL` / `BAD AUTO LEVEL`: no level line for a declared project (it reads as off); a level outside the ladder, two level lines for one project, `id="auto"` in the text more often than the page sees it, or the page and the edit script reading different levels. On the JSON record: a project without its `levels` entry; an entry whose level the ladder does not name, or a record still carrying the pre-L109 single auto object (convert it)
- `NO CATEGORY` / `BAD CATEGORY` / `NO RULING CITE`: a Needs-you item without `data-category`; a category outside the list on any item, or `other` beside another; `changes-ruling` without `data-ruling`
- `BAD AUTO`: a stamp that is not `AGENT LEVEL OPTION` with a level from the table, whose option is not one of the item's, or without `data-auto-category`
- `AUTO MISMATCH`: a stamp whose level keeps one of the item's categories for the owner, or an unknown one, an item with none, or categories that differ from the recorded ones: as far as the file can tell, the decision was not the coordinator's to take
- `AUTO IN NEEDS YOU` / `AUTO NO NOTE`: a stamped item in Needs you; a stamp without its note
- `AUTO RULE DRIFT`: the ladder in `rules.json` missing, not monotone, or no longer loaded by every runtime; the load checks below
- `NO LANE` / `BAD LANE`: a Running item without `data-lane`; a lane outside the four forms, a `via:` agent the routing file does not name, a `term:` handle that is one of the routing file's terminals (an owner-facing one, recorded as `via:` instead), or a lane outside Running
- `UNKNOWN TRANSPORT` / `BAD AGENT ID`: an agent route selects a transport other than `orca` or `herdr`, or a Herdr address is malformed. Missing transport means Orca.
- `TRANSPORT RULE DRIFT`: the transport/lane rules in `rules.json` missing or no longer loaded by every runtime, checked like the auto table.
- `STALE`: `data-changed` older than three days on an open item

Then one report line per `data-check` (`CHECK <id>`: DONE when it exits 0, OVERDUE when it fails past `due`, else pending, and whether it ran without a shell or through `sh -c`; a command with no shell metacharacter runs without one, under a timeout either way); then the lane-deadline ledger the coordinator keeps, whose overdue lines also count as flags; then the counts per state. Exit 1 on any flag.

**The load checks** (S2): `AUTO` / `ACTIONS` / `TRANSPORT RULE DRIFT` fire when `rules.json` beside the board does not load — missing, not valid JSON, not the schema:1 rules record, or a ladder that is not one monotone set per level — or when a consumer's source stops loading it or declares its table again; the file is all-or-nothing, so a load failure flags all three, each naming why, and the checker fails closed: it never reports a clean board whose rules it could not read. The per-consumer proof is by mutation: remove the load from the edit tool, the helper, the page or the checker and that consumer fails visibly (the mutation run's four red-then-green plants).

`--stamp` rewrites the last-checked line through the same anchor tool used for items, falling back to a direct write; on the JSON record it writes the record root's `checked` field instead (the header's stamp has a record home), as one locked, schema-validated, atomic write. The mutation run that proves the checker: a scratch copy with one planted instance of every defect, all flagged, exit 1 — the full flag set on both records.

## The helper

Select the delivery adapter using [Runtime delivery](SKILL.md#runtime-delivery) before implementing mailbox delivery.

A local server with no dependency beyond its runtime, started and stopped by hand through a lifecycle script (`start`, `stop`, `status`), never as a login item. It serves the board folder at `http://localhost:PORT/` (also accepting `127.0.0.1:PORT`), so the board opens there with none of `file://`'s limits, and adds `POST /click`, `POST /retry`, `POST /feedback` (Report bundles), `POST /level` (The auto level), `POST /steer` (Steering notes) and `GET /state` (fetched at each page load). It never writes the board file: its writes are appends to the inbox, the one-time bootstrap file (rewritten on each use) and the session file.

- **Self-reload**: the process the lifecycle script starts is a supervisor that runs the helper as a worker child and watches the helper's code file. When the file changes and passes a syntax check, it swaps the worker; a broken edit is logged and the running worker stays. The session secret, the page token and the pending one-time URL persist in a mode-600 session file, written atomically, so the owner's cookie and open page survive a reload; `start` writes fresh secrets and `stop` deletes them. The supervisor's own code is not reloaded. The page retries a send that gets no HTTP answer, a few times, with the same click id, which covers the moment a reload takes.

- **Routing file**: each AI-owner name to its mailbox address and, for the wake, an optional terminal handle (an address that is itself a terminal handle serves), plus the coordinator's name and the helper's own sender label. The helper sends under that neutral label and starts with a clean environment, so it never acts as the agent that launched it.
- **Inbox**: one JSON event per line, append-only: `click` (an answer, or feedback on a report section), `sent` (with the mailbox message id), `send-failed` (with the error), `retry`, `seen`, `woken`, `wake-failed` (with the reason).
- **Wake**: after each delivered owner copy, never the coordinator's notice, the helper types one fixed line into that agent's terminal through the mailbox system, telling it to check its mailbox. One attempt per copy; a failed or skipped wake (no terminal handle, or one that fails validation) is recorded as `wake-failed` and leaves the click sent.
- **States**, in the expanded item and as a short badge in row view:
  - sending: until a copy is confirmed, never shown as sent;
  - sent: the answer and its time, with "agent not woken" after a `wake-failed`, and "unread 30+ min" in the warning colour once a copy has stayed unread that long;
  - seen: by whom and when, from the selected adapter's verified read receipt or message-ID acknowledgement, where supported, which the helper polls while a sent message is unread; it means handed to the agent, and says nothing about acting;
  - not delivered: to whom, with a **retry** button;
  - answered an older version: the click's version differs from the item's `data-changed` at the moment of the click;
  - resolved: the item left Needs you, or was edited after the answer.
- **Note**: a text field on the expanded item, at most 500 characters, kept across the refresh, sent with whichever button is pressed.
- **Default Done**: a Needs-you item that declares no reply, options or actions gets one **Done** button with the note field, so a task the owner performs can be answered, with any detail in the note. The helper accepts `Done` only for such an item. It announces its features in the page it serves, and the page offers a feature only when announced, so a page newer than its helper never sends what the helper would refuse.
- **Linked files**: a page served over http cannot open `file://`, so the helper serves the non-text local files the board links, from one `reports/` folder; the edit script copies a linked non-text file there and links the copy, a snapshot, refusing a symlink, a non-regular file and anything on a hidden path. Text files open in the editor either way.
- **No silent copy**: on the helper page a refused send shows "not sent: <reason>" in the danger colour, opens the item and keeps the note, and copies nothing. Only on the `file://` page, or when the helper does not answer at all, does a click copy `<id>: <answer>` and the note to the clipboard, and the item then says "helper offline: copied, paste it to the agent". The `file://` page carries a banner saying clicks are not sent from it, with a link to the helper page.

**Security baseline**, each requirement proved by a mutation (SKILL.md, Clicks reach the AI owner):

- **Loopback only**: bound to 127.0.0.1, and every request's `Host` is exactly `127.0.0.1:PORT` or `localhost:PORT`, against DNS rebinding.
- **Session cookie**: every route but a health check and the bootstrap needs it; it is `HttpOnly; SameSite=Strict` and set only by a one-time bootstrap URL, which the helper keeps in a mode-600 file and rotates on each use, and the lifecycle script prints.
- **Per-start token and Origin**: a random token, rotated at each start, held only in the mode-600 session file beside the session secret and the pending one-time URL (never in the board file, a URL or a log) and injected into the page the helper serves; required on every POST and on `/state`. Every POST also carries an `Origin` exactly `http://127.0.0.1:PORT` or `http://localhost:PORT`; every other hostname, scheme and port is refused.
- **Input**: an open item's id, of plain letters, digits and dashes at most 24 long on every click (an id reaches message bodies, so any other id is refused), an answer that item declares (reply, option or action, or `Done` when it declares none, or one of the four Loose-ends answers when it sits in Loose ends, or `grill` when it sits in Needs you, or only `override` when it carries `data-auto`, the one answer a Done item takes), a Running item with a `term:`, `herdr:` or `via:` lane on `POST /steer`, a level from the table on `POST /level`, a note within its cap, a body within a size cap, JSON only.
- **Owner list**: the helper reads `data-ai-owner` once per name, keeping each name's first position, and refuses a list of more than eight distinct names (400, naming the count), for answers, report feedback and grill me alike, so a board edit cannot fan one click into a send per listed name.
- **File serving**: a file is served only when the board links it, its real path (every symlink resolved) lies inside the reports folder, and it is a regular file; a served file gets a sandbox CSP so it cannot act as the board. The hidden-path refusal sits in the edit script's copy step (Linked files).
- **Strict CSP on the board**: `script-src 'self'` with no inline script, `frame-ancestors 'none'`, `X-Frame-Options: DENY`.
- **First-wins attributes**: an attribute an item carries twice is read first-wins, as the browser reads it, so an item can never render with one section or actor and route by another; the checker flags the duplicate.
- **Argv-only process calls**: every mailbox and terminal call is an argument array; request content reaches no shell. The wake's terminal handle must match the mailbox system's plain handle shape, and the item id it types must be plain letters, digits and dashes.
- **Idempotent clicks**: each decision carries a client id that a double click or a retry reuses, and the helper records and sends a known id once. An id already used for an answer is refused for feedback, and the reverse (400). Each mailbox send carries a deterministic request id, so an ambiguous retry is replayed rather than duplicated.
- **Delivery resume**: a delivery cut off by a reload (a click recorded, no `sent` or `send-failed` for a recipient) is re-delivered by the new worker at boot and when the page replays that click id, to the recipients recorded with the click when it was made, never to names the routing file gained since; the same request id makes the mailbox replay a copy that did go out instead of sending it twice. Resume only finishes recorded clicks and constructs none. A copy recorded as sent whose wake has no outcome gets that wake, once, at boot, on a replay and on retry, under the same deterministic request id, and the mailbox copy is not sent again for it.
- **Visible delivery failure**: every send ends as `sent` or `send-failed`, in the inbox and on the page; a malformed mailbox reply is logged and keeps the helper running, and the receipt poll runs at most once every few seconds however often `/state` is fetched.
- **Lifecycle identity**: `stop` kills only a process whose command line is the runtime running this helper, so a recycled PID survives. The worker exits when its supervisor is gone, deleting the secret files only while they still hold its own. `start`, `stop` and `status` never trust the pidfile alone: each also checks whether the port answers, and none reports success while another process holds it.
- **Known residual**: cookies are host-only but not port-scoped, so the browser also sends the session cookie to another server on the same loopback hostname the owner opens; `HttpOnly` keeps page scripts from it, but that server could log it. The cookie stays valid across reloads for as long as the supervisor runs; only stop then start rotates it.

### SSH local forward

Keep the helper bound to `127.0.0.1` on the server. From the owner's machine, run:

```sh
ssh -N -L <port>:127.0.0.1:<port> <user>@<host>
```

Open the printed one-time bootstrap URL at `http://localhost:<port>/bootstrap?...`, then use `http://localhost:<port>/`. The bootstrap file and lifecycle output name localhost; the same one-time path also works through the numeric loopback alias. Cookies stay host-only, HttpOnly and SameSite=Strict: open the bootstrap using the hostname you will use for the board. Keep the per-start POST token, exact Host/Origin allowlists and one-time rotation; forwarding adds no password or public listener. Report frames allow exactly the two HTTP loopback origins at that port, while the board and wrapper remain unframeable. Prove both authorities through a TCP relay and refuse suffix hostnames, foreign origins and different ports; reverting to a single authority must make the localhost proof fail.

### Transports

Select `"transport": "orca"` or `"transport": "herdr"` per agent in the routing file. An absent field means Orca; an unknown value fails visibly without falling back. Keep the current routes until the owner authorizes a cutover. The helper owns one adapter interface: send to mailbox, wake or pointer, read inbox. Every click kind and every recipient uses it, including coordinator notices and `via:` lanes.

For Orca, retain the existing mailbox calls, fixed terminal pointer, clean process environment, deterministic retry IDs and read receipts. For Herdr, read the installed export from `herdr api schema --json` and the runtime guidance in [dispatching-work](../dispatching-work/herdr-native.md) before implementing the adapter. Configure an explicit Unix socket for the intended session; use newline-delimited JSON requests with matching response IDs. Ambient pane selection and a fallback server can misroute an owner's words.

Use `"to": "herdr:w1:p2"` for a Herdr route and `data-lane="herdr:w1:p2"` for a lane: these are pane IDs, accepted as agent-prompt targets, rather than agent-name aliases that end when an agent exits. Validate the qualified pane shape, `^w[0-9A-Za-z]+:p[0-9A-Za-z]+$`, before writing a mailbox or calling the socket: this server's herdr issues lettered workspace ids (observed `wC`, `wM`; a fresh `workspace.create` returned `wN:p1`), and the exported schema states no pane-id alphabet (`pane_id` is a free string), so the numeric-only shape stays accepted as a subset. Capture real IDs from creation responses; update a lane after moving or replacing its pane. Any pane named by an agent route is owner-facing for steering and uses `via:` instead, checked again at delivery and immediately before the pointer.

Herdr's native API provides no durable mailbox, idempotent send or read receipt. Supply a helper-owned file mailbox accessible to the recipient: one private JSON file per deterministic delivery ID, atomically published once, containing the sender, subject, body and payload. An agent reads it with its own file tool; `via:` recipients forward its body. The typed line contains only a fixed instruction and a validated mailbox path, never note text. Submit the fixed pointer through `agent.prompt` with `{target: <pane-id>, text: <fixed pointer>}` only after reconciling the live target as an exclusively assigned worker ready for input: ready for input means `idle` or `done` (herdr's own contract — "`idle` and `done` normally indicate the agent is ready for input"). Durably queue the pointer in the adapter while busy, blocked or unknown; reconcile readiness before submission. A queued pointer is reconciled by the helper itself on a timer, not only while the board is viewed, and a definitively undeliverable pointer is recorded as failed (visible), never silently pending. A send receipt confirms the file exists, and a prompt receipt confirms submission.

For Herdr, record `seen` only after the recipient explicitly acknowledges that delivery ID through the adapter. Until then, show read status unknown; when no acknowledgement channel exists, mark it not supported. Prompt success, lifecycle state and the recipient's local processed-ID record are not acknowledgements. `pane.read`, focus/Done badges and event subscriptions are not read receipts.

Verify durable publication and replay against the selected transport's documented guarantees before enabling delivery. Unsupported read acknowledgements use the unknown state above; Herdr prompt submission uses the weaker guarantee in Prompt recovery. If required durable delivery/replay cannot be provided, show delivery unavailable and preserve the note. Apply The helper's No silent copy rule: an online refusal preserves the note and copies nothing; clipboard fallback is for offline/no-response operation.

### Receiving file deliveries

Before dispatch, put the private `mailbox_root`, the agent's `recipient_directory` relative to that root, and its private local `processed_delivery_ids` file in the receiving agent's runtime instructions. Bind the actual per-recipient location the helper publishes to; an agent receiving a coordinator notice or a `via:` copy gets no pointer from which to discover it. Admit filesystem access for the receiving agent before routing a copy there. Mailbox directories are mode 700 and files mode 600: this is a same-user access boundary, not isolation between panes sharing that user.

1. On each next turn, list `*.json` files in the bound `mailbox_root/recipient_directory`, before starting other work. This includes copies delivered without a wake.
2. Skip delivery ids already in the bound `processed_delivery_ids` record; use each immutable filename's delivery id, not a timestamp or directory position.
3. Read the subject, body and payload of each remaining copy. Handle a coordinator notice as notice-only; forward a `via:` body word for word with the agent's own tool, then take it into the current work as appropriate.
4. After successful handling, record that delivery id in `processed_delivery_ids` locally, retaining previous ids across turns. Keep the local record private (directory 700, file 600) and the helper mailbox files immutable. The local processed-ID record does not acknowledge the message through the adapter (Transports).

Done when a fresh recipient with only this procedure and its runtime binding handles a no-wake copy once, then finds a later copy on its next turn without handling the first again. Prove the procedure with a scripted recipient when no live model is available, and state that limit; removing the discovery/next-turn instruction must make that eval fail.

### Prompt recovery

Herdr request IDs correlate responses; they do not promise idempotency. Persist and flush a prompt-start record before calling it. On reload, a start without an outcome becomes a visible unknown wake failure, with no automatic replay. This gives one durable mailbox copy and at most one prompt attempt, with possible lost attention in the crash window. Reconcile the pane and file before a manual intervention. Orca keeps exactly-once replay through its runtime retry IDs. These transport-specific guarantees qualify the generic resume requirements above.

Prove the adapter against the exported request and response schemas with a fixture that does not invent native mailbox or deduplication calls. Run the full click matrix with mixed routes, default-Orca regressions with the transport field absent, checker defects planted then fixed, and source mutations for route selection, unsafe IDs, owner-facing panes and reload recovery. Keep a separate live proof that creates, addresses, reads and closes only its own throwaway pane. Verify Linux lifecycle and reload too. A loopback helper works over an SSH local forward when the browser retains its exact loopback Host and Origin, bootstrap URL and cookie; leave the binding and authentication checks in place.

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
| grill me | `grill` | each AI owner resolved within the item's project; an unlisted name falls back to that project's coordinator | yes |

- **Where it is accepted**: the helper accepts `grill` only for an item whose `data-section` is `needs-you`, and refuses it on any other item (400, naming the item's section). `grill` is the board's own answer: a declared reply of that name sends the grill request on a Needs-you item and is refused elsewhere.
- **Recipients**: the item's `data-ai-owner` names, read as the security baseline's Owner list says (The helper), resolved within its project (Projects). An unlisted name falls back to that project's coordinator. The coordinator gets the usual notice-only copy, skipped when it is a recipient.
- **A request, not an answer**: the item keeps its place and its count, never enters the answered strip, and keeps its chips or the default Done, because the decision is still the owner's. The request has its own line beside any answer's, "grilling round requested HH:MM · seen by <agent>", with sending, agent not woken, requested on an older version, and not delivered with **retry**, as for answers; row view shows a short badge beside the age.
- **Cleared**: once an owner copy is seen and the item's `data-changed` is later than the click, the line and the badge go, and the item's changed-since-you-looked dot shows the new content. Both halves count: the seen copy is the adapter's receipt/acknowledgement record, which a board edit cannot write.
- **Older helper**: the helper announces `needs-you-grill` among its features. On a helper without it, the button is disabled with a visible "helper too old" note, and nothing is copied to the clipboard. Offline it copies `<id>: grill` like every button (The helper, No silent copy).

**The grilling round** is what the receiving agent does on `grill`, within its next turn:
1. Run the `grilling` skill on the item's decision yourself. Answer every question the code, records or docs answer, and continue from the owner's prior rulings rather than re-asking them. The skill's wait for the user does not apply: you play both roles, and what neither you nor the records settle becomes the page's questions.
2. Deliver or refresh the item's decision page (Decision pages): the questions first, plain, each with its recommendation, what it blocks and its continuity; then each explained; then the material. Proportionate to the decision.
3. Set `data-complexity` to medium or higher and link the page as the item's title.
4. Rewrite the brief and options to the questions that remain, and reply on the item.
5. Leave the item in Needs you. When the round leaves nothing for the owner to decide, say so in the brief and recommend Done, then set complexity low and drop the link: this overrides step 3.

## Steering notes

The owner can steer the agent working a Running item while it works. Every expanded Running item carries an **include feedback** box: a line saying where the note goes, a text field of 2000 characters kept across the refresh, and a send button.

**The lane** is `data-lane`, written by the dispatcher when it dispatches the work, in one of four forms:

| `data-lane` | who works the item | where a note goes | wake |
|---|---|---|---|
| `term:<handle>` | an agent with a terminal of its own, by the runtime's handle | a mailbox message to that handle | one fixed pointer typed into its terminal |
| `herdr:<pane-id>` | a Herdr pane running an agent | the helper-owned file mailbox | one fixed pointer, queued until readiness is reconciled |
| `via:<AGENT>` | an agent with no terminal of its own (a subagent), or any owner-facing agent; AGENT is a routing-file name | AGENT's mailbox | none: AGENT forwards the note with its own tool |
| `none` | nobody, for now (waiting on CI, a merge, the owner) | nowhere: the box is disabled and says why | — |

A terminal the routing file names belongs to an owner-facing agent, so the dispatcher records that lane as `via:<AGENT>`, and a steering note never types into it. The helper reads the routing file afresh before each send, a retry or a resume included, and refuses the send when the lane has become owner-facing; it reads it again right before the pointer and then always withholds the pointer, though a mailbox message already in flight may still arrive. Either way the item shows the reason as text, asking for the lane to be recorded as `via:<AGENT>`. The edit script's `lane ID VALUE` writes the attribute on a Running item only, checking the form; a move into Running keeps it, a move out of Running and a close drop it.

**The answer**: `POST /steer` with `{cid, id, version, note}`, under the cookie, token, Origin, click-id and version rules of every click. The helper accepts it only for a Running item whose lane is `term:`, `herdr:` or `via:` (400 otherwise, naming why), with a note of 1 to 2000 characters, control characters other than line breaks removed.

**Delivery** keeps the note's text in the mailbox body, indented, and out of every terminal:

- `term:` — one message to the handle, then the pointer: `You have sync-board a steering note on <id> from the owner: run <mailbox check>.`, as an argument array. For the verified Orca `term:` behavior, an idle agent takes the pointer as a prompt and reads its mailbox at once; a busy one takes it as its next prompt, after its current step. A handle outside the runtime's plain shape is recorded `send-failed` and `wake-failed`, with nothing run.
- `via:` — one message to AGENT's address, asking it to forward the note word for word to the lane it runs.
- The coordinator gets the usual notice-only copy, skipped when it is the `via:` agent.

The pointer follows the selected transport's wake policy and creates no orchestration assignment.

**On the page**, under the box, every note sent on the item, newest first, read from the inbox, the earlier ones past the newest five behind one toggle: its time, its text, and its state (sending, sent to the handle or agent, woken or not woken, seen once the mailbox marks it read, not delivered with retry, and "sent on an older version" when the page was older than the item). The latest note's state is a short badge beside the age. The helper announces `steer-notes` among its features; the `file://` page copies `<id>: steering note: <text>` and says so. The notes are the board's record of what was said: they live in the inbox, and the board file stays as the edit script leaves it.

**What the receiving agent does**: reads its mailbox, takes the note into its current work with the owner's words governing, and acks it when the transport supports receipts; the page shows seen only from that receipt (Transports). A `via:` agent forwards the note word for word to the lane it runs, then carries on.

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

- **Report serving**: at `/b/<key>/<bundle>/<path>`, with `sandbox allow-scripts allow-popups` and no `allow-same-origin`, `connect-src 'none'`, `form-action 'none'`, and `frame-ancestors` set to the helper's two allowed loopback origins, so only the wrapper can frame it. Only for a bundle some item links, only from inside that bundle's folder (real path, every symlink resolved), and only allowed types and regular files; every escape, raw or encoded, is a 404.
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
  index.html             600   the record and the page through S8; at S9 a page the renderer writes from board.json
  board.json             600   the record at S9 (schema:1; absent through S8 — its presence flips every runtime to the JSON store)
  rules.json             600   THE rules file (S2): the auto-level ladder, the action-kind rule, the transport/lane patterns — one reading, loaded by the edit tool, the checker, the helper and the page; change-controlled with both owners
  README.md              600   the edit protocol: ADD, MOVE, CLOSE, ARCHIVE, with worked examples
  check.py               600   the checker: the HTML record through S8, the JSON record at S9, the same flags
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

Back up `index.html` and the stylesheet before a restructure. The Done list is bounded by the **archive window** (default 14 days): a Done item older than that moves to `archive/<yyyy-mm>.html` (at S9, `archive/<yyyy-mm>.json`), where its id stays taken.

**The S9 landing order** (one cutover window, owner-approved; through S8 nothing here touches the live board): dated backups of `index.html`, the archive pages and the stylesheet into `backups/`; the migration converts the HTML record to `board.json` + `archive/*.json` on a scratch copy first, writing `rules.json` beside it, and the round-trip proof renders the HTML back and compares; the successor checker reports the same flags on the migrated record; the new runtimes and `rules.json` land in the folder together with `board.json` — one unit, so no consumer runs without the one rules file; the app takes the port and prints a fresh one-time URL. Rollback restores the backups, and the renderer converts any JSON-era edits back.
