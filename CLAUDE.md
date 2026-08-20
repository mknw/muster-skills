# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A portable, stack-agnostic collection of Claude Code skills. Each top-level directory is one skill: a `SKILL.md` with YAML frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), plus optional supporting files (reference docs, script templates) that the skill body links to. There is no build, lint, or test tooling — the deliverables are the markdown files themselves.

Skills are installed by symlinking each directory into `~/.claude/skills/`; this repo is the single source of truth, so edits here take effect globally on the machine.

## Hard rules for every skill (from README.md)

- **Procedures, not facts.** A skill describes something an agent *does* — a loop, an interview, a gated procedure with an output contract. Facts about a specific codebase (commands, paths, model tables) belong in that repo's own CLAUDE.md/AGENTS.md, never here.
- **No project references.** Nothing may name a specific project, path convention, or stack. Where a skill needs a repo-specific anchor (a glossary, ADR directory, test loop), it must say how to *find or create* one, never where a particular repo keeps it. Project skills may call these skills; these skills must never reference a project skill.

## Authoring standard

`writing-for-agents/SKILL.md` and `writing-for-agents/SKILL-MECHANICS.md` are the house style for everything in this repo — read them before creating or editing any skill. Key concepts they define:

- **Context pointers**: a skill's `description` is an always-loaded pointer whose wording (leading trigger words, one trigger per distinct branch) decides whether the skill fires. Weak pointer wording is a variance bug.
- **The two loads**: context load (always-loaded tokens) vs. cognitive load (what the human must remember). Model-invoked skills (with a description) spend context load for agent discoverability; user-invoked skills (`disable-model-invocation: true`, invoked only by typing the name) spend cognitive load instead.
- **Alias pattern**: a user-invoked skill can be a one-line alias that calls a model-invoked one (see `grill-me` → `grilling`).
- Only model-invoked skills can be reached by other skills; shared reference needed by two user-invoked skills must live in a plain file outside the skill system.

## Provenance

Several skills are adapted from MIT-licensed upstream repos. If you adapt more external material, update `NOTICE.md` with the upstream copyright and permission notice; homegrown skills need no entry. The README's skill table and inspiration section should stay in sync when skills are added, renamed, or removed.
