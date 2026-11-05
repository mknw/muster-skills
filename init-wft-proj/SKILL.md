---
name: init-wft-proj
description: >-
  Applies only to wft. Draft, validate or repair a repository's wft.yaml so new
  wft lanes bootstrap themselves — profiles, seed semantics, setup commands,
  host/VM placement and stacks. Use this whenever the user mentions wft.yaml,
  wft lane setup or profiles, initializing or onboarding a repo for wft lanes,
  or complains that a fresh lane workspace is missing its .env / node_modules /
  test database / tool config, that a lane received a secret it should not
  hold, or that lane setup has to be redone by hand every time — even if they
  never name the file. Also use it before hand-editing an existing wft.yaml,
  because unknown and duplicate keys are refused wholesale, not ignored, and
  because deciding which env keys a profile is granted is a judgment call this
  skill exists to make.
---

# Wft project init

A wft lane workspace starts as a **clean git checkout plus a policy**. Everything
gitignored is therefore absent: no `.env`, no `node_modules`, no build cache, no
tool config. The repo looks complete and isn't, which is why the first command a
fresh lane runs so often fails.

`wft.yaml` at the repo root fixes this once, for everyone, in version control.
One file, several setups: `profiles` name them, because one repo genuinely needs
more than one kind of lane.

The division of labour is fixed: **`wft init` does the mechanical part** — it
writes and validates the file, seeds a workspace, runs setup. **This skill makes
the judgment calls** the CLI cannot make: which env keys each profile is
granted, and which work needs a VM.

Two rules bind everything below, stated plainly:

- **Never copy a secret file.** A `seed.require` file stays in the primary
  checkout and is never copied whole — not into the lane, not into any archive.
  A lane receives only the env keys its profile grants, read from that file at
  lane-creation time.
- **Never print a secret value.** Key names only, everywhere: `wft.yaml` is
  committed, and so are receipts and reports. Names of granted keys travel;
  values never do.

## 1. Resolve the CLI first

1. `wft` on `PATH` — use it for everything mechanical (`wft init`, `wft doctor`,
   `wft lane add`).
2. If the CLI is not installed yet, **draft the file anyway**: `wft.yaml` is
   committed data, so writing it by hand from the schema is safe and useful.
   Say plainly that the CLI is missing and that validation below was done by
   checklist, not by the loader. Do not invent CLI flags; write the file, not
   the tool.
3. `wft init --from orca.yaml` imports an existing Orca setup when both exist.
   Run it, then re-judge its output: the import maps mechanics, never judgment
   calls — the grant lists and placement decisions are still yours.

## 2. Inventory what a fresh lane is missing

Don't guess from the stack — ask git, then look at what's actually on disk:

```bash
git -C <repo> ls-files --others --ignored --exclude-standard --directory | head -50
du -sh <each candidate> 2>/dev/null | sort -h | tail
```

Sort each entry into one of four buckets. This is the whole design decision:

| Bucket | Mechanism | Use when |
|---|---|---|
| **Derive** | `setup` | It can be rebuilt from tracked files — installing deps, codegen, migrations, `direnv allow`. Prefer this; it stays correct when branches disagree. |
| **Grant** | `seed.require` + the profile's `env` list | It is a secret (or another machine-local credential) the lane needs *some keys of*. The file must exist in the primary checkout and is never copied whole; the lane gets exactly the keys its profile grants, read at lane-creation time. |
| **Copy** | `seed.copy` | Small, non-secret, machine-local, and *not* derivable — tool configs, local overrides. The lane owns its copy and may diverge from the primary's. |
| **Link** | `seed.link` | Machine-local files the lane must read but must never own privately. Wft links them to the primary checkout's file; never copied. |

One guard the schema enforces and the author must respect: a `seed.copy` or
`seed.link` entry may never name a `seed.require` file or an `.env`-shaped path.
The config file is committed, so it must not be usable to smuggle a whole secret
file into a lane — the loader refuses such an entry outright.

**The grant list is the skill's judgment call, per profile, under least
privilege:** name the keys a profile's work actually touches, and nothing more.
A docs profile grants no keys; an e2e profile may need a test database URL the
docs profile must never see. Record the decision by key name only, with the
reason — it is a standing security choice about the repo, and it deserves a
sentence in the commit or the record the repo keeps.

### The toolchain itself

As in any fresh checkout, check the package manager too — `command -v pnpm`,
`command -v uv` — because a setup command that can't find its tool fails exactly
like no setup at all. When the tool is missing, ask the owner; it is a standing
choice about the repo (devshell, corepack shim, or a global install), not a
detail to settle silently. Lean devshell when sibling repos already have one;
the setup command then enters the shell itself.

## 3. Profiles and placement

Profiles carry the flexibility: one repo, several lane setups. A profile may
override placement, Docker posture and memory size, add its own setup and close
commands, and — the part that matters most — own its `env` grant list.

- **`env` is a grant list, not a value list.** It names keys; values are read
  from the `seed.require` files in the primary checkout at lane-creation time.
  The grant list is *not merged* with anything: the granted set is exactly the
  profile's list, or `defaults.env` when the profile states none. A CLI flag may
  select a subset of it; it can never add a key. That asymmetry is the point.
