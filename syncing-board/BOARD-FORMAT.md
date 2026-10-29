# Board format

The reference half of [`syncing-board`](SKILL.md): the item, the page, the panels, the checker, the folder. Everything here is created once and then edited by anchor.

## The item

One item is one `<li class="item">` carrying its data as attributes, with the human text inside. Attributes are the record; the page's script derives everything else and writes none of them.

```html
<li class="item" data-id="L5" data-section="loose-ends" data-actor="owner" data-since="2026-10-28" data-changed="2026-10-28T17:17:00Z" data-rel="after:N1">
  <h3><a href="https://host/owner/repo/pull/845">Title as the owner would read it</a></h3>
  <p class="next"><b>owner</b> the one next action</p>
</li>
```

| attribute | meaning |
|---|---|
| `data-id` | stable, never reused. Prefix by first state (N / R / L / D) and the next free number |
| `data-section` | `needs-you` / `running` / `loose-ends` / `done`; must equal the `<section id>` it sits in |
| `data-actor` | who moves next: the owner, the coordinator, a named agent role, `lane`; `none` on Done |
| `data-since` | date the item first existed; kept on a move |
| `data-changed` | ISO UTC time of the last edit; stamped on every edit; the "changed" cell reads it |
| `data-due` | optional; the checker flags it once passed |
| `data-check` | optional outcome check command; exit 0 means the outcome exists |
| `data-rel` | optional, space-separated `verb:ID`. `decides`, `unblocks`, `closes` point from this item; `after`, `needs`, `blocked-by`, `waits` point to it |
| `data-mechanism` | optional URL of the item's explain-mechanism page |

Inside: the `<h3>` title, a link when there is a PR, issue or page (Done titles are always the deliverable link); then `<p class="next"><b>actor</b> next action</p>` for anything not Done. The script turns the title link into a chip in the link column (`#845` for a PR or issue, `#788 ↳` for a comment, `page` / `md` / `log` for a local file, `doc` / `repo` for other tracker links) and leaves the title as text; hides the `<b>actor</b>` prefix because the who column says it; adds the who, id, age and changed cells and the explain button; tints rows whose actor is the owner; sorts rows on the page (due first, then oldest; Done newest first) without touching file order, so an added item goes at the end of its list.

## The page

One `index.html`, no build step. A `<meta http-equiv="refresh" content="60">` keeps it current; scroll position and open panels survive the refresh through session storage. Parts, top to bottom:

1. **Header**: title, who the board serves, the refresh interval, the last-checked stamp the checker writes.
2. **Band**: three panels (next section), each with a one-line heading that names the question it answers.
3. **Four sections**, `<section id="needs-you">` through `done`, each an `<h2>` (the script appends the count) over a column-header row and an `<ol class="items">`. Same columns in every section. An empty section collapses to its header and one line.
4. **How this page works**: a collapsed `<details>` with the item schema, the state flow as a small diagram, and the visualization table below.
5. The vendored diagram library and the page's own script, which reads the DOM once and renders from it.

Stylesheet in `assets/`: tokens on `:root`, dark by `prefers-color-scheme`, the owner's tint as its own token, column widths in one grid template shared by the header row and the rows, a phone breakpoint that turns each row into a meta line (who, id, link, age, changed) over the title and next action, and hides the band's charts. No web fonts, no remote request of any kind.

## The panels: which form answers which question

Per panel, the most compact form that carries its question, and nothing the question does not need.

| question | form | reason |
|---|---|---|
| what must I do? | the owner's rows, tinted, Needs you first; no chart | position is the most accurately read channel; a list in priority order needs no decoding |
| who waits on whom? | a count matrix, actor by open state; clicking a cell filters the rows; the owner's cells outside Needs you marked | a handful of integers; a chart adds ink, not precision |
| how long open? | one bar per open item on a shared day axis, a now line, a tick at `due` | length on a common baseline is the next best channel; dots would hide duration. Weak while every item is a day old; it earns its place as items age |
| what unblocks what? | chips on the rows always; a node-link graph of only the connected items while there are at most twelve edges; an adjacency matrix beyond that | node-link reads for sparse chains and becomes a hairball past a dozen edges; a matrix stays legible at any density but hides paths |
| counts by category | numbers in the section headers and a one-line flow (opened, closed, touched in 24 h; stale and overdue only when non-zero) | three numbers read faster than three areas |

The graph draws every arrow from the thing that must come first, whichever item declared the relation: an inbound verb (`after`) is rendered reversed and relabelled (`before`). Isolated items are never drawn.

## The checker

`check.py`, standard library only. It parses `index.html` with the HTML parser, collecting every element with `data-id`, the `<section id>` enclosing it, its title text and its next-action text. Flags, each one line with the id and the line number:

- `DUPLICATE id`: the same `data-id` twice
- `SECTION MISMATCH`: `data-section` differs from the enclosing section
- `BAD data-changed` / `BAD data-due`: unparsable
- `OVERDUE`: `data-due` passed
- `NO NEXT ACTION`: a Needs-you item with no next action, or one that only names the actor
- `STALE`: `data-changed` older than three days on an open item
- `CHECK <id>`: the result of each `data-check`; a command with no shell metacharacter runs without a shell under a timeout, otherwise through `sh -c`, and the report says which

Then it echoes whatever lane-deadline ledger the coordinator keeps, prints the counts per state, and exits 1 on any flag. `--stamp` rewrites the last-checked line through the same anchor tool used for items, falling back to a direct write. The mutation run that proves it: a scratch copy with one planted instance of each defect, all flagged, exit 1.

## The folder

```
<private dir>/sync/      700
  index.html             600   the record and the page
  README.md              600   the edit protocol: ADD, MOVE (two patches), CLOSE, with worked examples
  check.py               600
  assets/style.css       600
  assets/<diagram-lib>   600   vendored, version and checksum recorded in README.md
  backups/               700   dated copies taken before any restructure
```

Back up `index.html` and the stylesheet before a restructure; never delete a Done item to make room.
