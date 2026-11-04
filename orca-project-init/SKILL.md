---
name: orca-project-init
description: >-
  Set up or repair a repository's orca.yaml so new Orca worktrees bootstrap
  themselves — setup/archive hooks, issueCommand, defaultTabs, shared
  directories, and environment recipes. Use this whenever the user mentions
  orca.yaml, Orca worktree setup or hooks, initializing or onboarding a repo for
  Orca, or complains that a new worktree is missing its .env / node_modules /
  venv / build cache, that dependencies have to be reinstalled by hand every
  time, or that an Orca setup script "isn't running" — even if they never name
  the file. Also use it before hand-editing an existing orca.yaml, because a
  single duplicate key makes Orca discard the entire file silently.
---

# Orca project init

An Orca worktree is a **clean git checkout**. Everything in `.gitignore` is
therefore absent: no `node_modules`, no `.venv`, no `.env`, no build cache. The
repo looks complete and isn't, which is why the first command an agent runs in a
new worktree so often fails.

`orca.yaml` at the repo root fixes this once, for everyone, in version control.

## Resolve the CLI first

Pick the executable once and reuse it. `ORCA` below is a placeholder — substitute
the real name, don't run `ORCA` literally.

1. `$ORCA_CLI_COMMAND` if set (Orca exports this for managed WSL sessions)
2. `orca-dev` in a dev checkout that exposes `ORCA_DEV_REPO_ROOT`
3. `orca-ide` on Linux outside an Orca terminal. **Never bare `orca` there** — it
   normally resolves to the GNOME Orca *screen reader* and starts speech on the
   user's machine.
4. Otherwise `orca`

`ORCA skills get orca-cli` prints the version-matched CLI guide. This skill covers
the config file; that one covers driving Orca.

## 1. Inventory what a fresh worktree is missing

Don't guess from the stack — ask git, then look at what's actually on disk:

```bash
git -C <repo> ls-files --others --ignored --exclude-standard --directory | head -50
du -sh <each candidate> 2>/dev/null | sort -h | tail
```

Then sort each entry into one of three buckets. This is the whole design
decision, and getting it wrong is the usual cause of weird cross-branch bugs:

| Bucket | Mechanism | Use when |
|---|---|---|
| **Derive** | `scripts.setup` | It can be rebuilt from tracked files — installing deps, migrations, codegen, `direnv allow`. Prefer this; it stays correct when branches disagree. |
| **Copy** | `.worktreeinclude` | Small, machine-local, and *not* derivable — `.env`, `.envrc`, editor settings. Each worktree gets its own copy. |
| **Share** | `worktree.sharedDirectories` | Large, expensive, and genuinely branch-independent caches. One instance, symlinked (APFS clone-copy on macOS). |

**Be conservative with Share.** A shared directory is one instance seen by every
worktree, so if two branches would ever disagree about its contents, sharing
turns that disagreement into corruption that reproduces on neither branch alone.
Dependency trees (`node_modules`, `.venv`) usually fail this test even though
they're the most tempting candidates — a branch that adds a dependency silently
mutates every other worktree. Share content-addressed or immutable caches
instead. When unsure, derive; a slow setup beats a haunted one.

### The fourth bucket: the toolchain itself

The three buckets cover files inside the repo. Check the package manager too —
`command -v pnpm`, `command -v uv` — because a hook running `pnpm install` on a
machine with no `pnpm` fails exactly like no hook at all, surfacing as a broken
worktree rather than a missing binary. On nix-managed machines this is the normal
case: `node`, `npm` and `corepack` arrive from home-manager while `pnpm` never
does.

When the tool is missing, **ask** — it is a standing choice about the repo, not a
detail to settle silently:

| Option | Consequence |
|---|---|
| **Devshell** — `flake.nix` + `.envrc` | Tracked, so every worktree gets the toolchain with nothing to copy. The hook must enter the shell itself. |
| **Corepack** — `corepack pnpm …` | Already present wherever node is. Downloads the manager on first use, and picks its own version unless `packageManager` is pinned in `package.json`. |
| **Global install** | Hook stays a one-liner; every machine that clones the repo needs the same install done by hand. |

