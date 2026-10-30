# Board format

The reference half of [`syncing-board`](SKILL.md): the item, the page, the panels, the checker, the folder. Everything here is created once and then edited by anchor.

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
| `data-rel` | optional, space-separated `verb:ID`. `decides`, `unblocks`, `closes` point from this item; `after`, `needs`, `blocked-by`, `waits` point to it |
| `data-mechanism` | optional path of the item's explain-mechanism page (the page links it as a `file://` URL) |

Inside: the `<h3>` title, linking the primary PR, issue or page (a Done title links the deliverable when one exists); then `<p class="next"><b>actor</b> next action</p>` for anything not Done; then, when the item cites more than one reference, `<p class="links">` with one `<a>` per further PR, issue, comment or page, so a `#NNN` written in the text always has a link to click. The script turns the title link and each anchor in the links row into chips in the link column (a link repeated in both appears once), removes the row, and leaves the title as text. A chip reads `#845` for a PR or issue, `#788 ↳` for a comment, the extension for a local file, `doc` / `repo` for other tracker links. The script also hides the `<b>actor</b>` prefix because the who column says it, and leaves the who cell blank in Needs you, where it is true by definition; adds the who, id, age and changed cells and the explain button (faint at rest, full on hover, absent on Done); tints rows whose actor is the owner; sorts rows on the page (due first, then oldest; Done newest first) without touching file order, so an added item goes at the end of its list.

**Badges**, in the changed cell, short and relative, allowed to wrap: `overdue 3 d`, `due 10-30`, `stale`, `check` (the item has an outcome check; the command is the tooltip). Nothing else.

## The page

One `index.html`, no build step. A `<meta http-equiv="refresh" content="60">` keeps it current; the scroll position (session storage) and each section's collapsed state and the open help panel (local storage) survive the refresh. Parts, top to bottom:

1. **Header**: title, who the board serves, the refresh interval, the last-checked stamp the checker writes.
2. **Band**: three panels (next section), each with a one-line heading that names the question it answers.
3. **Four sections**, `<section id="needs-you">` through `done`, each an `<h2>` (the script appends the count; clicking it collapses the section) over a column-header row and an `<ol class="items">`. Same columns in every section: who, id, item, next action, link, age, changed. An empty section collapses to its header and one line.
4. **How this page works**: a collapsed `<details>` with the item schema, the state flow as a small diagram, and the panels table below.
5. The vendored diagram library and the page's own script, which reads the DOM once and renders from it.

Stylesheet in `assets/`: tokens on `:root`, dark by `prefers-color-scheme`, the owner's tint as its own token, column widths in one grid template shared by the header row and the rows, a phone breakpoint that turns each row into a meta line (who, id, link, age, changed) over the title and next action, and hides the band's charts. No web fonts, no remote request of any kind.

## The panels: which form answers which question

Per panel, the form below, drawn as `visualizing` ([FORMS.md](../visualizing/FORMS.md)) says. The board's own questions and the forms that answer them:

| question | form | reason |
|---|---|---|
| what must I do? | the owner's rows, tinted, Needs you first; no chart | position is the most accurately read channel; a list in priority order needs no decoding |
| who waits on whom? | a count matrix, one row per actor present by open state; clicking a cell filters the rows; the owner's cells outside Needs you marked | a handful of integers; a chart adds ink, not precision |
| how long open? | one bar per open item on a shared day axis, a now line, a tick at `due` | length on a common baseline is the next best channel; dots would hide duration. Weak while every item is a day old; it earns its place as items age |
| what unblocks what? | chips on the rows always; a node-link graph of only the connected items while there are at most twelve edges; an adjacency matrix beyond that | node-link reads for sparse chains and becomes a hairball past a dozen edges; a matrix stays legible at any density but hides paths |
| counts by category | numbers in the section headers and a one-line flow (opened, closed, touched in 24 h; stale and overdue each shown only when non-zero) | three numbers read faster than three areas |

An inbound verb (`after`, `needs`, `blocked-by`, `waits`) is rendered reversed and relabelled (`before`, `needed by`, `blocks`, `awaited by`), so the graph keeps FORMS.md's arrow direction.

## The checker

`check.py`, standard library only, no network. It parses `index.html` with the HTML parser, collecting every element with `data-id`, the `<section id>` enclosing it, its title text, its next-action text and its links. Flags, one line each with the id (and the line number where the parser has one):

- `DUPLICATE id`: the same `data-id` twice, counting the archive pages
- `SECTION MISMATCH`: `data-section` differs from the enclosing section
- `BAD data-changed` / `BAD data-due`: unparsable
- `OVERDUE`: `data-due` passed
- `NO NEXT ACTION`: a Needs-you item with no next action, or one that only names the actor
- `NO CHECK`: a Running item without `data-due` or without `data-check`
- `UNLINKED REF`: a `#NNN` in an open item's title or next action that no link in the item points at (`/pull/NNN` or `/issues/NNN`); Done items are exempt
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
  <edit helper>          600   optional: a script wrapping the anchor tool for ADD / MOVE / CLOSE
```

Back up `index.html` and the stylesheet before a restructure. The Done list is bounded by the **archive window** (default 14 days): a Done item older than that moves to `archive/<yyyy-mm>.html`, where its id stays taken.
