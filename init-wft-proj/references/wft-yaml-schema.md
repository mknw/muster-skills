# wft.yaml schema

The full field reference for `wft.yaml`, the per-repo config the
`init-wft-proj` skill writes. One file per repo, committed at the root, so the
whole team gets it. The loader **fails closed**: unknown keys, duplicate keys
and schema violations refuse the entire file rather than ignoring one field.

## Top-level fields

| Field | Type | Default | Meaning | Validation |
| --- | --- | --- | --- | --- |
| `version` | int | required | schema version | must be `1` |
| `defaults` | map | `{}` | fallback values for every lane | keys come only from: `profile`, `on`, `stack`, `docker`, `size`, `base`, `env` |
| `seed.require` | list of paths | `[]` | gitignored secret files that must exist in the primary checkout. A missing source refuses lane creation **before** the workspace exists. **Never copied whole** — a lane receives only the env keys its profile grants, read from these files at lane-creation time. | repo-relative, no `..`, no absolute paths |
| `seed.copy` | list of paths | `[]` | non-secret gitignored files copied into the lane, which the lane may then diverge from (tool configs, local overrides) | same path rules; may not name a `seed.require` file or an `.env`-shaped path |
| `seed.link` | list of globs | `[]` | files the lane must read but never own privately; linked to the primary checkout's file, never copied | glob under the repo; resolved targets stay inside it; same prohibition as `seed.copy` |
| `setup` | list of commands | `[]` | run in the fresh workspace after seeding, before the agent starts; as the lane user | each short, no interpolation of lane-controlled input |
| `close` | list of commands | `[]` | run before a lane is removed; reporting only, they cannot block removal | same |
| `profiles` | map of name → profile | required, at least one | the per-setup variants (below) | name: lowercase, starts with a letter, short |
| `stacks` | map of name → stack | `{}` | shared compose deployments lanes connect to | name: same shape as profiles |
| `publish` | map | `{by: coordinator}` | publication policy; lanes never push | keys come only from: `by`, `base`, `branch-prefix` |
| `search` | map | `{}` | research-lane policy (web reading happens in a fenced lane, its report is data) | keys come only from: `enabled`, `model`, `budget-minutes` |
| `vm` | map | `{}` | defaults for VM-placed lanes | keys come only from: `default`, `pool`, `project`, `memory-cap` |

## Profile fields (`profiles.<name>`)

Every field optional; a profile overrides `defaults` and may add to the lists.

| Field | Type | Default | Meaning |
| --- | --- | --- | --- |
| `env` | list of key names | `[]` | **The only env keys granted to lanes of this profile.** A grant list of names, never values — values are read from the `seed.require` files in the primary checkout at lane-creation time and written to a coordinator-owned file the lane can read but not write. |
| `docker` | `none` \| `stack` \| `own` | `none` | Docker posture: no Docker; services by address from a coordinator-run stack; or the lane's own daemon (a VM, or rootless on the host only). |
| `stack` | stack name | — | which `stacks` entry this profile connects to; requires `docker: stack` |
| `on` | `host` \| `vm` \| `vm:NAME` | `host` | placement; bare `vm` resolves to the `vm.default` VM |
| `size` | memory spec | `1G` | memory for VM lanes; advisory only for host lanes |
| `setup` | list | `[]` | appended after the top-level `setup` |
| `close` | list | `[]` | appended after the top-level `close` |
| `seed` | map | `{}` | additional `require` / `copy` / `link` entries, appended to the top-level lists |

## Stack fields (`stacks.<name>`)

| Field | Type | Default | Meaning |
| --- | --- | --- | --- |
| `compose` | path | required | compose file, repo-relative, must be tracked |
| `files` | list of paths | `[]` | extra files compose needs, staged to the stack's own directory — never into lanes |
| `on` | `host` \| `vm:NAME` | `host` | where the coordinator runs the stack |
| `env` | list of key names | `[]` | keys the coordinator supplies to the stack itself (for example a database password); **never** the lane grant list |

## Merge rules

Resolution for one lane creation, profile `P` plus CLI flags:

1. **Scalars and maps** (`on`, `docker`, `stack`, `size`, `base`, `publish.*`):
   CLI flag > profile `P` > `defaults` > schema default. One guard: a CLI flag
   may not escalate a lane's isolation — asking for `own` Docker on a profile
   that declares `none` is refused; pick a profile that declares it instead.
2. **Lists** (`setup`, `close`, `seed.*`): concatenated `defaults` → profile →
   CLI, duplicates dropped preserving order.
3. **`env` is not merged.** The granted set is exactly `profiles.P.env`, or
   `defaults.env` when the profile states none. A CLI flag may only select a
   subset. This asymmetry is the security property: no flag path can widen a
   grant; only a committed edit of the profile can.
4. **Unknown keys refuse the whole file** before anything is created.

## Validation

The loader refuses the file, before any workspace exists, when:

- any key is duplicated — one duplicate invalidates the whole document;
- any key is unknown — a typo must not become a silently dropped setting;
- a `seed` path is a tracked file (seed exists for what git cannot give);
- a `seed.copy` or `seed.link` entry names a `seed.require` file or matches an
  `.env`-shaped path — so a committed config cannot quietly reverse the
  never-copied-whole rule;
- a stack's `compose` file is untracked;
- `defaults.profile` names a profile that does not exist.

Without the CLI installed, `init-wft-proj` runs this same list as a manual
checklist and says plainly that the loader did not check the file.
