---
name: architecture-report
description: Render the architecture of one user-named layer, subsystem, or topic as a verified report — inventory, structure, data/control flow, mermaid diagrams, every claim cited file:line. Use when the user asks to report, render, diagram, or document the architecture of X, or wants a written explanation of how a named layer is put together. Descriptive only — improvement and refactoring asks belong to improve-codebase-architecture.
---

# Architecture Report

Render the architecture of **one named layer or topic** — "the privacy enforcement layer", "the event pipeline", "everything that touches Redis" — as a report. The deliverable is the report and nothing else: describe what is, in source-verified terms. Code stays untouched; opinions stay out.

This skill shares its analysis machinery with `improve-codebase-architecture` but answers a different question — **"how is this put together?"**, not "what should change?". When the user wants improvements, deepenings, or refactors, hand over to that skill instead.

- Call the Skill tool with "codebase-design" for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and use those terms exactly — no drift into "component," "service," "API," or "boundary."
- Read the project's domain glossary (`GLOSSARY.md`) and any ADRs (`docs/adr/`) touching the topic — they give the report its domain nouns and record why things are shaped the way they are. If either is missing, say so and carry on.

## Process

### 1. Pin the scope

The user named the layer or topic; that name is the boundary. Restate it as one line — what is inside, what is out — before exploring, and if the name could honestly cover two different slices, ask which one before spending a scan on the wrong one.

Everything outside the boundary appears in the report only as a **touchpoint**: a named edge where the topic meets the rest of the system (who calls in, what it calls out to), one line each. A touchpoint's internals get no section, no diagram, no inventory row. Scope creep is the primary failure mode of this skill — a report on "the event pipeline" that explains the whole app has failed even if every sentence is true.

### 2. Explore

Spawn a sub-agent to walk everything inside the boundary (explore directly when the scope is a handful of files). The exploration is done when it can answer, with file and line in hand:

- **Inventory** — every file and module that is part of the topic, and each one's role.
- **Structure** — which modules exist, where each seam sits, which adapters satisfy which interface.
- **Control flow** — the real path of a request/event/call through the topic, entry to exit, traced end to end in source — not inferred from names.
- **Data flow** — what data crosses each seam, where it is stored, where it changes shape.
- **Touchpoints** — every edge crossing the boundary, in both directions.

Registered-but-never-called, dead branches, config that no code reads: report what the source shows, in neutral terms.

### 3. Verify

Every claim in the report is read in source before it is written, and carries a `path/to/file.ts:123` citation. A claim you cannot pin to a line does not go in — either dig until it pins, or leave it out. "The retry lives in the client wrapper, probably" is the failure mode; the citation discipline is the cure. Prior docs, ADRs, and code comments are leads to verify, never citations themselves — code drifts from all three.

### 4. Write the report

Follow [REPORT-FORMAT.md](REPORT-FORMAT.md): executive summary table first, then inventory, structure, flows, touchpoints — with mermaid diagrams wherever the mechanism is graph-shaped. The report describes; it ends when the description does. Append an explicitly-marked **Observations** section only when the user asked for one — the default report carries no recommendations, no "could be improved", no severity language.

### 5. Deliver

The user's ask decides the medium:

- **File** — write markdown where they said; unstated, use the OS temp dir (`$TMPDIR`, falling back to `/tmp`, `%TEMP%` on Windows) as `<tmpdir>/architecture-report-<topic>-<timestamp>.md` so nothing lands in the repo uninvited, and tell them the absolute path.
- **Issue or PR comment** — post via `gh`, on the issue/PR they named.
- **Artifact** — publish via the environment's artifact mechanism when one exists and they asked for a shareable page.

When they named no medium, write the temp file, give the path, and offer the other two in one line.
