---
name: sync-panel
description: Board an owner and their coordinator agent sync through, one private local page of what each party is waiting on, where the owner's clicks reach the waiting agent. Use when the coordinator records an event on an existing board, when a message says the owner answered, or sent feedback on, an item on the sync board, when the owner asks what they must do or what is going on, or when the owner asks for a board to be built or restructured.
---

# Sync panel

The **board** is the one surface where the **owner** (the human) and the **coordinator** (the agent the owner talks to) see what each is waiting on. The coordinator writes it at every **event**; the owner reads it **at a glance** and answers on it, each click reaching the agent that waits on the answer. It replaces status messages: a result left in a terminal never reaches the other party, and state that lives in a file survives a fresh session.

One board, four **states**: **Needs you** (the owner must act), **Running** (a lane works, with a due time and an outcome check), **Loose ends** (a next actor is named, no lane yet), **Done** (the deliverable). One **item** per thing waited on. The issue tracker already shows issues and PRs; the board shows only what the tracker cannot: private items, who moves next, how long each has waited, what unblocks what.

## Find or create the board

The board lives outside every repository, in the directory the project's instructions or the coordinator's memory name for private material; if none is named, ask once. Owner-only access (`umask 077`). It loads nothing remote: a diagram library ships as a vendored copy beside the page. Create what is absent from [BOARD-FORMAT.md](BOARD-FORMAT.md), the helper included.

Done when: the folder is mode 700 and every file 600, `check.py` exits 0, and the helper passes the click Done-when below.

## Events to edits

Every event is one edit, stamped on the item:

| event | edit |
|---|---|
| the owner must decide something | item in Needs you; the next action names the decision; link the page that argues it; add the decision context: a brief, the terms, a note on each link, and the AI owner(s) waiting on the answer (BOARD-FORMAT.md, Decision context) |
| a lane is dispatched | item in Running with `due` (dispatch time plus twice the expected duration) and `check` (the command that proves the outcome exists); both are required there |
| a lane reports done | close it: move to Done, the title links the deliverable, the next action goes |
| the owner decides | move the item where the decision points; Done when the decision closes it |
| something is owed and no lane holds it | item in Loose ends, with the next actor and one next action |
| an item blocks or follows another | `rel` on the item (verbs in BOARD-FORMAT.md) |
| items belong together, or are one decision for the owner | a theme record with one next step, and `group` on each member (BOARD-FORMAT.md, The theme) |
| a theme's work is done | close the theme; its id stays taken |
| the owner's answer is a short reply or a choice | `reply`, or `options` with the recommended one, on the item |
| a lane delivers a report the owner reads and comments on | publish it as the item's report bundle with the edit script's `bundle` command, and set `ai-owner` so feedback has somewhere to go (BOARD-FORMAT.md, Report bundles) |
| the coding agent behind an item needs another answer kind | declare the button on the item (`actions`, BOARD-FORMAT.md, The item) |
| an event names a PR, issue, comment or page | link each one: the title links the primary, every other goes in the item's links row (BOARD-FORMAT.md) |
| an item asks the owner to read a document | link the document itself beside its PR: the file in the worktree that has the PR's branch checked out, fast-forwarded to the PR head first when it is clean, plus a `:LINE[:COL]` link to the section the owner rules on (BOARD-FORMAT.md, Local links); re-point both at the main checkout when the PR merges |
| `spell-it-out` delivers a page for an item | `mechanism` = the page's path |
| a Done item is older than the archive window | move it to the archive page (BOARD-FORMAT.md, The folder) |

An id is never reused, Done and archive included. `changed` is stamped on every edit. A move or close rewrites the opening tag: it sets id, state, actor, since and changed, and carries every other attribute over, so a theme, relations and any attribute added later survive; a close also drops the open-item chips (`due`, `check`, `reply`, `options`, `recommend`). A next action is one sentence naming what the actor does, verb first; on the owner's rows at most 15 words, with the detail in the linked page; an item in Needs you always has one. Edit by anchor: a tool that rejects a stale read rather than applying it, so two agents cannot silently overwrite each other on the one file. If the tool applies the ops of one patch against the pre-edit line numbers, a move is two patches: cut and paste, then re-read and retarget the state.

