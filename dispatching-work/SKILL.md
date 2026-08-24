---
name: dispatching-work
description: Coordination doctrine for fanning work out to multiple agents — how to split the work, which executor and model take each piece, the task spec, supervision, and the review gate before merge. Use when dispatching or supervising workers, splitting a task across subagents or parallel worktree lanes, spinning up persistent per-worktree `claude --bg` sessions (INSTRUCTIONS.md / STATE.md lane briefs), or deciding which agent type or model should handle a piece of work. For Orca's command surface and message mechanics, use `orchestration`.
---

# Dispatching Work

Doctrine for the coordinator role: choosing the executor, writing the task
spec, supervising without waste, and landing the results. It is
runtime-agnostic — where an orchestration runtime (e.g. Orca) is present, get
its exact command surface from the runtime itself (`orca skills get
orchestration`); never encode CLI flags here or from memory.

## Choose the executor

The coordinator's context and attention are the scarce resource. Delegate even
small chores — inline work is for what only the coordinator can do.

| Work | Executor |
|---|---|
| Long-running implementation that needs its own branch/worktree, PR provenance, and supervision | Orchestration-runtime worker (dispatched task, lifecycle messages) |
| Short one-off: conflict resolution, format fixes, board updates, batch renames, research lookups | Native subagent (background task tool) |
| Reviewing a worker's PR before merge | Independent worker with more headroom than the author — never the author, never the coordinator |
| Parallel lanes the user supervises personally in Agent View, resumable across runs | Persistent per-worktree `claude --bg` session — launch mechanics and INSTRUCTIONS.md / STATE.md lane-brief templates: [worktree-lanes.md](worktree-lanes.md) |
| Verifying a worker's self-report, decisions, replying to asks, merges | Inline — the coordinator itself |

Model selection: a capable model for judgment work (design, review,
implementation); a cheaper model for mechanical work. State the model and
effort explicitly at dispatch; don't rely on defaults you haven't checked.

## Write the task spec

The spec is the worker's whole world — it will not infer your intent. Skeleton:

1. **Objective and source of truth.** If an issue exists, the issue body IS the
   spec — point at it rather than paraphrasing it.
2. **Reality-check clause** when the issue may be stale: "first establish what
   already exists on main; if the work is already done or not needed, report
   that verdict instead of building."
3. **Gates**: the exact quality bars (type-check, tests, coverage floors, lint,
   build, CI green) and any house rules (e.g. no attribution trailers).
4. **Parallel-lane warnings**: name the other in-flight lanes that touch nearby
   files, and the merge order (see below).
5. **Communication contract** — append verbatim:

   > COMMUNICATION: do NOT send periodic heartbeats. Send 'ask' if blocked
   > (ONE consolidated ask, not a drip), 'escalation' if coordinator
   > intervention is needed, and exactly one final 'worker_done' when finished
   > (include outcome and the PR URL).

   Periodic pings waste tokens twice: the worker's call, and the coordinator
   turn each unread message triggers.

## Design the lanes

- **Hot-zone consolidation**: identify file regions multiple tasks touch and
  give each such region ONE sole-writer lane; others wait or warn.
- **Merge order for cross-cutting changes**: the wide mechanical change (a
  rename, a format sweep) merges FIRST and stays a pure sweep — no
  opportunistic refactors; every other lane rebases over it before opening its
  PR, and its spec says so.
- **Pre-flight the base branch**: lanes inherit only committed state; commit or
  copy in what they need before dispatch.
- **Match the repo's worktree conventions** (existing folder and branch naming)
  rather than inventing new ones.
- **Don't shard the backlog**: lane count = genuinely parallel threads, not
  issue count.

## Supervise

- **Verify every dispatch actually started.** Read the worker's terminal after
  dispatch: a pasted-but-unsubmitted prompt looks dispatched and sits idle for
  hours. If the prompt is sitting in the input box, submit it and re-verify.
- **Wait typed, not polled.** Block on the message types that require action
  (worker_done, escalation, question) in a re-arming loop; filter heartbeats
  and status noise out of the wake condition.
- **Process whole deliveries.** Acknowledge each batch after handling it;
  an unacknowledged delivery replays and re-wakes you.
- **Answer asks decisively.** Workers send one consolidated question; reply
  with a decision and rationale, not options back. If the decision is genuinely
  the user's, surface it — don't guess.
