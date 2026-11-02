# Board format

The reference half of [`sync-panel`](SKILL.md): the item and its decision context, the theme, the page, the panels, the checker, the helper, report bundles, the folder. Everything here is created once and then edited by anchor.

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
| `data-reply` | optional `text \| text` (`|` separates replies): the short replies the owner would type ("go release"), rendered as chips; a click sends the reply (The helper) |
| `data-options` | optional `A text\|B text`, with `data-recommend="A"`: the item's choices as chips, the recommended one starred; a click sends `A — text` (The helper) |
| `data-actions` | optional `Label=kind \| Label=kind`, written by the item's coding agent (a kind such as `explain` or `snooze:<date>`): extra buttons, each sending `action:<kind>` (The helper). The board renders only the buttons an item declares, plus the default Done on an item that declares no chips (The helper) |
| `data-ai-owner` | required in Needs you: the agent(s) waiting on the owner's answer, space-separated; shown as "for <name>" on the item; the helper sends each click to them |

Inside: the `<h3>` title, linking the primary PR, issue or page (a Done title links the deliverable when one exists); then `<p class="next"><b>actor</b> next action</p>` for anything not Done; then, when the item cites more than one reference, `<p class="links">` with one `<a>` per further PR, issue, comment or page, so a `#NNN` written in the text always has a link to click. The script turns the title link and each anchor in the links row into chips in the link column (a link repeated in both appears once), removes the row, and leaves the title as text. A chip reads `#845` for a PR or issue, `#788 ↳` for a comment, the file's name for a local file or a file in the tracker (without a markdown, HTML, text or log extension), and the hostname for any other link; a file chip shows only its icon until the item is expanded, the name in its tooltip. The script also hides the `<b>actor</b>` prefix because the who column says it; adds the who, id, age and changed cells and the explain button (under **more**, absent on Done); tints rows whose actor is the owner; sorts rows on the page (due first, then oldest; Done newest first) without touching file order, so an added item goes at the end of its list.

**Local links** are absolute `file://` URLs, optionally ending in `:LINE[:COL]`, and stay that way in the file. At render time the script rewrites a link to a local text file (markdown, text, code, config, logs, or no extension) to the owner's editor URL scheme, such as `zed://file/`, keeping the `:LINE[:COL]` suffix and putting the original URL in the tooltip. Folders, images, PDFs and every other type keep `file://` for the default app; `.html` opens in the browser.

**Decision context.** A Needs-you item carries what the owner needs to decide without hunting through links: three body lines after the next action, in this order, each on one line so the edit script can rewrite it.

```html
  <p class="brief">One to three plain sentences: what this is, what is being chosen, what happens next.</p>
  <dl class="terms"><dt>X2</dt><dd><a href="file:///abs/path/report.md:120">one-line plain meaning</a></dd></dl>
  <p class="links"><a href="https://host/owner/repo/pull/851" title="what this link covers">851</a></p>
```

- **Brief**: shown when the item is expanded, above the chips.
- **Terms**: every shorthand token in the item's options, next action or brief, each linked to the exact place it is defined (a file with `:LINE`, or a URL with an `#anchor`); shown expanded, under the brief, as "TERM: meaning".
- **Link notes**: the `title` on each links-row anchor says what that link covers; an expanded item shows each note beside its chip. A `title` on the `<h3>` link shows the same way and is optional.
- **AI owner**: `data-ai-owner` (attribute table).

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

