# Board format

The reference half of [`syncing-board`](SKILL.md): the item, the theme, the page, the panels, the checker, the folder. Everything here is created once and then edited by anchor.

## The item

One item is one `<li class="item">` carrying its data as attributes, with the human text inside. Attributes are the record; the page's script derives everything else and writes none of them.

```html
<li class="item" data-id="L5" data-section="loose-ends" data-actor="owner" data-since="2026-10-28" data-changed="2026-10-28T17:17:00Z" data-rel="after:N1">
  <h3><a href="https://host/owner/repo/pull/845">Title as the owner would read it</a></h3>
  <p class="next"><b>owner</b> the one next action, after #845 and #851</p>
  <p class="links"><a href="https://host/owner/repo/pull/851">851</a> <a href="https://host/owner/repo/issues/840">840</a></p>
</li>
```

| attribute | meaning |
|---|---|
| `data-id` | stable, never reused. Prefix by first state (N / R / L / D) and the next free number |
| `data-section` | `needs-you` / `running` / `loose-ends` / `done`; must equal the `<section id>` it sits in |
| `data-actor` | who moves next: the owner, the coordinator, a named agent role, `lane`; `none` on Done |
| `data-since` | date the item first existed; kept on a move |
| `data-changed` | ISO UTC time of the last edit; stamped on every edit; the "changed" cell reads it |
| `data-due` | required on Running, optional elsewhere; the checker flags it once passed |
| `data-check` | required on Running, optional elsewhere: the command that proves the outcome exists (exit 0). Trusted input written only by the coordinator, never built from tracker or message text, because the checker runs it |
| `data-rel` | optional, space-separated `verb:ID`. `decides`, `unblocks`, `closes` point from this item; `after`, `needs`, `blocked-by`, `waits` point to it; `see` is undirected |
| `data-mechanism` | optional path of the item's `spell-it-out` page (the page links it as a `file://` URL) |
| `data-group` | optional theme id (`G1`, never reused): the item belongs to that theme record. One theme per item |
| `data-reply` | optional `text \| text` (`|` separates replies): the short replies the owner would type ("go release"), rendered as chips that copy `<id>: <text>` |
| `data-options` | optional `A text\|B text`, with `data-recommend="A"`: the item's choices as chips, the recommended one starred; a click copies `<id>: A — text` |

Inside: the `<h3>` title, linking the primary PR, issue or page (a Done title links the deliverable when one exists); then `<p class="next"><b>actor</b> next action</p>` for anything not Done; then, when the item cites more than one reference, `<p class="links">` with one `<a>` per further PR, issue, comment or page, so a `#NNN` written in the text always has a link to click. The script turns the title link and each anchor in the links row into chips in the link column (a link repeated in both appears once), removes the row, and leaves the title as text. A chip reads `#845` for a PR or issue, `#788 ↳` for a comment, the extension for a local file, `doc` / `repo` for other tracker links. The script also hides the `<b>actor</b>` prefix because the who column says it, and leaves the who cell blank in Needs you, where it is true by definition; adds the who, id, age and changed cells and the explain button (under **more**, absent on Done); tints rows whose actor is the owner; sorts rows on the page (due first, then oldest; Done newest first) without touching file order, so an added item goes at the end of its list.

**Local links** are absolute `file://` URLs, optionally ending in `:LINE`, and stay that way in the file. At render time the script rewrites a link to a local text file (markdown, text, code, config, logs, or no extension) to the owner's editor URL scheme, such as `zed://file/`, keeping the `:LINE` suffix and putting the original URL in the tooltip. Folders, images, PDFs and every other type keep `file://` for the default app; `.html` opens in the browser.

**Badges**, in the changed cell, short and relative, allowed to wrap: `overdue 3 d`, `due 10-30`, `stale`, `check` (the item has an outcome check; the command is the tooltip). Nothing else.

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

## The page

