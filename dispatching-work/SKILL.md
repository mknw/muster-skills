---
name: dispatching-work
description: Dispatch and supervise agents, choose executors and models, or route a delivery request while coordinating. Resolve owner-defined general-coordinator and operational-PM roles before dispatch. Covers task briefs, lane ownership, recovery, independent review and landing; includes Herdr-native control and the persistent-worktree fallback when no runtime is available.
---

# Dispatching Work

**Resolve the role first.** Follow the owner's current assignment. When a
separate general coordinator and operational PM are assigned, the general
coordinator owns global priorities, alternatives, owner decisions and selected
milestones; the PM owns the delivery loop: dispatch, waits, evidence, failure
recovery, tracking, review gates and cleanup. Implementation belongs to authors;
review belongs to independent reviewers commissioned by the PM. An assigned
worker completes its lane and reports to that PM, rather than creating another
PM. Bounded checks explicitly allowed by the owner remain allowed; they do not
transfer the operational loop. Failed PM placement is a concrete blocker for the
general coordinator to surface, not an implicit role transfer.

For the operational coordinator/PM, this doctrine covers choosing executors,
supervising and landing results. Before editing or dispatching a newly arrived
delivery request, resolve the role and executor. Obtain the runtime's exact
commands and capabilities from its installed schema and official version-matched
docs. For Herdr, read [herdr-native.md](herdr-native.md) before controlling
agents, reconnecting or preparing owner entry. For deploying these skills to
coordinators or agents, read [skill-release.md](skill-release.md). Runtime
mechanics implement this doctrine; they do not define task acceptance.

## Choose the executor

The coordinator's context and attention are the scarce resource. Delegate even
small chores — inline work is for what only the coordinator can do.

| Work | Executor |
|---|---|
| Long-running implementation that needs its own branch/worktree, PR provenance, and supervision | Orchestration-runtime worker (dispatched task, lifecycle messages) |
| Short one-off: conflict resolution, format fixes, board updates, batch renames, research lookups | Native subagent (background task tool) |
| Reviewing a worker's PR before merge | Independent worker with more headroom than the author — never the author, never the coordinator — commissioned with the review's classification and models (see The review gate) |
| Any of the above, in an environment with **no orchestration runtime** | Persistent per-worktree `claude --bg` session — the fallback: [worktree-lanes.md](worktree-lanes.md) carries its launch mechanics and the INSTRUCTIONS.md / STATE.md lane briefs |
| Verifying a worker's self-report, operational decisions, replying to asks, merges | Inline — the operational coordinator/PM within its assigned authority |

Routing authority: where the owner has ruled on how lanes are dispatched (for example, "lanes go through the orchestration runtime"), that ruling overrides this table until the owner retracts it. When a row's precondition is ambiguous or a runtime's capabilities are in doubt, surface the choice with evidence instead of resolving it silently — and verify capability claims against the runtime's registry of record (official docs), never against examples in help text or skills.

Model selection: a capable model for judgment work (design, review,
implementation); a cheaper model for mechanical work. State the model and
effort explicitly at dispatch; don't rely on defaults you haven't checked.

**Re-run, not grandfathered.** The executor decision expires when the task
changes shape. Three tells: a capability you didn't plan for; a file or
conflict count past the one you sized; a "while I'm here" addition. On any
tell, re-run the sizing with current facts — write the from-scratch plan as if
nothing were underway, diff it against the current state, then salvage or
discard. Context you already hold is an argument for **writing the handoff
spec**, since inline coordinator work grows past the review gate unreviewed
(see The review gate).

When this trip-wire fires — or a second same-class worker failure lands in one
run — write the **incident extract** and dispatch a `self-improve` subagent
(independent context) to run its loop on it. The extract contract lives in
that skill. Writing the extract is the stop-and-name step: it comes before
recovery, not after.

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
5. **Execution boundary**: identify coordinator, model-agent and workload
   placement; admitted environment, egress mode and external enforcement;
   source/attempt identity; and the scoped helper authority. A worktree or pane
   alone provides no network boundary. Keep model inference/control outside an
   isolated workload with a restricted execution bridge, or report the inspected
   dependency. Carry read-only repository exclusions into every worker, review
   and operator brief: use immutable API reads/exports and prohibit checkout,
   index, worktree, status-refresh and remote writes for those repositories.
6. **Communication contract** — bind the following outcomes to the installed
   runtime or project's verified durable task/result adapter. Use its exact
   commands in the brief; the event names below are labels, not portable CLI:

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

