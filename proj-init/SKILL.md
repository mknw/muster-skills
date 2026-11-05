---
name: proj-init
description: One setup pass over a newly started project — run the project-init
  skills in order (wft lane setup, test pyramid, code reviewer), skipping any
  step the repo already has. Use this when a new project or repository is being
  started or onboarded for agent work, or when the user asks to set a project
  up, initialize it, or get it ready for lanes and review.
---

# Project init

One pass, three skills, fixed order. Run each to its own completion criterion
before starting the next:

1. `init-wft-proj` — the repo's `wft.yaml`: profiles, seed semantics, setup,
   placement. Lane setup exists, so later steps' state can be provisioned
   inside a fresh lane workspace.
2. `init-test-pyramid` — the repo's test layers: named suites, one command
   each, CI placement, per-suite test state.
3. `init-code-reviewer` — the repo's code-reviewer agent, which names the test
   command from step 2 as its empirical loop.

The order is load-bearing: lane setup first, because the pyramid's per-suite
test state may need to be reproducible in a new lane workspace; the pyramid
before the reviewer, because the generated reviewer's empirical loop points at
the suite commands the pyramid just settled.

## For each step, in order

1. **Check whether the step is already done** before invoking anything:
   - *wft setup*: a committed `wft.yaml` at the repo root. If it exists, skip —
     unless it looks stale (the toolchain or the lane workflow changed), in
     which case re-run `init-wft-proj` and let it validate or repair in place.
   - *test pyramid*: an existing layer map, found the way `init-test-pyramid`
     finds one — a pointer in the repo's `CLAUDE.md` / `AGENTS.md`, a
     `*-test-pyramid` skill, or a testing doc. If one exists, skip — that
     skill's own procedure audits an existing map and amends it, so a re-run is
     only warranted when the owner asks for an audit.
   - *code reviewer*: the code-reviewer agent file the `init-code-reviewer`
     skill generates, present in the repo's agent directory. If it exists,
     skip — unless the reviewer kernel changed, in which case that skill's
     re-initialize rule applies.
2. **Run the step** by invoking the skill and following its procedure to its
   completion criterion.
3. **Record one line per step**: ran, skipped (why), or re-run (why).

A skipped step is a claim, not an assumption — name the artifact you found
that made it done.

## Report the pass

At the end, report: which steps ran, which were skipped and on what evidence,
and the judgment calls still open for the owner — the env keys each profile is
granted, the VM placement decisions, and any model pin for the reviewer.

## Why these skills are reachable

Every skill this one runs is model-invoked (each carries a description), which
is what makes it reachable from here — a skill can only reach a model-invoked
one. `proj-init` is model-invoked for the same family of reasons: it has to
fire at the new-project moment without waiting to be remembered, and
model-invocation adds agent discovery without removing the human's ability to
type the name.