- **Heartbeats and terminal activity mean alive, not done.** Never stop or
  release a worker for mere idleness. On release, a "retained / user-takeover"
  result is normal (the user touched that terminal) — the dispatch is still
  settled.
- **Re-engage a finished worker with a fresh dispatch.** A settled dispatch is
  closed to lifecycle messages: prompt its terminal directly and the work still
  happens, but its `worker_done` is rejected and the report reaches you only as
  loose mail. Reuse the terminal (keeping its context) *through* a new task.
- **Verify results by git state, not the worker's self-report**: the claimed
  commits exist, the tree is clean, CI is green.

## Land the results

**The review gate.** Nothing merges until an independent reviewer returns a
positive verdict. Two things feel like review and are not:

- **Green CI is self-attestation.** A worker's PR ships with tests written by
  its own author, so the suite proves the author's beliefs about the code, not
  the code.
- **Coordinator inspection shares the author's framing** of what matters, and
  the coordinator is the party that wants the PR to land. Verifying a
  self-report is the coordinator's job; reviewing is a different agent's.

The reviewer needs more **headroom** than the author: a top-tier model at a
higher effort tier (authors at `high` → reviewer Opus 5 at `xhigh`). Escalate
with risk: higher effort for security or hardening changes; the strongest
available model (Fable-tier) for critical infrastructure or high-risk
vulnerabilities. Use the repo's review procedure/skill if it has one.

**Who commissions, and until when.** Reviews are COORDINATOR-commissioned,
never author-commissioned — an author picking its own reviewer is a weaker
guarantee. Medium and large PRs always get one; for small PRs, ask the user
(they may prefer to review personally). Whenever changes are applied
post-review, commission a **new** reviewer for the deltas and repeat **until
convergence** — a review that returns nothing to apply. (Evidence the loop
earns its cost: a round-2 reviewer once caught that a round-1 security fix
was under-scoped — a 15-second ReDoS still reachable from a shipped path.)
Merge on converged review plus green CI.

**The record lives on the PR.** The reviewer posts its outcome as a PR
comment; whoever applies fixes posts what they changed, the same way.
Orchestration messages evaporate on acknowledgement — the PR timeline is the
durable audit trail. Keep reports high-level, descriptive, short (~500
characters), with two escape hatches: HIGH-criticality findings get the
detail they need to act on, and a long report rides in a collapsed
`<details>` block under the short summary in the same comment — scannable
timeline, evidence preserved.

**Reviewing a test PR**, the decisive question is whether each test is
*discriminating*: mutate the source and confirm the test fails. A test that
passes whether or not the code is correct is worse than no test — it
manufactures a coverage number and the safety feeling that comes with it. Hunt
**coverage theatre**: asserting that a mock was called rather than that an
observable outcome happened. Have the verdict separate *verified by mutation*
from *looks right by reading*.

**Green on the PR's current head SHA**, not on an older commit. A workflow that
deliberately omits the `synchronize` trigger leaves a stale green on any PR
updated since its last run. Where required status checks cannot be enforced at
all — a private repo on a free plan 403s on both branch protection and rulesets
— say so plainly and document the command that triggers a run: a branch that
merely looks protected is the more dangerous state.

**Merged without review already?** Retro-review the merged span as one unit
rather than each PR alone; reviewing them together catches the interactions that
per-PR review misses.

**Merge mechanics.**

- **Stack on `main`, not on a sibling branch.** Squash-merging a PR and deleting
  its branch auto-closes every PR based on that branch, and GitHub cannot reopen
  or retarget a closed PR whose base is gone. The work survives only as the
  branch, to be reopened as a new PR.
- Stale base ("head branch is not up to date") → update the branch, watch the
  checks, merge on green — as one backgrounded sequence, not a poll loop.
- Merge conflicts → delegate resolution to a subagent with the repo's
  merge-conflict procedure; the coordinator never grinds conflicts inline.
- After a cross-cutting merge, complete what the VCS can't: untracked files
  (env files, build artifacts, generated code) don't follow a `git mv` — the
  sweep's PR body must carry the migration steps, and the coordinator runs them
  in the live checkout.
- Close the loop: release the worker, acknowledge the final delivery, and
  update the tracking surface (board, issue) — or delegate that update.
