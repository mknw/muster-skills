---
name: init-code-reviewer
description: Set up a repo-specific code-reviewer agent — the correctness reviewer that the reviewing-changes flow dispatches as its Correctness axis. Use when a repository has no code-reviewer agent yet, or is being onboarded to the reviewing flow.
---

Generates `.claude/agents/code-reviewer.md` for the current repo: the
exec-capable agent that `reviewing-changes` dispatches as its wave-2
Correctness axis (and that stands alone for quick correctness checks). The
generated agent is repo-specific by design — it lives in that repo; this
skill never names a stack, it discovers one.

The generated agent has three layers, and only the third is repo-specific:

1. **The kernel** — [`kernel.md`](kernel.md) in this folder, copied verbatim
   into each generated agent, never hand-forked (the kernel itself is this
   repo's adaptation of upstream material — provenance in the repo's
   NOTICE.md):
   correctness remit, confidence gate, pre-report gate, HIGH/CRITICAL-proof
   rule, false-positive skip list, and the empirical loop (run the suite,
   write discriminating tests, verify under mutation). The kernel is the
   single source — never fork it by hand; when the kernel changes,
   re-initialize and re-apply the stack section rather than editing the
   generated file in place.
2. **The frontmatter** — name `code-reviewer`, a description that fires on
   correctness review, tools that include command execution (read, search,
   and shell — the empirical loop cannot run in a read-only agent), and a
   model line only if the owner pins one; otherwise leave it unset and let
   the dispatching coordinator state the model per review (its risk-scaled
   rule lives in `dispatching-work`).
3. **The stack section** — generated from the repo, appended after the
   kernel: language and framework, the test command, the lint/type-check
   commands, error-handling and concurrency idioms in actual use, and a
   pointer instructing the agent to read the repo's `CLAUDE.md` / `AGENTS.md`
   conventions at review time rather than hardcoding them.

## Procedure

### 1. Introspect the repo — never assume

Read, don't guess: file extensions and package manifests for the language
and framework; the test runner and its invocation from config files and
scripts; the lint/format/type-check commands; how the codebase actually
handles errors, validation, and concurrency (read a few representative
modules); anything the repo's `CLAUDE.md` / `AGENTS.md` already states about
review expectations. If the repo has a `docs/reviewing.md`, honor its
overrides for what the reviewer should check.

Completion criterion: the language, test command, and error-handling idiom
are each stated from evidence you read, not assumption.

### 2. Decide the two open knobs with the owner

- **Model pin**: pin a model in the frontmatter, or leave it to dispatch
  time. Default to leaving it unset unless the owner has a standing choice.
- **Silent-failure hunting**: if the owner wants it, append the optional
  hunt-targets block from the kernel's appendix (empty catch blocks,
  swallowed errors, dangerous fallbacks, missing propagation). Optional —
  some owners prefer a dedicated failure-hunting agent instead.

Completion criterion: both knobs have explicit decisions — model pinned or
explicitly left to dispatch, silent-failure fold-in taken or declined.

### 3. Generate the agent

Write `.claude/agents/code-reviewer.md`:

- a provenance comment naming the kernel's upstream (`affaan-m/ECC`, MIT) and
  where this repo records third-party notices;
- frontmatter per layer 2 above;
- the kernel verbatim;
- the `## This repo's stack` section from step 1 — facts only, no taste;
- the conventions pointer per layer 3.

Completion criterion: the file exists, its frontmatter parses, and every
command it names (test, lint, type-check) has been run at least once to prove
it works.

### 4. Register provenance

The kernel derives from MIT-licensed upstream material. Record the
attribution in whatever mechanism the repo uses (a NOTICE file, a
PROVENANCE note, the skills' provenance comment) — a vendored agent file is a
substantial portion, and the notice must travel with it.

Completion criterion: the attribution is findable — search the repo's
provenance mechanism and confirm the upstream name appears.

## What this skill must not do

- Name a language, framework, or tool — discovery produces those, not this
  file.
- Bake repo facts into the kernel — facts live in the generated stack
  section, so a kernel update never clobbers them and a repo refresh never
  touches the kernel.
- Let the generated agent drift — if the repo's stack changes, regenerate the
  stack section; if the kernel changes, re-copy the kernel. One file, two
  clearly-separated regions, one owner each.
