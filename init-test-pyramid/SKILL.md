---
name: init-test-pyramid
description: Set up a repository's test pyramid as a layer map. Use when a repository has no stated test layers.
---

Writes a repo-local **layer map** for the current repository: every layer named,
each with one suite and one command, a recorded answer to "where does this
run", and the escape rule. The map is repo-specific by design and lives in that
repo; this skill never names a runner or a stack, it discovers them.

The standard the map holds the repo to — the whole pyramid covered, and then
some:

- **Every layer has a named suite, UI included.** A layer not yet built still
  names its suite and the item that tracks building it.
- **Suites above unit stay out of the default CI run.** End-to-end and live
  suites need a database, a browser, a server boot or a bill; a gate that goes
  red on infrastructure stops being trusted.
- **An escape names its layer.** When a failure reaches a human, the response
  names which layer should have caught it, and that layer gets the test. If no
  layer could have seen it, the response adds a layer — the missing piece was
  the instrument, not the coverage.
- **One pre-release command answers once.** It runs the hermetic layers in
  order and emits one go/no-go report that also lists the live steps it did not
  run.
- **Each suite owns its test state.** No two suites share writable state, so a
  concurrent run cannot corrupt another.

A layer is defined by the question it answers that the layer below cannot
express. The usual ladder: unit (a function, module or component), app-path
end-to-end (the real entry point, faked only at external edges), UI (what a
person sees, in a real browser or device), live (real external services). A
repo may need fewer or more.

## Procedure

### 1. Inventory the suites that exist — never assume

Read, don't guess: runner configs and their include globs, the package
manifest's scripts or task runner, every CI workflow, and the test directories
themselves. For each suite record its command, what it runs against (fakes,
a database, a browser, a live endpoint), what state it writes, and whether CI
invokes it. Read the repo's `CLAUDE.md` / `AGENTS.md` for anything already
stated about testing, and look for an existing layer map: a pointer in those
files, a `*-test-pyramid` skill, or a testing doc. If one exists, audit it
against the five standard points above and amend it in place, keeping its
form; steps 2–6 then fill only what the audit found missing.

Completion criterion: every test file is assigned to one suite (or listed as
orphaned), every test command CI runs is quoted from the workflow file, and an
existing map is either found and audited or confirmed absent.

### 2. Name the layers with the owner

Map the inventory onto layers. For each layer settle one suite (one directory
or config) and one command, and record whether it is hermetic (no network
beyond the machine, no credential, no bill) or live. Where a layer has no
suite — most often UI and live — ask the owner: build it now, or record it in
the map as owed. An owed layer still names its suite (the directory, runner
config and command it will have) and the item that tracks building it.

Completion criterion: every layer has a suite, a command and a hermetic-or-live
mark; an owed layer also names its tracking item.

### 3. Place each layer, and make the placement structural

The default CI run invokes the lowest layer only. Keep the layers above out of
it by construction rather than by care: each such suite lives outside the
default runner's globs, has its own runner config, uses a file suffix the
default glob misses, and has a standalone command that no hook chains. Add one
guard test per excluded suite, inside the default suite so it runs in the job
it protects, that fails when the default run would pick that suite up. Record
for every layer where it runs: every push, pre-merge by hand, pre-release, or a
coordinated live session.

Completion criterion: the CI workflow invokes no test suite other than the
default layer's, and each guard has gone red once under the mutation it exists for
(widening a glob, renaming a file to the default suffix).

### 4. Give each suite its own test state

Each suite gets its own database, schema, temporary directory or fixture
identity, provisioned on demand so a first run costs one setup step. Where the
state must exist per worktree and the repo uses Orca worktrees, put the
provisioning in the setup hook with the `orca-project-init` skill.

Completion criterion: for every pair of suites, the map names what keeps their
writable state apart.

### 5. Write the one pre-release command

It runs exactly the layers step 2 marked hermetic, cheapest first, and stops
at the first failure, because a failure below makes the layers above
undiagnosable. It writes one report: per-layer counts, which layers were not
attempted, and a final section listing every live step it did not run and
every owed layer — a GO is a statement about the hermetic layers only, and
never hides a missing one.

Completion criterion: the command has been run once, and its report's last
section names every live-layer command and every owed layer from step 2.

### 6. Write the layer map

Choose the form from the repo's conventions: a repo-local skill (named with the
repo's project-skill prefix, `<prefix>-test-pyramid`) when the repo already
keeps project skills and agents routinely write its tests; otherwise a doc in
the repo's docs location. The map is the single source for the layer table
and the rules. It may point at docs that hold mechanism detail (the
pre-release command, isolation), and the agent instruction file points at the
map. A skill's description triggers on writing or reviewing a test, deciding
where one goes, adding a suite, and asking why a failure was not caught.

The map holds: a table of layers (suite, command, what it fakes or needs,
where it runs, hermetic or live); placement — a test goes in the lowest layer
that can prove its claim; the isolation from step 4; the pre-release command from
step 5; and the escape rule verbatim. Values that live in a config file
(thresholds, env vars, scenario lists) are pointed at, not copied.

Completion criterion: the map exists, the agent instruction file points at it,
every hermetic command it names has been run once, and each live command is
either run once in a session the owner starts, or recorded in the map as not
yet run.

## Scope

The map carries what is true of this one repository — runners, commands, paths,
databases. This skill carries the procedure and the standard, so a change to
either is a one-place edit, and regenerating the map after the repo's suites
change means re-running steps 1–6 against the current tree.