One `index.html`, no build step. A `<meta http-equiv="refresh" content="60">` keeps it current; state survives the refresh: per viewer in local storage, each section's view and collapsed state and the open help panel; in session storage, the scroll position, the expanded items and the graph overlay's zoom. Every storage access sits in try/catch, and without storage the defaults render. Parts, top to bottom:

1. **Header**: title, who the board serves, the refresh interval, the last-checked stamp the checker writes, and "N new, moved or yours changed since HH:MM" with a **mark seen** button.
2. **Band**: the Themes panel across the top while any theme is open, then three panels (next section), each with a one-line heading that names the question it answers.
3. **Four sections**, `<section id="needs-you">` through `done`, each an `<h2>` (the script appends the count and a `rows | tiles` toggle; clicking the heading collapses the section) over a column-header row and an `<ol class="items">`; without the script they render as one plain table. Needs you defaults to **tiles**: id and title, due or age in the corner, the next action, the reply and option chips, one meta line (link chips, relations, edited age, the changed dot) and a **more** button for the rest (mechanism glyph or explain button, outcome check, full link labels). The other states default to **rows**: one line each (id, title, who, due or age, the dot), which a click expands in place to the next action, chips, links and relations. Tiles take their natural height (`align-items: start` on the tile grid), never stretching to the tallest in their row; a grid rather than CSS columns, which would drop the order the sort and theme grouping set. The who column is dropped from a section where nothing under the current filter has an actor. An empty section collapses to its header and one line.
   Done shows the last 24 hours; older Done items sit behind one "N more" row.
4. **How this page works**: a collapsed `<details>` with the item schema, the state flow as a small diagram, and the panels table below.
5. The vendored diagram library and the page's own script, which reads the DOM once and renders from it.

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
| what do I answer? | reply and option chips under the next action, the recommended option starred | a click replaces retyping a reply the board already knows |
| counts by category | numbers in the section headers and a one-line flow (opened, closed, touched in 24 h; stale and overdue each shown only when non-zero) | three numbers read faster than three areas |

An inbound verb (`after`, `needs`, `blocked-by`, `waits`) is rendered reversed and relabelled (`before`, `needed by`, `blocks`, `awaited by`), so the graph keeps FORMS.md's arrow direction; `see` is drawn as a line with no arrowhead, and as an open circle in the matrix.

## The checker

`check.py`, standard library only, no network. It parses `index.html` with the HTML parser, collecting every element with `data-id` (and every theme with `data-gid`), the `<section id>` enclosing it, its title text, its next-action text and its links; a void tag such as `<br>` closes itself. Flags, one line each with the id (and the line number where the parser has one):

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
- `GROUP UNKNOWN` / `DUPLICATE gid`: an item naming a theme that does not exist; a theme id used twice
- `GROUP NO NEXT` / `GROUP DONE`: an open theme with no next step; an open theme with no open item (close it)
- `GROUP MISPLACED`: a theme record outside `<section id="groups">`, where the page cannot see it
- `GROUP CLOSED`: an open item tagged into a closed theme
- `GROUP MISSING`: an open item with no `data-group` whose `data-rel` targets a member of an open theme, or whose title names one as a whole word (the next action is not searched: it routinely lists other ids); tag it or reword it
- `STALE`: `data-changed` older than three days on an open item

Then one report line per `data-check` (`CHECK <id>`: DONE when it exits 0, OVERDUE when it fails past `due`, else pending, and whether it ran without a shell or through `sh -c`; a command with no shell metacharacter runs without one, under a timeout either way); then the lane-deadline ledger the coordinator keeps, whose overdue lines also count as flags; then the counts per state. Exit 1 on any flag. `--stamp` rewrites the last-checked line through the same anchor tool used for items, falling back to a direct write. The mutation run that proves it: a scratch copy with one planted instance of each defect, all flagged, exit 1.

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
  <edit helper>          600   optional: a script wrapping the anchor tool for ADD / MOVE / CLOSE, themes, links, replies and options
```

Back up `index.html` and the stylesheet before a restructure. The Done list is bounded by the **archive window** (default 14 days): a Done item older than that moves to `archive/<yyyy-mm>.html`, where its id stays taken.