1. **Header**: title, who the board serves, the refresh interval, the last-checked stamp the checker writes, "N new, moved or yours changed since HH:MM" with a **mark seen** button, and "helper on" or "helper offline".
2. **Band**: the Themes panel across the top while any theme is open, then three panels (next section), each with a one-line heading that names the question it answers.
3. **Four sections**, `<section id="needs-you">` through `done`, each an `<h2>` (the script appends the count and a `rows | tiles` toggle; clicking the heading collapses the section) over a column-header row and an `<ol class="items">`; without the script they render as one plain table.
   - **Tiles**, the default in Needs you: id and title, due or age in the corner, the next action, the reply and option chips, one meta line (link chips, relations, edited age, the changed dot) and a **more** button for the rest (mechanism glyph or explain button, outcome check, full link labels).
   - **Rows**, the default elsewhere: one line each (id, title, who, due or age, the dot), which a click expands in place to the next action, chips, links and relations.
   - Tiles pack masonry-style: each spans as many 1 px grid rows as its measured height (no row gap, the spacing inside each span), and a resize observer repacks a section whenever a tile changes size. The grid's forward-only auto-placement lets a short tile start in the gap under a shorter neighbour but never above a tile that sorts before it, so reading and keyboard order stay the sort and theme order; CSS columns would pack tighter and break that order. Rows view drops the spans, and without the script tiles take their natural height (`align-items: start`) and never overlap.
   - In Needs you, an item whose answer was delivered (sent or seen; neither failed, answered an older version, nor edited after the answer) steps into a collapsed strip at the bottom, "Answered, waiting on the agent (N)", one dimmed line each with its answer and state, until its AI owner moves it. The section count covers only the items still to answer.
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
- `LINK WITHOUT NOTE`: a links-row anchor on a Needs-you item with no `title`
- `UNDEFINED TERM`: a shorthand token in a Needs-you item's options, next action or brief that its terms do not define. Shorthand is an upper-case group of one to four letters followed by digits (optional hyphen, optional bracketed suffix: `X2`, `QA-4`, `K5(b)`) or by a bracketed suffix alone (`AB(c)`); two joined by a dash are one range token, defined as a range or at both ends. Item ids, theme ids and agent names are excluded, and `#NNN`, dates and version strings cannot match. Model and hash names match too; a one-line definition costs nothing
- `BUNDLE …`: the seven report-bundle flags (Report bundles)
- `STALE`: `data-changed` older than three days on an open item

Then one report line per `data-check` (`CHECK <id>`: DONE when it exits 0, OVERDUE when it fails past `due`, else pending, and whether it ran without a shell or through `sh -c`; a command with no shell metacharacter runs without one, under a timeout either way); then the lane-deadline ledger the coordinator keeps, whose overdue lines also count as flags; then the counts per state. Exit 1 on any flag. `--stamp` rewrites the last-checked line through the same anchor tool used for items, falling back to a direct write. The mutation run that proves it: a scratch copy with one planted instance of each defect, all flagged, exit 1.

## The helper

A local server with no dependency beyond its runtime, started and stopped by hand through a lifecycle script (`start`, `stop`, `status`), never as a login item. It serves the board folder at `http://127.0.0.1:PORT/`, so the board opens there with none of `file://`'s limits, and adds `POST /click`, `POST /retry` and `GET /state` (fetched at each page load). It never writes the board file: its writes are appends to the inbox, the one-time bootstrap file (rewritten on each use) and the session file.

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
- **Input**: an open item's id, an answer that item declares (reply, option or action, or `Done` when it declares none), a note within its cap, a body within a size cap, JSON only.
- **File serving**: a file is served only when the board links it, its real path (every symlink resolved) lies inside the reports folder, and it is a regular file; a served file gets a sandbox CSP so it cannot act as the board. The hidden-path refusal sits in the edit script's copy step (Linked files).
- **Strict CSP on the board**: `script-src 'self'` with no inline script, `frame-ancestors 'none'`, `X-Frame-Options: DENY`.
- **Argv-only process calls**: every mailbox and terminal call is an argument array; request content reaches no shell. The wake's terminal handle must match the mailbox system's plain handle shape, and the item id it types must be plain letters, digits and dashes.
- **Idempotent clicks**: each decision carries a client id that a double click or a retry reuses, and the helper records and sends a known id once. An id already used for an answer is refused for feedback, and the reverse (400). Each mailbox send carries a deterministic request id, so an ambiguous retry is replayed rather than duplicated.
- **Delivery resume**: a delivery cut off by a reload (a click recorded, no `sent` or `send-failed` for a recipient) is re-delivered by the new worker at boot and when the page replays that click id, to the recipients recorded with the click when it was made, never to names the routing file gained since; the same request id makes the mailbox replay a copy that did go out instead of sending it twice. Resume only finishes recorded clicks and constructs none.
- **Visible delivery failure**: every send ends as `sent` or `send-failed`, in the inbox and on the page; a malformed mailbox reply is logged and keeps the helper running, and the receipt poll runs at most once every few seconds however often `/state` is fetched.
- **Lifecycle identity**: `stop` kills only a process whose command line is the runtime running this helper, so a recycled PID survives. The worker exits when its supervisor is gone, deleting the secret files only while they still hold its own. `start`, `stop` and `status` never trust the pidfile alone: each also checks whether the port answers, and none reports success while another process holds it.
- **Known residual**: cookies are not port-scoped, so the browser also sends the session cookie to any other server on 127.0.0.1 the owner opens; `HttpOnly` keeps page scripts from it, but that server could log it. The cookie stays valid across reloads for as long as the supervisor runs; only stop then start rotates it.

