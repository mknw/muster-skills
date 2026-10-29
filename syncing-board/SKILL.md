---
name: syncing-board
description: Board an owner and their coordinator agent sync through, one private local page of what each party is waiting on. Use when the coordinator records an event on an existing board, when the owner asks what they must do or what is going on, or when the owner asks for a board to be built or restructured.
---

# Syncing board

The **board** is the one surface where the **owner** (the human) and the **coordinator** (the agent the owner talks to) see what each is waiting on. The coordinator writes it at every **event**; the owner reads it **at a glance**. It replaces status messages: a result left in a terminal never reaches the other party, and state that lives in a file survives a fresh session.

One board, four **states**: **Needs you** (the owner must act), **Running** (a lane works, with a due time and an outcome check), **Loose ends** (a next actor is named, no lane yet), **Done** (the deliverable). One **item** per thing waited on. The issue tracker already shows issues and PRs; the board shows only what the tracker cannot: private items, who moves next, how long each has waited, what unblocks what.

## Find or create the board

The board lives outside every repository, in the directory the project's instructions or the coordinator's memory name for private material; if none is named, ask once. Owner-only access (`umask 077`). It loads nothing remote: a diagram library ships as a vendored copy beside the page. Create what is absent from [BOARD-FORMAT.md](BOARD-FORMAT.md).

Done when: the folder is mode 700 and every file 600, and `check.py` exits 0.

## Events to edits

Every event is one edit, stamped on the item:

| event | edit |
|---|---|
| the owner must decide something | item in Needs you; the next action names the decision; link the page that argues it |
| a lane is dispatched | item in Running with `due` (dispatch time plus twice the expected duration) and `check` (the command that proves the outcome exists); both are required there |
| a lane reports done | move to Done; the title links the deliverable; drop next action, `due`, `check` |
| the owner decides | move the item where the decision points; Done when the decision closes it |
| something is owed and no lane holds it | item in Loose ends, with the next actor and one next action |
| an item blocks or follows another | `rel` on the item (verbs in BOARD-FORMAT.md) |
| `explain-mechanism` delivers a page for an item | `mechanism` = the page's path |
| a Done item is older than the archive window | move it to the archive page (BOARD-FORMAT.md, The folder) |

An id is never reused, Done and archive included. `changed` is stamped on every edit. A next action is one sentence naming what the actor does; an item in Needs you always has one. Edit by anchor: a tool that rejects a stale read rather than applying it, so two agents cannot silently overwrite each other on the one file. If the tool applies the ops of one patch against the pre-edit line numbers, a move is two patches: cut and paste, then re-read and retarget the state.

Done when: the item reflects the event, `changed` is stamped, and `check.py --stamp` reports 0 flags.

## Reading it for the owner

"What do I have to do": the owner's rows in order, by id, each with its next action. The owner's rows are every item whose next actor is the owner, whichever state it sits in. "What is going on": the counts per state and actor, the oldest open item, anything overdue or stale. Answer from the board; memory of the conversation is not the record.

Done when: the answer cites every id whose actor is the owner.

## The checker

`check.py` reports and never moves an item: it flags the record's defects (the list in BOARD-FORMAT.md), runs every outcome check, and exits 1 on any flag. Prove a new or changed checker with a **mutation run**: plant each defect in a scratch copy and watch each one flagged.

## Rendering at a glance

Position before colour: Needs you is the first section; the owner's rows are tinted wherever they sit, with the next action in full weight; Done is muted. A dense table, one line per item, the same aligned columns in every state. Titles are plain text; the PR or issue number is the link chip; an item with a mechanism page shows a diagram glyph where the others show a faint explain button. Badges only where they mean something. Above the table, panels that each answer one question the table cannot; the forms and the reasons are in BOARD-FORMAT.md.

Verify as in `explain-mechanism` step 8: a local headless browser on the `file://` URL, desktop width in both schemes and 390 px, with one item planted per badge and glyph so every rendering path is seen. Then hand the screenshots to a critic that has not seen the design; apply its layout findings, and take its content findings to the owner.

Done when: the three screenshots have been looked at; 0 remote requests, 0 console errors, scroll width equal to the viewport; every layout finding applied.

## Explain hook

Each open item carries an explain button that copies `Use explain-mechanism on sync item <id>: <title>`. Pasted to the coordinator, it runs `explain-mechanism` on that item; that skill's own gate decides, so an item with no mechanism behind it gets a chat answer and no `mechanism`. A delivered page's path goes back on the item as `mechanism`, which is what turns the button into the glyph. A page served from `file://` cannot reach a terminal by itself; the clipboard is the whole mechanism until a localhost helper is deliberately built.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-29 — fix round 1 (independent review with visual validation on PR #9).** Prompted by 1 BLOCKING, 12 SHOULD, 11 NIT. `due` and `check` are now required on Running items and the checker flags their absence (the live board had six Running rows with neither, passing clean). Badges got a short relative form; the explain button is visible at rest; the checker description matches a real checker (CHECK lines report, line numbers only where the parser has them, the deadline ledger affects the exit code); a `data-check` trust sentence; an archive window for Done; the two-patch move stated as conditional on the tool; the description lost its attribute list and gained the "existing board" guard; every section has a Done-when; lists and rendering detail live only in BOARD-FORMAT.md, whose panels rule points at explain-mechanism's "Picking the form".

**2026-10-29 — v1.** Prompted by the owner's request for one syncing surface between them and their coordinator after status messages in chat kept missing one side. Dogfooded on a private board before writing: v1 (a single column of cards) was rejected by the owner for unused space and for cloning the tracker's project page; v2 became the dense table under three panels, with the owner's rows highlighted inside the "what is going on" framing. A critic pass on the screenshots fixed arrow direction for inbound dependency verbs, the empty-state row, phone layout, and the glyph (the first one read as "share"). Three outside ideas shaped it: compact representations per question (HumanLayer's show-me), state in files rather than chat with small self-contained pages sharing one assets folder (Matt Pocock's teach), and hash-anchored edits that reject stale reads, which is what makes one HTML file safe as a record several agents write (hashline). Kept distinct from `explain-mechanism`: the board records what is waited on; a mechanism page explains one item, and the two meet at the `mechanism` attribute.