Done when: the item reflects the event, `changed` is stamped, and `check.py --stamp` reports 0 flags and no CHECK line reading DONE.

## Reading it for the owner

"What do I have to do": the owner's rows in order, by id, each with its next action; a theme with several of them is one decision, answered with the theme's next step. The owner's rows are every item whose next actor is the owner, whichever state it sits in, except an item in the answered strip, which waits on its AI owner. "What is going on": the counts per state and actor, the oldest open item, anything overdue or stale. Answer from the board; memory of the conversation is not the record.

Done when: the answer cites every id whose actor is the owner.

## Clicks reach the AI owner

The owner answers by clicking a reply, option or declared button, or the default **Done** (BOARD-FORMAT.md, The helper), with an optional note. The **helper**, a small local server bound to the loopback address (BOARD-FORMAT.md, The helper), serves the board and carries the click:

1. The click carries the item id, the answer, the time, the item's version (`changed`) and the note.
2. The helper appends it to the **inbox**, an append-only event log, then sends it in full to each of the item's AI owners through the agents' mailbox system (e.g. Orca), and a notice-only copy to the coordinator, skipped when the coordinator is itself an owner. A mailbox message does not wake an idle agent, so after each delivered owner copy the helper **wakes** that agent's terminal.
3. Each send ends as delivered or failed in the inbox; the page shows sending, sent, seen, not delivered (with retry), answered an older version, and resolved, and a delivered answer steps into the answered strip.

The helper never writes the board file. An AI owner that receives a click acts on it, then moves the item itself; leaving Needs you is what marks the click resolved. Feedback on a report section travels the same path (BOARD-FORMAT.md, Report bundles); its AI owner acts on the note and leaves the item where it is. The coordinator's notice needs no action. Only offline does a click fall back to the clipboard, and it says so (BOARD-FORMAT.md, The helper).

Saving the helper's code file is a **live deploy** to the owner's running helper (BOARD-FORMAT.md, The helper, Self-reload), gated by nothing beyond a syntax check. Edit and test a copy (another port, a stub mailbox), then move the finished file into place in one step. Tests work on a scratch copy of the board and set the test flag that makes the edit script refuse the real board before reading or writing it. They stop only the processes they started, by recorded PID, never by a name pattern: a pattern also matches the owner's live helper, and killing it ends the owner's session. A worker change reaches the owner with no restart and no new URL; a change to the supervisor itself needs stop, start and a fresh one-time URL for the owner.

Done when (building or changing the helper): a click on a test item lands in the inbox, reaches each AI owner's mailbox (read there, not assumed) and gives the coordinator its notice; the board file's checksum is the same before and after; the page shows sent, seen and resolved across a reload; and a mutation for each baseline requirement is refused, at least: no token 403, a foreign Origin 403, an unknown id 400, `Done` on an item that declares chips 400, a stale version shown as "answered an older version", a reload in the middle of a delivery ending in exactly one copy, a hostile terminal handle recorded as `wake-failed` with nothing run, and a killed supervisor taking its worker down with `start`, `stop` and `status` all reporting the truth; and each report-bundle requirement (BOARD-FORMAT.md, Report bundles) refused by its own mutation.

## The checker

`check.py` reports and never moves an item: it flags the record's defects (the list in BOARD-FORMAT.md), runs every outcome check, and exits 1 on any flag. Prove a new or changed checker with a **mutation run**: plant each defect in a scratch copy and watch each one flagged.

## Rendering at a glance