- **Docker posture**, per profile: `none` (default), `stack` (the lane reaches
  services by address from a compose deployment the coordinator runs — the lane
  never sees a daemon), or `own` (the lane has its own daemon — legitimate only
  inside a VM, or rootless on the host after the owner has set that up).
- **Placement.** A host worktree is the default. Use a VM when any of these
  hold:
  - no one watches its approval prompts;
  - it reads untrusted content in bulk (web research, fixes from outside PRs,
    dependency upgrades);
  - it runs code nobody here wrote;
  - the work is sensitive;
  - it needs its own Docker;
  - it changes system state.

  Record the choice with its reason. When the rule gives no clear answer, ask
  the owner — placement is a standing decision about the repo, not a per-lane
  guess.

## 4. Write the file

Repo root, committed, so the whole team gets it:

```yaml
version: 1
defaults: { profile: code, on: host, base: main }
seed:
  require: [app/.env]            # must exist in the primary checkout; NEVER copied whole
  copy:    [configs/tool.yaml]   # non-secret gitignored files the lane owns
  link:    []                    # read-only shares; linked, not copied
setup:                            # derived rebuilds, run as the lane user
  - direnv allow .
  - <lockfile-respecting install>
profiles:
  code: { env: [TEST_DATABASE_URL], docker: stack, stack: dev, size: 4G }
  docs: { env: [], docker: none, size: 1G }
  e2e:  { on: vm, docker: own, size: 6G }
stacks:
  dev: { compose: compose.yaml, on: host }
publish: { by: coordinator }
```

Full field-by-field schema, merge rules and validation:
[`references/wft-yaml-schema.md`](references/wft-yaml-schema.md). Read it before
using `stacks`, `search` or `vm`, which carry real validation.

### Setup commands that survive contact

- **Assume none of your tooling is on PATH.** Setup runs as the lane user in a
  plain environment: no direnv, no devshell, no version-manager shim, no
  activated virtualenv. A repo whose toolchain comes from any of those must
  resolve the binary itself — or warn and skip rather than dying. This is the
  most common way a setup that passed in your own shell fails in the first real
  lane.
- **Locate the primary checkout dynamically**, never hardcoded:
  `primary="$(git worktree list --porcelain | awk 'NR==1 && $1=="worktree" {print $2; exit}')"`
  — needed when a setup step must read a granted key's source file from it.
- **`set -eu`, not `set -euo pipefail`**, and an `if` block instead of
  `cmd -v foo >/dev/null && foo` — a bare failing `&&` chain aborts the script.
- **Be idempotent.** Setup re-runs; guard copies with `[ ! -e "$dest" ]`.
- **Make verification non-fatal.** Ending with a test run is a free correctness
  proof, but a mid-refactor branch should not present as a broken lane: append
  `|| echo "WARNING: ..."`.
- **Keep secrets out.** The file is committed. Credentials live in
  `seed.require` files and arrive as granted keys; never inline a value.
- **Stay fast.** Depending on configuration, the agent may start working before
  setup finishes.

## 5. Validate

The loader fails closed, so the file is either fully accepted or fully refused —
but only when the CLI is installed. With the CLI: `wft init` validates what it
writes and reports the fields it could not map, and `wft doctor` checks the
config against the machine (harness, lane user, Docker posture). Without it,
walk this checklist and say so:

1. **Duplicate keys anywhere.** One repeated key invalidates the whole
   document, and the refusal should be loud — a config that silently loses a
   key is worse than no config.
2. **Unknown keys.** They fail rather than being ignored; a typo must not
   become a silently dropped setting.
3. **Every `seed` path is untracked.** Seed exists to replace what git cannot
   give; a tracked path in `seed` is a mistake the loader refuses.
4. **No `seed.copy`/`seed.link` entry names a `seed.require` file or an
   `.env`-shaped path** — the never-copied-whole rule, made structural.
5. **Each stack's compose file is tracked**, and `defaults.profile` names a
   profile that exists.

Completion criterion: every key in the file is either loader-validated or
checklist-checked, and the grant list of every profile has an owner-decision
behind it.

## 6. Test for real

Run `wft doctor` (when available), then exercise one throwaway lane exactly as
a lane will experience it — create it, let setup run, close it:

- a missing `seed.require` file refused **before** the workspace was created;
- the granted keys arrived — check by name, never by value — and only those;
- no secret file was copied into the workspace, whole or in part;
- setup ran clean a second time (idempotence).

A failing setup is not contained: a lane that dies mid-setup looks like an
orchestration failure rather than a config one, so an unexplained lane failure
is worth checking against the setup output before blaming dispatch.

## What this skill must not do

- Never copy a secret file into a lane, an archive, or a `seed.copy`/`seed.link`
  entry.
- Never print or inline a secret value — key names only, in the config, in
  chat, in receipts, in reports.
- Never grant a profile an env key its work does not touch.
- Never hand a lane a Docker daemon where a stack address suffices, and never a
  push token — publication goes through the coordinator's publish path, never
  from the lane.

For dispatching and supervising lanes once the repo is set up — briefs, waits,
the review gate — see the `dispatching-work` skill.