Lean devshell when sibling repos already have one (list `*/flake.nix` in the
directory that holds the primary checkout), and
crib the pinned `nixpkgs` input and `system` from the nearest sibling rather than
inventing them, so the new shell matches the ones that already work.
`pkgs.nodejs_22` with `pkgs.corepack_22` covers a pnpm repo; `pkgs.pnpm` pins the
manager version in nix instead of in `package.json`.

Two things bite:

- **`nix develop` only sees tracked files.** An untracked flake is invisible to
  it, so `git add flake.nix flake.lock` is part of writing one — and a fresh
  worktree carries the flake only if it was committed on the base branch.
- **The hook runs outside the shell.** Wrap the commands that need it:
  `nix develop --command pnpm install`, or
  `nix develop --command sh -c '<several steps>'`.

## 2. Write the file

Repo root, committed, so the whole team gets it. Orca recognises exactly six
things — `scripts.setup`, `scripts.archive`, `issueCommand`, `defaultTabs`,
`environmentRecipes`, `worktree.sharedDirectories`. Anything else is ignored.

```yaml
scripts:
  setup: |
    set -eu
    # Everything gitignored is absent in a fresh worktree. Rebuild it.
    <install deps>
  archive: |
    set -eu
    # Runs before removal. It cannot block deletion, so it only reports.
    exit 0

issueCommand: |
  Work the linked item: {{artifact_url}}
  <conventions the issue author shouldn't have to restate>

worktree:
  sharedDirectories:
    - .cache/build
```

Full field-by-field schema, limits and normalisation rules:
[`references/orca-yaml-schema.md`](references/orca-yaml-schema.md). Read it
before using `defaultTabs` or `environmentRecipes`, which have real validation.

### Setup hooks that survive contact

- **Assume none of your tooling is on PATH.** Orca runs the hook in a plain
  login shell: no direnv, no nix devshell, no mise/asdf/nvm shim, no activated
  virtualenv. A repo whose toolchain comes from any of those must resolve the
  binary itself — e.g. `uv` if present, else `nix develop --command uv`, else
  warn and skip rather than dying. This is the most common way a hook that
  passed locally fails on the first real worktree, because running it from your
  own shell inherits everything the real one lacks.
- **Locate the primary checkout dynamically**, never a hardcoded path:
  `primary="$(git worktree list --porcelain | awk 'NR==1 && $1=="worktree" {print $2; exit}')"`
  The main working tree is always listed first. Compare it against
  `git rev-parse --show-toplevel` so the hook is a no-op in the primary itself.
- **`set -eu`, not `set -euo pipefail`.** The hook may run under a POSIX `sh`
  where `pipefail` is unsupported, and the hook then dies on line 1.
- **Never `cmd -v foo >/dev/null && foo`** as a bare statement under `set -e`: when
  the guard is false the whole `&&` chain returns non-zero and aborts the script.
  Use an `if` block.
- **Be idempotent.** Setup re-runs. Guard copies with `[ ! -e "$dest" ]`.
- **Make verification non-fatal.** Ending with a test run is a great free
  correctness proof, but a branch mid-refactor should not present as a broken
  worktree: `<test cmd> || echo "WARNING: ..."`.
- **Keep secrets out.** `orca.yaml` is committed. Copy credentials from the
  primary checkout at runtime; never inline them.
- **Stay fast.** Depending on repo settings the agent may start typing before
  setup finishes (see §5).

## 3. Validate — Orca fails silently here

There is no `orca validate`, and **`orca repo show` does not surface the parsed
file** (it reports only the per-machine hook settings), so a broken `orca.yaml`
looks exactly like no `orca.yaml`. Check it explicitly:

```bash
python3 scripts/validate_orca_yaml.py <repo>/orca.yaml
```

The three ways a valid-looking file goes dead:

1. **A duplicate key anywhere.** Orca parses with `uniqueKeys: true`, so one
   repeated key rejects the *entire document* — not just that key.