Position before colour: Needs you is the first section; the owner's rows are tinted wherever they sit, with the next action in full weight; Done is muted. Needs you renders as tiles, each a decision read whole; the other states as one-line rows that expand in place; each section has its own view toggle (BOARD-FORMAT.md, The page). Above the sections, panels that each answer one question the sections cannot; BOARD-FORMAT.md says which form answers each panel's question, and `graph-it` says how that form is drawn.

Verify with a local headless browser on the `file://` URL, and on the helper's page when it runs: the two screenshots `graph-it` names (390 px light, desktop dark) plus desktop light, with one item planted per badge and glyph, a section in each view, a row expanded and the graph overlay open, so every rendering path is seen. Then hand the screenshots to a critic that has not seen the design; apply its layout findings, and take its content findings to the owner.

Done when: the three screenshots have been looked at; 0 remote requests, 0 console errors, scroll width equal to the viewport; every layout finding applied.

## Explain hook

Each open item carries an explain button that copies `Use spell-it-out on sync item <id>: <title>`. Pasted to the coordinator, it runs `spell-it-out` on that item; that skill's own gate decides, so an item with no mechanism behind it gets a chat answer and no `mechanism`. A delivered page's path goes back on the item as `mechanism`, which is what turns the button into the glyph. The button stays a clipboard copy while the helper runs: the helper carries answers to an item's AI owners, and this request goes to the coordinator.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-11-02 — report bundles and section feedback.** Prompted by the owner asking to comment on report pages section by section, ahead of a lane programme that publishes its reports that way. The design call: report pages stay sandboxed in an opaque origin, a helper-written wrapper frames them and does all the sending, and a page may post one message that points at a section and carries no text. Added the bundle contract (folder, manifest, pages, publish command, caps, one bundle per item), feedback as a comment that never enters the answered strip, seven `BUNDLE` checker flags, and the security requirements as tested in an independent review (per-bundle key, frame-ancestors, the message's source and shape check, manifest-validated feedback). The click path gained click ids refused across kinds and recipients recorded per click for resume. That review killed the owner's live helper with a pattern-matched kill, which is where the test rule on recorded PIDs comes from.

**2026-11-02 — masonry, default Done, self-reload, answered strip, wake, delivery resume.** Prompted by the live board moving ahead of the skill again, through its own build and two security review rounds. Tiles pack masonry-style in sort order; a decision item with no buttons gets a default Done; the helper reloads itself under a supervisor with the session persisted, which makes saving its code a live deploy; a refused send is never silently copied, and the `file://` page says clicks are not sent from it; delivered answers step into a collapsed strip; the helper wakes the AI owner's terminal and flags an answer unread for 30 minutes; a delivery cut off by a reload resumes at boot without duplicating; a killed supervisor takes its worker down and the lifecycle script never trusts the pidfile alone; the edit script refuses an existing id on `add` and merges `links`. The checker gained `BAD ACTIONS` and `ACTIONS RULE DRIFT`.

**2026-11-01 — renamed `sync-panel`; decision context and clicks.** Prompted by the live board gaining its interactive layer, which the 2026-10-30 rule ties to the rename. Decision context: every Needs-you item carries a plain brief, its shorthand defined with a link to each definition, a note on each link and the AI owner(s) waiting on the answer, with four checker flags (`NO BRIEF`, `UNDEFINED TERM`, `LINK WITHOUT NOTE`, `NO AI OWNER`). Clicks: a loopback helper serves the board and relays each click to the item's AI owners through the agents' mailbox system, with a notice to the coordinator, an append-only inbox, page states from sent to resolved, buttons declared per item, a clipboard fallback, and a security baseline stated as requirements. The helper never writes the board file. The description gained the branch for an agent a click reaches.

**2026-10-31 — tiles and rows, open-items graph, editor links.** Prompted by a live board that had moved ahead of the skill on the owner's layout decisions. Needs you became tiles and the other states one-line rows, each section with a per-viewer view toggle, rows expanding in place and staying expanded across the refresh, tiles at their natural height; the dependency panel counts and draws only links between open items, and gained a full-screen node-link overlay; local text-file links open in the owner's editor at render time while the file keeps `file://`; an item asking the owner to read a document links the document and the section to rule on, not only its PR; move and close carry every attribute they do not render, close dropping the open-item chips. The checker gained `GROUP MISSING`.

