---
name: syncing-board
description: Keep the board the owner and their coordinator agent sync through, one private local page of what each party is waiting on, with next actor, age, outcome checks and dependencies. Use when a coordinator records an owner decision needed, a lane dispatched or done, a loose end or a deliverable; when the owner asks what they must do or what is going on; or when the board is first built or restructured.
---

# Syncing board

The **board** is the one surface where the **owner** (the human) and the **coordinator** (the agent the owner talks to) see what each is waiting on. The coordinator writes it at every **event**; the owner reads it **at a glance**. It replaces status messages: a result left in a terminal never reaches the other party, and state that lives in a file survives a fresh session.

One board, four **states**: **Needs you** (the owner must act), **Running** (a lane works, with an outcome check), **Loose ends** (a next actor is named, no lane yet), **Done** (a deliverable link). One **item** per thing waited on. The issue tracker already shows issues and PRs; the board shows only what the tracker cannot: private items, who moves next, how long each has waited, what unblocks what.

## Find or create the board

The board lives outside every repository, in the directory the project's instructions or the coordinator's memory name for private material; if none is named, ask once. Owner-only access (`umask 077`; `ls -l` shows no group or world bits). It loads nothing remote: a diagram library ships as a vendored copy beside the page. The folder holds `index.html` (the data and the page), `assets/`, a report-only `check.py`, a `README.md` stating the edit protocol, and `backups/`. Create what is absent from [BOARD-FORMAT.md](BOARD-FORMAT.md).

## Events to edits

Every event is one edit, stamped on the item:

| event | edit |
|---|---|
| the owner must decide something | item in Needs you; the next action names the decision; link the page that argues it |
| a lane is dispatched | item in Running; `due` = dispatch time plus twice the expected duration; `check` = the command that proves the outcome exists |
| a lane reports done | move to Done; the title becomes the deliverable link; drop next action, `due`, `check` |
| the owner decides | move the item where the decision points; Done when the decision closes it |
| something is owed and no lane holds it | item in Loose ends, with the next actor and one next action |
| an item blocks or follows another | `rel` on the item (verbs in BOARD-FORMAT.md) |
| `explain-mechanism` delivers a page for an item | `mechanism` = the page's path |

An id is never reused, Done included. `changed` is stamped on every edit. A next action is one sentence that opens with the actor's verb; an item in Needs you always has one. Edit by anchor: a tool that rejects a stale read rather than applying it, so two agents cannot silently overwrite each other on the one file. A move is two patches (cut and paste, then re-read and retarget the state), because one patch applies both against the pre-edit numbering and duplicates the item.

Done when: the item reflects the event, `changed` is stamped, and the checker reports 0 flags.

## Reading it for the owner

"What do I have to do": the owner's rows in order, by id, each with its next action. The owner's rows are every item whose next actor is the owner, whichever state it sits in. "What is going on": the counts per state and actor, the oldest open item, anything overdue or stale. Answer from the board and cite ids; memory of the conversation is not the record.

## The checker

`check.py` reports and never moves an item. It flags: a duplicate id; a state attribute disagreeing with the section the item sits in; an unparsable date; overdue (`due` passed); Needs-you without a next action; stale (unchanged for more than three days); and the result of every `check` command (a Running item reads DONE when it exits 0, OVERDUE when it fails past `due`, else pending). Exit 1 on any flag; standard library only; no network. Prove it with a mutation run: plant each defect in a scratch copy and watch each one flagged. `--stamp` writes the last-checked time into the page.

## Rendering at a glance

Position before colour: the owner's rows first and tinted; every other row lower contrast; Done muted. A dense table, one line per item, the same aligned columns in every state: who, id, item, next action, link, age, changed. Titles are plain text; the PR or issue number is the link chip; an item with a mechanism page shows a diagram glyph where the others show the explain button. Badges only where they mean something (overdue, stale, due). Above the table, panels that each answer one question the table cannot, in the most compact form that carries it (the table in BOARD-FORMAT.md).

Verify with a local headless browser on the `file://` URL: desktop width in dark and light, and 390 px; 0 remote requests, 0 console errors, no sideways scroll. Look at the screenshots, then hand them to a critic that has not seen the design and apply its layout findings; its content findings go to the owner. A single column of cards was tried first and rejected: unused space, and a clone of the tracker's own page.

## Explain hook

Each open item carries an explain button that copies `Use explain-mechanism on sync item <id>: <title>`. Pasted to the coordinator, it runs `explain-mechanism` on that item's case; the delivered page's path goes back on the item as `mechanism`, which is what turns the button into the glyph. A page served from `file://` cannot reach a terminal by itself; the clipboard is the whole mechanism until a localhost helper is deliberately built.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-29 — v1.** Prompted by the owner's request for one syncing surface between them and their coordinator after status messages in chat kept missing one side. Dogfooded on a private board before writing: v1 (a single column of cards) was rejected by the owner for unused space and for cloning the tracker's project page; v2 became the dense table under three panels, with the owner's rows highlighted inside the "what is going on" framing. A critic pass on the screenshots fixed arrow direction for inbound dependency verbs, the empty-state row, phone layout, and the glyph (the first one read as "share"). Three outside ideas shaped it: compact representations per question (HumanLayer's show-me), state in files rather than chat with small self-contained pages sharing one assets folder (Matt Pocock's teach), and hash-anchored edits that reject stale reads, which is what makes one HTML file safe as a record several agents write (hashline). Kept distinct from `explain-mechanism`: the board records what is waited on; a mechanism page explains one item, and the two meet at the `mechanism` attribute.
