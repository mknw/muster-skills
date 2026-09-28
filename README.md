# muster-skills

A portable, stack-agnostic set of [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code) —
procedures an agent loads at the moment a task matches them. This repository is
the single source of truth; the skills are installed globally by symlinking
each directory into `~/.claude/skills/`, which makes them available in every
project on the machine without copying.

```bash
git clone <this repo> ~/Code/muster-skills
for d in ~/Code/muster-skills/*/; do ln -s "$d" ~/.claude/skills/"$(basename "$d")"; done
```

## What belongs here — and what doesn't

Two rules keep the set portable:

- **Procedures, not facts.** A skill is something an agent *does* at a moment —
  a design interview, a diagnosis loop, a merge-conflict procedure — with gates
  and an output contract. Facts about a codebase (commands, paths, model
  tables) belong in that repo's `CLAUDE.md`/`AGENTS.md`, not here.
- **No project references.** Nothing in this set may name a specific project,
  path convention, or stack. Where a skill needs a repo-specific anchor (a
  glossary, an ADR directory, the tightest test loop) it says how to find or
  create one, never where one particular repo keeps it. Project-specific skills
  live in that project's own `.claude/skills/`, prefixed so they can't collide
  with these; a project skill may call one of these, but never the reverse.

## The set

| Skill | Moment it serves |
|---|---|
| `writing-for-agents` | Authoring skills, CLAUDE.md/AGENTS.md, or any doc an agent consumes |
| `grilling` / `grill-me` | Structured interviews that converge a vague idea into a shape |
| `codebase-design` | Deep-module vocabulary for designing or restructuring code |
| `domain-modeling` | Building a project's glossary and decision records |
| `improve-codebase-architecture` | A guided architecture-improvement pass |
| `architecture-report` | A cited, descriptive report on one named layer or topic |
| `intent-driven-development` | Keeping implementation tied to stated intent |
| `diagnosing-bugs` | A diagnosis loop for hard bugs and regressions |
| `loop-design-check` | Sanity-checking agent/feedback loop designs |
| `council` | Four-voice structured disagreement for ambiguous decisions |
| `wizard` | Generating interactive walkthroughs for human-only steps |
| `resolving-merge-conflicts` | In-progress merge/rebase conflict procedure |
| `living-docs-governance` | Keeping long-lived project docs from rotting |
| `agent-architecture-audit` | 12-layer diagnostic for agent/LLM applications |
| `dispatching-work` | Coordination doctrine for fanning work out to multiple agents — specs, lanes, supervision, the review gate; fires on any file-changing task that arrives while coordinating |
| `reviewing-changes` | Three-axis review (originating spec, repo standards, empirical correctness) of changes since a fixed point, size-gated into one-wave and two-wave patterns |
| `init-code-reviewer` | Scaffolding a repo-specific code-reviewer agent — the correctness reviewer the reviewing flow dispatches |
| `self-improve` | Turning owner corrections, countermands, and failures into re-engineered decisions, not prose lessons — a five-step correction loop |

Setup skills (the `init-` prefix) run **once per repo**, not per task: reach for `init-code-reviewer` when a repo joins the reviewing flow, when it has no code-reviewer agent yet, or when the kernel changes and its generated reviewer must be regenerated.

## Inspiration

This set did not appear from nothing. It was assembled by reviewing several
public skill collections, adopting what survived contact with real work and
rewriting it against the rules above:

- **[mattpocock/skills](https://github.com/mattpocock/skills)** (MIT) — the
  primary influence. `writing-for-agents`, `diagnosing-bugs`,
  `codebase-design`, `wizard` and the general skill-authoring discipline
  (small, procedural, gated) trace back here.
- **[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)**
  (MIT) — the code-minimalism ladder ("the best code is none at all", climb
  from YAGNI to the minimum that works) that several skills lean on.
- **[affaan-m/ECC](https://github.com/affaan-m/ECC)** (MIT) — `council` and
  `agent-architecture-audit` originate here, as does the code-reviewer kernel
  that `init-code-reviewer` stamps out for each repo.
- **[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)**
  and **[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)**
  — reviewed sources; ideas rather than text made it in.

Material adapted from the MIT-licensed repositories above is redistributed
under this repository's own MIT license. Full upstream copyright and
permission notices: [NOTICE.md](NOTICE.md).

`dispatching-work` is homegrown: orchestration doctrine distilled from running
multi-agent coordination sessions.
