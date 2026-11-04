---
name: init-test-pyramid
description: Set up a repository's test pyramid — named layers, one suite and one command per layer, where each runs, and the rule that an escaped failure names the layer that should have caught it. Use when a repository has no stated test layers, is being onboarded to the pyramid, or a failure reached a human that no suite would have caught.
---

Writes a repo-local **layer map** for the current repository: every layer named,
each with one suite and one command, a recorded answer to "where does this
run", and the escape rule. The map is repo-specific by design and lives in that
repo; this skill never names a runner or a stack, it discovers them.

The standard the map holds the repo to — the whole pyramid covered, and then
some:

- **Every layer has a named suite, UI included.** A layer with no suite is a
  gap, recorded as one.
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
repo may need fewer or more; "more of the same, slower" is not a layer.

## Procedure

### 1. Inventory the suites that exist — never assume

Read, don't guess: runner configs and their include globs, the package
manifest's scripts or task runner, every CI workflow, and the test directories
themselves. For each suite record its command, what it runs against (fakes,
a database, a browser, a live endpoint), what state it writes, and whether CI
invokes it. Read the repo's `CLAUDE.md` / `AGENTS.md` for anything already
stated about testing.

Completion criterion: every test file is assigned to one suite (or listed as
orphaned), and every test command CI runs is quoted from the workflow file.

### 2. Name the layers with the owner

Map the inventory onto layers. For each layer settle one suite (one directory
or config) and one command. Where a layer has no suite — most often UI and
live — ask the owner: build it now, or record it in the map as owed.

Completion criterion: every layer has a suite and a command, or an explicit
owner decision recording it as a gap.

### 3. Place each layer, and make the placement structural

The default CI run invokes the lowest layer only. Keep the layers above out of
it by construction rather than by care: each such suite lives outside the
default runner's globs, has its own runner config, uses a file suffix the
default glob misses, and has a standalone command that no hook chains. Add one
guard test per excluded suite, inside the default suite so it runs in the job
it protects, that fails when the default run would pick that suite up. Record
for every layer where it runs: every push, pre-merge by hand, pre-release, or a
coordinated live session.

Completion criterion: the CI workflow invokes only the default layer's
commands, and each guard has gone red once under the mutation it exists for
(widening a glob, renaming a file to the default suffix).

### 4. Give each suite its own test state

Each suite gets its own database, schema, temporary directory or fixture
identity, provisioned on demand so a first run costs one setup step. Where the
state must exist per worktree and the repo uses Orca worktrees, put the
provisioning in the setup hook with the `orca-project-init` skill.

Completion criterion: for every pair of suites, the map names what keeps their
writable state apart.

### 5. Write the one pre-release command

It runs the hermetic layers cheapest first and stops at the first failure,
because a failure below makes the layers above undiagnosable. It writes one
report: per-layer counts read from each runner's machine-readable output
(output that will not parse is reported as unreadable, never as zero), which
layers were not attempted, and a final section listing every live step it did
not run — a GO is a statement about the hermetic layers only.

Completion criterion: the command has been run once, and its report's last
section names every live-layer command from step 2.

### 6. Write the layer map

Choose the form from the repo's conventions: a repo-local skill (named with the
repo's project-skill prefix, `<prefix>-test-pyramid`) when the repo already
keeps project skills and agents routinely write its tests; otherwise a doc in
the repo's docs location. Either way it is the single source, and the repo's
`CLAUDE.md` / `AGENTS.md` carries one pointer to it. A skill's description
triggers on writing or reviewing a test, deciding where one goes, adding a
suite, and asking why a failure was not caught.

The map holds: a table of layers (suite, command, what it fakes or needs,
where it runs); the placement ladder — climb from unit and stop at the first
layer that can prove the claim, so nothing is bought expensively that could be
proved cheaply; the isolation from step 4; the pre-release command from
step 5; and the escape rule verbatim. Values that live in a config file
(thresholds, env vars, scenario lists) are pointed at, not copied.

Completion criterion: the map exists, the agent instruction file points at it,
and every command it names has been run once.

## Scope

The map carries what is true of this one repository — runners, commands, paths,
databases. This skill carries the procedure and the standard, so a change to
either is a one-place edit, and regenerating the map after the repo's suites
change means re-running steps 1–6 against the current tree.