- **Dispatch into a finished environment.** Runtimes bootstrap new
  workspaces (dependency installs, env approval, codegen — often tens of
  seconds), and a prompt arriving mid-bootstrap stalls or fails without a
  diagnosable error. Confirm the executor's bootstrap has completed before
  dispatching: wait out a fresh workspace's setup phase once; reusing a warm
  workspace avoids the race entirely.
- **Diagnose from full output.** Before declaring any failure from your own
  observation, re-read the FULL output — truncated listings and filtered
  greps hide live state, and a false failure diagnosis costs more than the
  wait would have. A status name on a task row (queued, accepted, dispatched)
  is a receipt, not a verdict.
- **Verify every dispatch actually started.** Use the native start/readiness
  result and observe task-specific activity or a durable receipt. Inspect only
  the assigned worker's permitted output when necessary; preserve private user
  sessions. A timeout after submission leaves execution uncertain: reconcile
  before retrying so the same work is not submitted twice.
- **Wait on actionable state.** Use the runtime's native lifecycle waits or
  events and the durable task/result channel for completion, blockers and
  questions. A lifecycle transition is a wake to inspect task evidence, not a
  task verdict. Re-arm waits after processing and reconcile after disconnect.
- **One retry, then surface.** On a failure signal, retry once calmly, then
  put the failure in front of the owner with the evidence.
- **Process whole deliveries.** Where the task channel has consuming batches
  and acknowledgement, handle the full batch before acknowledging. For a
  non-durable event stream, reconcile authoritative state and durable receipts
  after reconnect; do not assume replay or invent an acknowledgement API.
- **Answer asks decisively.** Workers send one consolidated question; reply
  with a decision and rationale, not options back. If the decision is genuinely
  the user's, surface it — don't guess.
- **Heartbeats and terminal activity mean alive, not done.** Never stop or
  release a worker for mere idleness. On release, a "retained / user-takeover"
  result, where supported, preserves the user's terminal after settlement.
  Clean up only positively identified resources owned by this attempt.
- **Re-engage a finished worker with a fresh dispatch.** A settled dispatch is
  closed to lifecycle messages: prompt its terminal directly and the work still
  happens without a current task identity. Reuse the terminal (keeping its
  context) through a new task/attempt and verify its current occupant first.
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

**Classify before dispatching.** The review commission carries the review's
classification, so the reviewer executes rather than re-classifies. Classify
the PR with the review procedure's pattern table — size from
`gh pr diff --stat`, risk class from the diff's paths (any risk-class path
forces the large pattern regardless of size — the table's list) — and state
in the dispatch: the pattern
(one wave, or the two-wave gate), the reviewer's model, and each sub-agent's
model. Capable model for judgment work (the reviewer, and the empirical
correctness agent whenever risk-class paths are in the diff); cheaper model
for the mechanical reading passes.

**The verdict and the merge policy are different hands.** The reviewer
returns `APPROVE` / `APPROVE-with-edits` / `BLOCK` and nothing about merge
intent. Whether APPROVE-with-edits lands without another round is coordinator
policy, stated in the pattern's terms: reviews run under the large pattern
(two waves) always converge — the edits are applied and the deltas
re-reviewed; under the small pattern, ask the user, who may prefer to apply
the edits personally.

**Harvest artifacts before release.** A correctness review leaves proposed
test edits in the reviewer's workspace worktree, named in its report.
Harvest that path **before** releasing or archiving the reviewer's workspace,
and route it to the executor or author, who applies and commits the tests
under its own provenance — even when tests are the only delta. A path lost to
workspace release is evidence lost.

**Who commissions, and until when.** Reviews are COORDINATOR-commissioned,
never author-commissioned — an author picking its own reviewer is a weaker
guarantee. Reviews under the large pattern always get one; under the small
pattern, ask the user (they may prefer to review personally). Whenever changes are applied
post-review, commission a **new** reviewer for the deltas and repeat **until
convergence** — a full review in which every commissioned axis ran and
returned clean. A review that exits early (spec fails wholesale before
correctness runs) is **exited, not converged**; the next round runs the full
pattern on the deltas. (Evidence the loop earns its cost: a round-2 reviewer
once caught that a round-1 security fix was under-scoped — a 15-second
ReDoS still reachable from a shipped path.) Merge on converged review plus
green CI.

**The record lives on the PR.** The reviewer posts its outcome as a PR
comment; whoever applies fixes posts what they changed, the same way.
Preserve the review in the PR timeline as a durable audit trail even when a
runtime's task messages are transient. Keep reports high-level, descriptive, short (~500
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
