---
name: dispatching-work
description: Coordination doctrine for fanning work out to multiple agents. Use when dispatching or supervising workers, splitting a task across subagents or worktree lanes, deciding which agent type or model should handle a piece of work, or running a coordinator loop over worker messages.
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
| Verification, decisions, replying to worker questions, merges | Inline — the coordinator itself |

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
- **Verify results by git state, not the worker's self-report**: the claimed
  commits exist, the tree is clean, CI is green.

## Land the results

- Green CI is necessary, never sufficient. A worker's PR ships with tests
  written by its own author — self-attested green is not a review. Before
  merging, dispatch an independent reviewer (capable model, generous effort;
  use the repo's review procedure if it has one); on findings, iterate with
  the author or a fix dispatch; merge only on positive review.
- Reviewed + green CI → merge.
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
