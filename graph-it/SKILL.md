---
name: graph-it
description: Draw one visual form as text or as HTML, in place of prose. Use when the user says "show me" or finds a message too long, or when another skill has chosen a form for a section and needs it drawn.
---

# Graph it

Draws one **form** so the reader takes it in **at a glance**. The skill that calls this one decides which form goes where; this one decides how the form is drawn. Called directly ("show me"), restate the last message as the form in [FORMS.md](FORMS.md) whose "shows" line matches the reader's question, one form per question.

## Drawing a form

1. **Elide.** Keep what the question needs; mark what was cut with `…`.
2. **Plain words.** Labels and sentences say what happens in the reader's words, as for someone who has not read the code. Function names, field names and internal codenames belong in pseudocode, types and cites only.
3. **Mark the answer point**: the deciding branch, the changed line, the failure path, the field the rule reads. Mark it with a word as well as with weight or colour.
4. **Ground it.** Every name, path and number comes from source opened in this session, cited as `path:line`; the model's memory of a codebase is untrusted. A form for a design that has no code yet takes its names from the agreed design and is labelled `proposed`.
5. **Render it for its surface.** Chat and terminal take the text recipe; Mermaid only where the surface renders it. A page takes the HTML recipe, and is screenshot at 390 px in the light scheme and at desktop width in the dark scheme.

Done when: removing any remaining line would lose part of the answer, no identifier or codename appears outside pseudocode, types and cites, the answer point is marked, each name resolves in the source or the form is labelled `proposed`, and the form was seen the way the reader will see it.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-30 — Mermaid for control flow, plain words.** Prompted by the owner on a real page: "Where is the mermaid diagram for the control flow??????", and the page "still stupid". The HTML recipe had replaced the diagram with a list of boxes, on the reasoning that a scaled SVG shrinks its text on a phone, which traded the one picture the owner asked for against a phone edge case; and labels carried code names. Control flow on a page is now Mermaid from a vendored copy, with the case's path coloured and a phone box that scrolls sideways; a plain-words rule keeps identifiers in pseudocode, types and cites. Proved on the real private case before this change.

**2026-10-30 — named `graph-it`.** The owner's name for the skill, replacing the working name `visualizing` before the first merge.

**2026-10-30 — v1.** Prompted by the owner: `spell-it-out` pages lacked variety (control flow and pseudocode were expected almost every time) and ran too long. The owner set the split: this skill says how to draw each form, and the skills that build pages say where each form goes (`spell-it-out` for its page, `syncing-board` for its panels). Shaped by two published skills, rewritten here with no text adapted: HumanLayer's `show-me` (the lightest form, elided, `+`/`−` for change) and Matt Pocock's `teach` and `wait-what` (grounded claims; a long instruction yields a long answer, so this one stays short). `show-me` is the one-line user-invoked alias, as `grill-me` is for `grilling`.
