---
name: graph-it
description: Draw one visual form as text or as HTML, in place of prose. Use when the user says "show me" or finds a message too long, or when another skill has chosen a form for a section and needs it drawn.
---

# Graph it

Draws one **form** so the reader takes it in **at a glance**. The skill that calls this one decides which form goes where; this one decides how the form is drawn. Called directly ("show me"), restate the last message as the form in [FORMS.md](FORMS.md) whose "shows" line matches the reader's question, one form per question.

## Drawing a form

1. **Elide.** Keep what the question needs; mark what was cut with `…`.
2. **Plain words** in the reader-facing forms: sentences, table cells, and the labels of flow, sequence and state diagrams say what happens in the reader's words, as for someone who has not read the code. The code-shaped forms (pseudocode, types, call stack, tree and layout, diff) keep their identifiers; that is what they show.
3. **Mark the answer point**: the deciding branch, the changed line, the failure path, the field the rule reads. Mark it with a word as well as with weight or colour.
4. **Ground it.** Every name, path and number comes from source opened in this session, cited as `path:line`; the model's memory of a codebase is untrusted. A form for a design that has no code yet takes its names from the agreed design and is labelled `proposed`.
5. **Render it for its surface.** Chat and terminal take the text recipe; Mermaid only where the surface renders it. A page takes the HTML recipe, and is screenshot at 390 px in the light scheme and at desktop width in the dark scheme.

Done when: removing any remaining line would lose part of the answer, no identifier or codename appears in a sentence, a table cell or a diagram label (cites, links and ids aside), the answer point is marked, each name resolves in the source or the form is labelled `proposed`, and the form was seen the way the reader will see it.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-11-02 — zoom set.** Prompted by the owner on a private report page that drew a required complete flow as one chart of 32 nodes, its labels up to three lines long and carrying setting names: "I really like the overall diagram ... it's just that it's humongous." What fought it: the eight-node budget had no branch for a flow that must be complete, so the page broke the budget. Now setting names and values go in a table under the diagram, and a longer flow is a zoom set: an overview row of stage boxes that is also the navigation, one diagram per stage within the budget, framed and stubbed in stage colours, and the whole diagram in a closed box with a zoom bar. Rebuilt from the private chart and checked in a headless browser on `file://` and in a sandboxed frame, light and dark, at 1280 and 390 px: every stage rendered within 671 px wide and 953 px tall, against 2050 × 3576 px for the one chart. Two parts of the proposed design changed on that evidence: the overview is a wrapping row of linked boxes, because a Mermaid overview came out 1537 px wide drawn left to right and 681 px tall drawn top to bottom; and stage colours are literal pairs, because `classDef` rejects `var()`. Review on PR #21 (1 SHOULD, 2 NIT) added the cut for paths that run side by side (checked against the same private chart, whose cut between two stages is such a reconvergence), named the 760 px column, and marked the elided stages in the example.

**2026-10-30 — review of PR #13.** Two rounds (1 BLOCKING, 7 SHOULD, 10 NIT). Plain words now bind only the reader-facing forms (sentences, table cells, diagram labels; cites, links and ids aside), and the code-shaped forms keep their identifiers. Decisions are hexagons, so the flow down to its deciding node fits the first screen. The recipe says how to find or create the vendored Mermaid copy (checked against the registry's sha512 `integrity`), colours every node on the case's path, writes the path's edges first so the `linkStyle` indices hold, and renders at natural size (`useMaxWidth: false`) inside the phone's scrolling box, so labels stay legible.

**2026-10-30 — Mermaid for control flow, plain words.** Prompted by the owner on a real page: "Where is the mermaid diagram for the control flow??????", and the page "still stupid". The HTML recipe had replaced the diagram with a list of boxes, on the reasoning that a scaled SVG shrinks its text on a phone, which traded the one picture the owner asked for against a phone edge case; and labels carried code names. Control flow on a page is now Mermaid from a vendored copy, with the case's path coloured and a phone box that scrolls sideways; a plain-words rule keeps identifiers in pseudocode, types and cites. Proved on the real private case before this change.

**2026-10-30 — named `graph-it`.** The owner's name for the skill, replacing the working name `visualizing` before the first merge.

**2026-10-30 — v1.** Prompted by the owner: `spell-it-out` pages lacked variety (control flow and pseudocode were expected almost every time) and ran too long. The owner set the split: this skill says how to draw each form, and the skills that build pages say where each form goes (`spell-it-out` for its page, `sync-panel` for its panels). Shaped by two published skills, rewritten here with no text adapted: HumanLayer's `show-me` (the lightest form, elided, `+`/`−` for change) and Matt Pocock's `teach` and `wait-what` (grounded claims; a long instruction yields a long answer, so this one stays short). `show-me` is the one-line user-invoked alias, as `grill-me` is for `grilling`.