**2026-10-30 — themes and easing.** Prompted by the owner grouping items into themes that span all four states, and asking what else makes them do work the board could do. Added: the theme record and `group` on items, rendered as a Themes panel, a stripe per member, members kept together inside each state, and one decision row in Needs you; "changed since you looked" with an explicit mark seen; relation chips that show the other item's title; Done limited to the last 24 hours; reply and option chips; `see` as an undirected relation; next actions capped at 15 words. The checker gained BAD REL, LONG NEXT, BAD OPTIONS and the four theme checks (each planted in a scratch copy and flagged), and stopped treating a `<br>` in a title as an unclosed element, a false NO NEXT ACTION the PR #10 review had found. Review round 1 on PR #14 (1 BLOCKING, 9 SHOULD, 13 NIT) then made close keep an item's theme, relations and links; fixed `<br/>`; dotted only new, moved and owner-edited items, marked at page load; drew `see` without an arrowhead; showed the themes container and added GROUP MISPLACED; refused to reuse a closed theme id; cleared a stale theme filter; counted archive ids; and removed board content from this record. Round 2 returned MERGE; its nits added GROUP CLOSED, a section boundary for GROUP MISPLACED, the closed-theme and line-end guards on tagging and closing, older Done members shown under the theme filter, and `see` as an open circle in the matrix.

**2026-10-30 — name.** The owner set the rename: this skill becomes `sync-panel` when the board gains its interactive layer, in the same change; until then it keeps `syncing-board`, since the page only displays.

**2026-10-30 — links row and `graph-it`.** Prompted by the owner having to tell the coordinator to add links for an item that carried several PRs. The live board had already grown a links row for it; the skill now records it (BOARD-FORMAT.md, The item), adds the event row that says to link every reference, and adds the `UNLINKED REF` flag so the omission is caught by the checker (proved by a planted `#999`; Done items are exempt, since their deliverable link is the record). The panels' forms are now drawn as `graph-it` says, while this skill keeps the table of which form answers which board question; the verify line names the two screenshots `graph-it` takes plus desktop light.

**2026-10-29 — fix round 1 (independent review with visual validation on PR #9).** Prompted by 1 BLOCKING, 12 SHOULD, 11 NIT. `due` and `check` are now required on Running items and the checker flags their absence (the live board had six Running rows with neither, passing clean). Badges got a short relative form; the explain button is visible at rest; the checker description matches a real checker (CHECK lines report, line numbers only where the parser has them, the deadline ledger affects the exit code); a `data-check` trust sentence; an archive window for Done; the two-patch move stated as conditional on the tool; the description lost its attribute list and gained the "existing board" guard; every section has a Done-when; lists and rendering detail live only in BOARD-FORMAT.md, whose panels rule points at explain-mechanism's "Picking the form".

**2026-10-29 — v1.** Prompted by the owner's request for one syncing surface between them and their coordinator after status messages in chat kept missing one side. Dogfooded on a private board before writing: v1 (a single column of cards) was rejected by the owner for unused space and for cloning the tracker's project page; v2 became the dense table under three panels, with the owner's rows highlighted inside the "what is going on" framing. A critic pass on the screenshots fixed arrow direction for inbound dependency verbs, the empty-state row, phone layout, and the glyph (the first one read as "share"). Three outside ideas shaped it: compact representations per question (HumanLayer's show-me), state in files rather than chat with small self-contained pages sharing one assets folder (Matt Pocock's teach), and hash-anchored edits that reject stale reads, which is what makes one HTML file safe as a record several agents write (hashline). Kept distinct from `spell-it-out`: the board records what is waited on; a mechanism page explains one item, and the two meet at the `mechanism` attribute.
