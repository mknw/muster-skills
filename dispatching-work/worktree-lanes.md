# Worktree lanes — persistent `claude --bg` sessions

Executor mechanics for parallel worktree lanes: each lane is a git worktree
owned by its own persistent Claude Code session, launched with `claude --bg`,
surfacing in **Agent View** (`claude agents`, or left arrow from any active
session) where the user attaches, checks in, and replies. Lane *design* — hot
zones, sole writers, base pre-flight, naming conventions, specs, the review
gate — is the parent skill ([SKILL.md](SKILL.md)); this file is only the
mechanism.

Reach for a different executor when:

- the work is a single task in one worktree — plain foreground `claude`;
- a one-shot job should return its result to *this* conversation — a native
  subagent (it never surfaces in Agent View);
- an orchestration runtime owns the workers — its own skill carries its
  mechanics.

(Agent View sessions are running processes; `.claude/agents/<name>.md` files
define subagent types — distinct features.)

## Set up the lanes

1. **Scope with the user, not the tracker.** The user's framing is the primary
   input; propose reading issue trackers or roadmaps only if scope is unclear,
   and wait for them to accept — the fetch is large and burns context. Ask up
   front for anything unspecified: lane count (typically 2–4 ready,
   prioritized threads — the user's choice) and worktree location (propose
   `../<project>-worktrees/<lane>`, sibling of the cwd, as the default).
2. Inventory `git worktree list` and in-flight branches so new lanes don't
   collide; design the lanes per the parent skill.
3. **Toolchain pre-flight** before writing briefs: probe for `flake.nix` /
   `.tool-versions` / `mise.toml` / `.envrc` / `Makefile`, and surface
   non-obvious setup (devshell entry, required daemons, service composes) in
   `INSTRUCTIONS.md` so lanes don't each rediscover it.
4. `git worktree add <path> -b <branch> <base>` per lane.
5. Append `INSTRUCTIONS.md` and `STATE.md` to the **shared**
   `.git/info/exclude` — one entry covers every worktree, and this private
   scaffolding stays out of the project's tracked ignore list.
6. Write `INSTRUCTIONS.md` per lane (template below).
7. **Prime direnv** if the project has a `.envrc`: run
   `direnv allow <worktree>` for every new worktree *before* launching its
   agent. New worktrees inherit the `.envrc` but not the per-directory trust
   state — unprimed, the lane's first `cd` prints `direnv: error .envrc is
   blocked`, the devshell silently fails to activate, and the agent runs
   against the host toolchain rediscovering the entire env setup.

## Launch — fully detached

The launch must keep lane output out of the coordinator's context: the user
manages lanes via Agent View, and a streamed transcript re-enters this
conversation and explodes token use. For each lane, one foreground Bash
command that returns immediately after detaching:

```bash
cd <worktree>
nohup <toolchain-shell-prefix, e.g. `nix develop --command`> claude --bg \
  "Read INSTRUCTIONS.md and STATE.md (if present), then work the lane. Scope to the first milestone. Commit coherent units locally on the current branch — do not push, do not open PRs." \
  </dev/null >/dev/null 2>&1 &
disown
```

Each piece is load-bearing: `</dev/null >/dev/null 2>&1` keeps stdio out of
the coordinator's shell; `&` plus `disown` (and/or `nohup`) detaches the
process from the shell's lifetime. Launch with a plain foreground Bash call —
the Bash tool's `run_in_background: true` keeps the shell attached and pipes
the lane's transcript back into context on completion, exactly the leak this
avoids.

## Verify, then record

Verify by git state, read directly —

```bash
git -C <worktree> log --stat -N   # N = commits the lane reported
git -C <worktree> status --short
```

— never by tailing the launched session, and never by reading JSONL
transcripts (they overflow context; the lane's Agent View report or
`git log --stat` carries what you need). Then write or update `STATE.md`
(template below) with the **verified** outcome, not the lane's self-summary,
and roll any cross-lane environmental finding (toolchain quirks, CI gotchas)
into the project's own docs so future sessions don't rediscover it.

Resume paths: Agent View to attach a running session and answer inline; or a
fresh foreground `cd <worktree> && claude` that reads `INSTRUCTIONS.md`,
`STATE.md`, and `git log` — works without Agent View.

Cleanup after merge: `git worktree remove <path>` (`--force` only when sure of
the dirty state); `git branch -d <branch>` is safe — it refuses unmerged
branches, so get confirmation before any `-D`.

## `INSTRUCTIONS.md` template (durable lane brief — written once, git-ignored)

```markdown
# Worktree: <Lane name>

> Local scaffolding — **git-ignored, do not commit.** Branch: `<branch>`.

## Goal
<One paragraph: what shipping this lane achieves.>

## Issues, in order
1. **#NN** — <one-line scope; what unblocks the next>
2. ...

## Files / regions you own
- `<path>` — <brief description>
- ...

## Conflict boundaries (other lanes run in parallel)
- Do NOT edit `<path>` — `<other lane>` owns it for `<reason>`.
- If you find you need to touch a forbidden file, STOP and surface the decision.

## Reference
- <design doc> · <ROADMAP section> · <related issues>

## Commands
- Toolchain entry: `<nix develop / direnv allow / etc.>`
- Dev / test / type-check (project-specific).

## Commit / push discipline
Commit coherent units on the current branch. Do NOT push and do NOT open PRs — leave that for human review.
```

## `STATE.md` template (volatile resume brief — updated each run, git-ignored)

```markdown
# STATE.md — <Lane name>

> Local scaffolding — **git-ignored, do not commit.** Resume brief from the previous run.

**Branch:** `<branch>` (already checked out)

## What shipped (previous run)
- **`<sha>`** — <commit subject>
  - `<file>` — <key facts>
- Tests: **<count>** passing. Type-check baseline state.

## Next milestone
<Concrete next step, with exact files/work to start on.>

## Open notes / decisions
- <anything surfaced last run that needs the user or affects the next step>

## Hard boundaries
(Repeat from `INSTRUCTIONS.md`, with any updates — e.g., the sole-writer set grew.)

## How to pick up
- Toolchain entry: `<...>` · install / pre-commit (project-specific).
- Read: `INSTRUCTIONS.md`, `<design doc>`.
- Do NOT push or open PRs.
```
