---
name: visualizing
description: Pick the most compact visual form that carries one question (control-flow diagram, pseudocode, call stack, state or sequence diagram, types, file layout, diff) in place of prose. Use when the user says "show me" or finds a message too long, when presenting a design or a large diff, or when another skill needs a visual for a section.
---

# Visualizing

Replace prose with the **most compact** form that carries **one question**. A reader takes in structure (indentation, branches, columns, position) faster than sentences, so the reader's question picks the form, and the shape of the material does not.

Three moments call it. A message the reader finds too long ("show me") is restated as a form. A design is agreed as shapes (types, signatures, call stacks) before code exists. A large diff is mapped as `+`/`−` on a structure before review. A skill that builds pages calls it once per section.

## Process

### 1. Pin the question

Write the reader's question in one sentence, with what they will do with the answer ("which branch rejects it, so I know where to move the limit?"). Two questions get two visuals.

Done when: the sentence is a question and names the decision or action it serves.

### 2. Pick the form

Look the question up in [FORMS.md](FORMS.md) (question to form) and take the **lightest** row that carries it. Weight ascends: types and signatures, pseudocode, call stack, tree or layout, diff, diagram (flow, sequence, state), table, HTML visual, prose. "What happens, and where does it branch" is **control flow**: draw pseudocode for the exact predicates, a flow diagram for the shape, and both when the reader will predict outcomes from them.

Done when: each question has one form, and any form above a table carries one clause saying why the lighter ones fall short.

### 3. Draw it

**Elide** everything the question does not need and mark the elision (`…`). Mark the **answer point** (the deciding branch, the changed line, the failure path) so the eye lands there first. Label with the reader's words; name code with its real names and `path:line`. A change is `+`/`−` on the unchanged structure, a single picture in place of a before/after pair.

Done when: removing any remaining node or line would lose part of the answer, and the answer point is marked.

### 4. Ground it

Every name, path and number comes from source opened in this session; the model's memory of a codebase is untrusted. Search the source for each name in the visual, and cite where the reader can open it.

Done when: each name resolves, and each number states where it is set.

### 5. Check it renders

Chat and terminal carry the text forms; a diagram language (Mermaid) goes only where the surface renders it, with the text equivalent everywhere else. A page is screenshot at phone and desktop width in both colour schemes. Forms that text cannot carry (mockups, gauges, matrices) go on a page; a page skill's own format file holds the markup.

Done when: the visual was seen the way the reader will see it.

## Reference cards

A rule, algorithm or glossary the reader will come back to goes in its short form (pseudocode, a table) as its own section or page, kept apart from the explanation that introduced it. Explanations are read once; cards are returned to.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-30 — v1.** Prompted by the owner's observation that `explain-mechanism` pages lacked variety: control flow and pseudocode were what they expected almost every time. The form-choice doctrine had lived in two skills (`explain-mechanism` and `syncing-board`); it now lives here and both point to it. Shaped by two published skills, rewritten here with no text adapted: HumanLayer's `show-me` (the lightest form per question, elided, with `+`/`−` for change) and Matt Pocock's `teach` (grounded in cited sources; reference cards kept apart from lessons). `show-me` stays as a one-line user-invoked alias, the same pattern as `grill-me` over `grilling`.