## Report bundles

A **report bundle** is a folder of pages the owner reads from one board item, with feedback per section that reaches the item's AI owners like a click. This section is the whole contract: a lane builds and publishes a bundle from it alone.

**The design.** Report pages stay sandboxed, in an opaque origin, so no script a lane writes can read the board's token or post as the owner. A **wrapper** page the helper writes frames the report and does all the sending, and the owner types the note in the wrapper. A page can only point at a section.

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
- No network load of any kind: no remote `src` / `srcset`, `<link href>`, CSS `url()` / `@import`, script `fetch` / `import` / `WebSocket`, and no forms. A plain `<a href>` to an outside page is a link, not a load, and opens a new tab. The served CSP blocks every load anyway.
- Scripts run sandboxed, with no access to the board, its cookie or token, the parent page or the network. `localStorage` and `sessionStorage` throw there, so wrap any use in try/catch.
- An optional "comment on this section" button may send exactly this message, and nothing else:

  ```js
  parent.postMessage({ type: 'sync-feedback', section: 'risks' }, '*');
  ```

  The wrapper then selects that section and focuses its note field. It lists every section anyway, so a page needs no script to get feedback.

**Publish.** `<edit script> bundle ID DIR` copies the folder to `reports/<sha8>-<name>/` (folders 700, files 600) and links the item to the entry page, labelled with the bundle title. It refuses a folder or manifest that breaks the rules above, naming the file, and an item that already links more than one bundle (one bundle per item). A refusal changes nothing: every check runs before anything is copied. It does not check pages against their HTML: an `entry` that names no listed page falls back to the first page, and a section id missing from its page is caught only by the checker (`MISSING SECTION`). Publishing again with changed content replaces the item's bundle in place, removing the old folder unless another item links it; the same content changes nothing.

**What the owner sees.** On the helper page the item's link opens the wrapper, `/r/<bundle>/<page>?item=ID`: the page list, a section picker, a note field (2000 characters) and **Send feedback**, around the report in a sandboxed frame. The item then shows "feedback on <page>#<section> · sending…", then "· sent HH:MM", then "seen by …". Feedback is a comment, not an answer: the item stays where it is and never enters the answered strip. A Done item's report stays readable, and its wrapper shows no feedback form. On the `file://` page the link opens the entry page directly, with no feedback.

**What the AI owner receives.** A message headed "<id>: feedback on <page>#<section>", the note in the body, and a payload of kind `sync-feedback` (item id, bundle, page, section, note, version, click id, time), followed by the wake; the coordinator gets a notice-only copy. Delivery, retry, resume and visible failure are the click path's (The helper).

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
- **The one message**: the wrapper acts on a message only when its source is its own report frame, its data is a plain object with exactly two keys, `type: 'sync-feedback'` and a string `section`, and the section is an own property of the manifest's section map; it ignores everything else. Every manifest string it renders is escaped.
- **`POST /feedback`**: Host, Origin, token and cookie as for a click, and an idempotent click id; an open item that links that bundle; a page and section from that bundle's manifest; a non-empty note within its cap.

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
  <edit script>          600   optional: wraps the anchor tool for ADD / MOVE / CLOSE, themes, links, replies, options and decision context; `add` refuses an id already on the board, `links` merges into the links row, and `links --replace` prints each href it drops
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