2. **Any YAML syntax error.** Same outcome: treated as missing.
3. **Nothing usable parsed.** If every recognised field is empty or absent, the
   file is treated as missing. A file containing only unknown keys is inert.

## 4. Test the hook for real

Run it in a throwaway worktree exactly the way Orca will. This catches the
copy-source logic, ordering assumptions and non-idempotent steps that reading
can't:

```bash
scripts/test_setup_hook.sh <repo>          # creates, runs, re-runs, cleans up
```

It runs the hook under `env -i` with a system-only PATH, which is what Orca
actually provides — testing from your own shell inherits direnv/nix/mise and
will pass while the real worktree fails. Confirm the second run is quiet and
that anything you expected to be copied actually arrived.

A failing setup hook is not contained: `worker-start --setup run` can abort with
`runtime_unavailable` (the runtime dropping the connection) rather than a clean
setup error, so an unexplained dispatch failure is worth checking against the
setup terminal's output before blaming orchestration.

## 5. Settings `orca.yaml` cannot express

These are per-repo, per-machine, in Settings → Repository (visible via
`ORCA repo list --json` under `hookSettings`):

- **`setupAgentStartupPolicy`** — `start-immediately` lets the agent begin while
  setup is still installing, so it can hit a half-built dependency tree. If your
  setup builds anything, recommend **`wait-for-setup`**.
- **`mode` / `commandSourcePolicy`** — whether committed `orca.yaml` hooks, local
  per-machine scripts, or both run. If hooks don't fire and the YAML validates,
  check here before debugging the file.
- **Worktree Shared Paths** — the per-user list. `worktree.sharedDirectories`
  *adds to* it and never replaces it.

Also note: **`environmentRecipes` only appear in the workspace composer once
committed to the project's primary branch.** `ORCA vm recipe doctor` validates
from any branch's working copy, so a recipe can pass every check and still not
show up. Say this up front rather than debugging it later.

## Gotchas worth stating unprompted

- **A copied `.envrc` does nothing until `direnv allow` runs.** direnv refuses any
  `.envrc` it hasn't been shown, so copying it silently produces a worktree where
  the environment never loads. Run `direnv allow .` in setup, guarded by an `if`.
- **`nix develop` inherits the ambient `PATH`.** A stale `.direnv` profile keeps
  removed packages visible, so a tool you just deleted from `flake.nix` still
  resolves. Verify with `nix develop --ignore-environment`, and tell the user to
  run `direnv reload` in existing checkouts.
- **`.worktreeinclude` takes literal paths only.** Globs and negation are skipped
  with a warning, so `.env*` copies nothing.
- **Shared entries must already exist as gitignored directories** in the primary
  checkout. Tracked or missing paths are skipped silently; files are rejected.

## Python / uv repos

The mechanism differs from the usual node assumption, so be explicit:

- **`uv sync` in `scripts.setup`; keep `.venv` per-worktree.** Never share it —
  branches can declare different dependencies. The cost is low because uv's
  global cache makes a cold sync mostly hardlinks.
- **`.python-version` is normally tracked**, so uv picks the interpreter itself;
  don't hardcode one in the hook.
- **Prefer plain `uv sync`** in a dev worktree. `--locked` fails outright when a
  branch legitimately adds a dependency, and `--frozen` silently installs a stale
  tree; both are better left to CI.
- **`uv run pytest -q` is an excellent closing check** — offline test suites cost
  nothing and prove the interpreter, the venv and imports all work.
- **`uv add` / `uv remove`**, never hand-edited `pyproject.toml` / `uv.lock`.

For other ecosystems the same shape applies — `npm ci` / `pnpm install --frozen-lockfile`,
`bundle install`, `go mod download` — with the lockfile-respecting variant in
setup and the dependency tree kept per-worktree. Where the locked variant aborts
on a lockfile the branch legitimately moved (`pnpm --frozen-lockfile`, `uv
--locked`), fall through to the unlocked install with a warning: reproducible
when the branch agrees with the lockfile, still usable when it doesn't.

For how to dispatch and supervise workers once the repo is bootstrapped — agent-type and model choice, communication policy, typed waits, merge patterns — see the `dispatching-work` skill.
