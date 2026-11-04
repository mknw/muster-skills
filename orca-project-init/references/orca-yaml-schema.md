# `orca.yaml` schema

Derived by reading `parseOrcaYaml` and its helpers out of the shipped Orca
application bundle (verified against **1.4.182**), because the published docs
split this across pages and no single page lists every key. If a field here
disagrees with the app, the app wins — re-derive with:

```bash
python3 - <<'PY'
import re
b = open("/Applications/Orca.app/Contents/Resources/app.asar","rb").read().decode("utf-8","replace")
i = b.find("function parseOrcaYaml")
print(b[i:i+2000])
PY
```

On Linux/Windows the bundle sits under the install root's
`resources/app.asar` instead.

## Contents

- [Document rules](#document-rules)
- [`scripts`](#scripts)
- [`issueCommand`](#issuecommand)
- [`defaultTabs`](#defaulttabs)
- [`environmentRecipes`](#environmentrecipes)
- [`worktree.sharedDirectories`](#worktreesharedDirectories)
- [Related files](#related-files-not-orcayaml)

## Document rules

Location is the **repo root**. It is committed, so treat it as shared team
config and never put secrets in it.

| Rule | Behaviour |
|---|---|
| Whole-file size | > 262144 chars **or** UTF-8 bytes → file rejected |
| Per-string-field size | > 65536 chars/bytes → *that field* becomes undefined |
| YAML errors | Any parse error → whole file rejected |
| Duplicate keys | Parsed with `uniqueKeys: true` → **whole file rejected** |
| Root type | Must be a mapping; a list or scalar → rejected |
| Alias expansion | `maxAliasCount: 100` |
| Empty result | If none of the six fields yields a value → **treated as missing** |

"Rejected" and "treated as missing" are the same observable outcome: Orca
behaves as if there is no `orca.yaml` at all. There is no error surfaced to the
CLI, which is why validation has to be deliberate.

All string fields pass through a trim; a whitespace-only value becomes
undefined, exactly as if the key were absent.

## `scripts`

```yaml
scripts:
  setup: |
    <shell>
  archive: |
    <shell>
```

- `scripts.setup` — runs **after** a worktree is created.
- `scripts.archive` — runs **before** a worktree is archived or removed. It
  cannot veto the removal, so it is only useful for reporting (e.g. logging
  unpushed commits about to be discarded).

Both are plain strings; a block scalar (`|`) keeps newlines. Either may be
omitted. The mapping is read with the same trim rule, so `setup: ""` counts as
absent.

## `issueCommand`

A single string, prepended to the agent's prompt when the worktree is created
from a linked work item.

Placeholders present in the bundle: **`{{artifact_url}}`** and **`{{branch}}`**
(`{{issue}}` appears as a legacy alias). Its best use is carrying repo
conventions — branch/PR policy, dependency workflow, how to run tests — so they
don't depend on each issue author restating them.

## `defaultTabs`

Tabs opened with the new worktree. Array, **max 256 entries**; a non-array is
ignored entirely.

```yaml
defaultTabs:
  - title: dev
    command: npm run dev
    color: "#3b82f6"
```

| Field | Type | Notes |
|---|---|---|
| `title` | string | optional |
| `command` | string | optional |
| `color` | string | optional; must match `/^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$/` |

An **invalid `color` is dropped rather than raising**, and an entry with no
`title`, no `command` and no valid `color` is discarded. So a tab whose only
field is `color: "blue"` vanishes without a word — quote hex colours, since a
bare `#3b82f6` is a YAML comment.

## `environmentRecipes`

On-demand disposable runtimes (cloud sandbox, VM, local container) per
workspace. Array, **max 256**; exceeding that discards all of them.

```yaml
environmentRecipes:
  - id: sandbox
    name: Cloud sandbox
    create: ./scripts/orca-vm/create.sh
    suspend: ./scripts/orca-vm/suspend.sh
    resume: ./scripts/orca-vm/resume.sh
    destroy: ./scripts/orca-vm/destroy.sh
```

| Field | Required | Notes |
|---|---|---|
| `id` | **yes** | `/^[a-z0-9][a-z0-9._-]{0,63}$/` — 1–64 lowercase letters, numbers, dots, underscores, hyphens, starting alphanumeric. Must be unique. |
| `name` | **yes** | Non-empty display name |
| `create` | **yes** | Alias: `command` |
| `description` | no | |
| `suspend` / `resume` | no | |
| `destroy` | no | Alias: `cleanup`. The literal value `none` sets `destroyDisabled` instead of a command. |

Unlike every other field, bad recipes produce **diagnostics** rather than silent
omission, and the presence of diagnostics alone is enough to keep the file from
being treated as missing.

**Deployment gotcha:** recipes appear in the workspace composer only once the
`orca.yaml` change is on the project's **primary branch**. `orca vm recipe doctor`
validates from the working copy of any branch, so a recipe can pass every check
and still be invisible in the picker.

For authoring the lifecycle scripts themselves, use the bundled
`orca-per-workspace-env` skill (`ORCA skills get orca-per-workspace-env`) — it
covers the four setup phases, snapshots and credential handling.

## `worktree.sharedDirectories`

```yaml
worktree:
  sharedDirectories:
    - .cache/build
```

Gitignored **directories** shared into each worktree (symlink, or APFS
clone-copy on macOS) rather than copied. Max **100** entries; deduplicated.

Normalisation: backslashes → `/`, a leading `./` stripped, trailing slashes
stripped. An entry is then **skipped** if it is empty, absolute, drive-letter
prefixed (`C:`), or contains a `..`, `.`, empty, or `.git` segment.

At materialisation time the path must **exist as a directory in the primary
checkout and be gitignored**. Tracked paths, missing paths and plain files are
skipped without complaint.

These entries **add to** the per-user "Worktree Shared Paths" list in
Settings → Repository; they never replace it.

## Related files (not `orca.yaml`)

- **`.worktreeinclude`** (repo root) — gitignored files *or* directories to
  **copy** into each new worktree, one per line. `#` comments and blank lines
  allowed. **Literal paths only** — globs and negation are skipped with a
  warning, so `.env*` matches nothing. This is the right home for `.env`,
  `.envrc` and editor settings; use it instead of hand-rolling copies in
  `scripts.setup` when no conditional logic is needed.
- **`.orca/issue-command`** — file-based alternative to the `issueCommand` key.

## Per-repo settings that live outside the file

Visible under `hookSettings` in `orca repo list --json`, set in
Settings → Repository. They are per-machine and are **not** overridable from
`orca.yaml`:

| Setting | Why it matters |
|---|---|
| `mode` | Whether committed YAML hooks are consulted at all |
| `commandSourcePolicy` | e.g. `shared-only` — YAML vs local scripts vs both |
| `setupRunPolicy` | Whether setup runs by default on new worktrees |
| `setupAgentStartupPolicy` | `start-immediately` lets the agent run against a half-built tree; prefer `wait-for-setup` whenever setup installs anything |
| `scripts.setup` / `scripts.archive` | Local per-machine hooks, stored outside the repo |

`orca repo show` reports these local settings but **not** the parsed
`orca.yaml`, so it cannot be used to confirm the file was accepted.
