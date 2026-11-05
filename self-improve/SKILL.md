---
name: self-improve
description: Turn owner corrections, countermands, and failures into re-engineered decisions, not prose lessons. Fires on owning a mistake to the user, on any correction of a decision you made (mechanism, routing, placement, agent or model choice), and automatically on the second occurrence of the same correction class in one session. Runs a five-step loop — investigate before concluding; anchor at the earliest decision it could have changed; autopsy the loaded stack for what actively fought the right answer; ensure by making the right decision the cheap decision; propose in fixed format (improvement / what fought / remove / add) and apply through proportionate gates. Changes to this skill are themselves produced by this loop and recorded in its design record.
---

# self-improve — the correction loop (v2)

Improvement is **re-engineering of the decision path**, not recording of what
went wrong. Prose lessons fail three ways: they are not addressed at the moment
of decision, not falsifiable against an outcome, and not measurable over time.
This skill therefore produces no prose lessons. It produces four things, each
anchored to a concrete decision: a **live contract**, a **rule on an
always-loaded surface**, a **change to a tracked file**, or the **removal of
text that fought the right answer**.

## Trigger

Fires on:

1. **Owning a mistake to the user** — an apology, a "that was me", a recovery
   report.
2. **Any correction from the user of a decision you made** — mechanism,
   routing, placement, sequencing, agent or model choice — whether or not you
   framed the choice as a mistake. A correction is a lesson surfacing.
3. **The second occurrence of the same correction class in one session** — the
   skill then fires itself; the owner should never have to invoke it by name
   for a repeat.
4. **A trip-wire in a running skill fired** — the skill's body routed here
   with an incident extract (`dispatching-work`'s executor re-decision on scope
   creep; a second same-class worker failure in one run). The extract, not the
   dispatcher's session context, is the incident record.
5. **Owner discontent signal (swearing)** — swearing in the owner's own words
   triggers the loop automatically through the Claude Code prompt hook. Carry
   out the authorized request in the same turn — where the request is a
   question, dispatching-work's declaration-gated question rule applies:
   answer first, declare, then act — or acknowledge the mistake in one line,
   then dispatch a
   subagent under the extract contract below; quote the owner's words in the
   extract. The hook excludes pasted content and system reminders. Its signal
   starts investigation, not a presumed diagnosis.

For Claude Code, install the [prompt hook](hooks/discontent.py) using the
[hook setup](hooks/README.md). Codex and pi have no equivalent hook supplied
here: the equivalent manual trigger is `/self-improve` with the discontent
quote and incident extract, dispatched under the same contract.

Not a trigger: a stumble the next tool call absorbed — a retried command, a
transient error. Apply severity silently.

## The five steps

Run them on the concrete incident. Generalise only at step 5.

### 1. Investigate before concluding

When a capability, surface, or approach is in doubt:

- Consult the **registry of record** first. Evidence hierarchy: official docs
  > CLI reference/schema > examples in skills or help text. **Examples are
  illustrative, never enumerations.**
- An abandoned lookup is not an exhausted lookup: if a tool returned something
  your pattern missed, dig before concluding it has no answer.
- Then complete the answer one of two ways: **ask the owner** the specific
  question, or **push back with evidence** if you believe the desired path is
  impossible. Silence and silent compliance are both incomplete answers; only
  an evidenced claim or an evidenced counter-proposal is a complete one.
- Output: the right answer, its source, and a note of the moment it was first
  available.

### 2. Earliest-moment analysis

Replay to the **first decision the answer could have changed** and anchor the
lesson there — not where the pain became loud. A lesson anchored late
reproduces late. Write the best-case run from that moment, and state the
actual run's cost against it (aborted work, rework, owner interventions).

### 3. Stack autopsy — what *fought* the right decision

Walk the loaded-context stack top-down and name what **actively opposed** the
right decision. Not "what was missing" first — what was present and harmful:

1. **system prompt** — tool affordances; note asymmetry when the wrong path is
   one call and the right path needs external knowledge;
2. **always-loaded surface** — decision-time rules that should fire here and
   do not exist; the surfaces differ per runtime (Claude Code: `CLAUDE.md` at
   user, project and local scopes, `.claude/rules/`, and its auto memory;
   Codex: user and repo `AGENTS.md`; pi: `AGENTS.md`/`CLAUDE.md` plus its own
   `APPEND_SYSTEM` and memory) — verify each against that runtime's own docs
   or installed CLI, never from a prior run's list;
3. **skills** — escape-hatch rows without an authority clause; stale defaults;
   era-wrong examples;
4. **modules, packages, extensions** — hooks and affordances;
5. **memories** — ambiguities and silences that were read the wrong way;
6. **in-session habit** — successful uses of the wrong path reinforce it;
7. **runtime-specific assumptions** — surfaces or affordances the loop took
   for granted (a memory hook, an instruction-file path, a tool) that hold in
   the runtime it ran in but not in the others the owner uses.

Verdict per layer: **active fight / stale default / ambiguity / gap / clean.**

### 4. Ensure — make the right decision the cheap decision

For each fight or gap, in enforcement order (environment > always-loaded
prose > skills > memory):

- **Remove or subordinate** the fighting text: an escape-hatch row gains
  "except where the owner has ruled on this"; a stale default is replaced with
  the current, era-stamped ruling.
- **Add decision-time rules to the always-loaded surface** — recall is
  guaranteed there and only there.
- **Disambiguate** rulings that were read two ways; the ruling's owner
  confirms the reading.
- **Prefer environment-level enforcement** — wrappers, hooks, one-command
  paths — over prose: friction asymmetry (right path expensive, wrong path
  cheap) beats any rule.
- **Harness parity** — a lesson that governs agent behaviour lands on an
  always-loaded surface **every runtime in use loads** — the surfaces the
  autopsy's layer 2 names, verified against each runtime's own docs or
  installed CLI, the registry of record — never from a prior run's
  assumptions. The proposal states which runtimes the
  lesson reaches and which it does not; a runtime-specific place alone (one
  runtime's project memory, say) is a gap, named as such in the proposal and
  covered by each runtime's equivalent surface or an explicit fallback.

### 5. Propose — fixed format, proportionate gates

Present exactly four fields:

- **IMPROVEMENT** — one short paragraph: the generalised procedure, not the
  incident story.
- **WHAT FOUGHT** — the autopsy's fights, named by layer.
- **REMOVE** — per layer, concrete.
- **ADD** — per layer, concrete.

Then apply through gates proportionate to **blast radius × persistence**,
never task size:

- **Live contract** — a session-scoped behavioural amendment ("every dispatch
  gets sign-off first"), stated in one line, binding immediately, dies with
  the session. No gate: the session is the review.
- **Memory** — apply directly; the owner sees entries in the index.
- **Tracked files** — branch → PR → owner review and merge, in whichever repo
  owns the file. In an owner-authorized autonomous cycle, use the forced review
  gate below within the delegated merge authority.

For correction-class lessons, draft trigger conditions **from the owner's
quoted words** and have them confirm the reading — the agent's paraphrase is
where shallowness enters.

## Dispatched runs — the extract contract

A trip-wire reaches this loop by dispatching it as a subagent, in a context
that cannot see the dispatcher's session. That independence is the point: the
dispatcher shares the framing that produced the snag — the same reason the
review gate bars the author and the coordinator from reviewing.

So the **extract is the whole record**: self-contained, ~400 words, four parts.

- **Expected** — what the plan said would happen.
- **Observed** — what happened instead, with the facts that diverged.
- **Decisions made and why** — each decision at the moment it was taken, with
  the reasoning available then.
- **Attempts and outcomes** — what was tried after the divergence, and what
  each attempt returned.

Run the five steps on the extract alone; where it is silent, name the silence
as a gap in the record rather than reconstructing from the dispatch prompt.
Propose in the same fixed four-field format, and land the outputs through the
same proportionate gates — tracked-file changes go branch → PR.

### Autonomous review gate — FORCED

In the autonomous self-improvement cycle, every PR receives independent review
commissioned by the coordinator. The reviewer is neither the author nor the
coordinator. In a plain session, the originating agent commissions a separate
reviewer and acts as coordinator. Apply findings and repeat review on the
updated changes until the reviewer explicitly returns **CONVERGED**, following the
[review loop](../reviewing-changes/SKILL.md). Green CI alone never authorizes
merge. Report `merge_ready` only after convergence; merge remains with the
authorized merger under the tracked-file gate above. Delegation comes from an
explicit live owner contract; without it, keep the PR for owner review and
merge. If review is unavailable or cannot reach CONVERGED, leave the PR open
and escalate the unresolved terms to the coordinator, or the owner in a plain
session; merge remains gated.

## Design record — the recursion, made textual

**Convention:** every change to this skill is itself produced by running this
loop on the incident that motivates it, and is recorded below — date, incident
in one line, which step failed, what changed. A change to the skill without an
entry here is unreviewed drift. The skill is part and parcel of its own
improvement history.

**2026-08-29 — v1 → v2.** Incident: in one session the v1 pipeline fired only
when the owner invoked it by name, after **three** corrections of the same
class (dispatch routing: native subagent vs orchestration-runtime lanes). Its
ask-gate had no branch for redirects, so an earlier directive answer silently
killed the lesson pipeline; and a v1 invocation produced three shallow edits
because the lessons were the agent's paraphrase rather than anchored in the
owner's words. Steps that failed: the **trigger** (the description mentioned
corrections, but the body's firing condition never acted on them); **step 4's
single gate** (apply-or-decline only — no redirect branch, no proportionality);
and the **output format** (prose lessons, unverifiable). Change: full v2 —
correction-and-repeat trigger; the five-step owner-shaped loop (investigate
before concluding, with push-back as a duty; earliest-moment anchoring; stack
autopsy for active opposition; ensurance over recording; fixed-format
proposal); proportionate gates with the live contract; owner-words drafting;
and this design record.

**2026-09-18 — trip-wire branch and the extract contract.** Incident: a
2026-08-24 session drafted a course-correcting skill that never landed; its
capture gate and user-rejection branch duplicated this skill's trigger and its
step-5 gates. Step that failed: the **trigger** — every branch routed through
the owner, so a flow skill that detected its own snag mid-run had nowhere to
send it. Change (owner-approved fold rather than a second skill): trip-wires in
flow skills now route here as branch 4, via a dispatched subagent, and the
extract contract above defines what that subagent receives. The description
pointer is unchanged — the trip-wire line in the calling skill's body is the
pointer that reaches here, and restating that branch in the description would
be one branch written twice.

**2026-11-05 — discontent signal and forced autonomous review.** Incident: an
agent deferred a small authorized fix under a superseded memory rule; repeated
explanation drew swearing, yet the owner still had to invoke this loop by name.
Steps that failed: the **trigger** had no discontent branch, and **step 4** left
the decision-time path dependent on recall. Change: branch 5 routes the prompt
hook's discontent signal into an extract-only subagent run; the tracked hook
has exclusion, timeout and mutation-tested behavior plus idempotent setup;
Codex and pi retain an explicit manual trigger. The autonomous cycle now
requires independent review to CONVERGED before merge, including fix rounds.
The superseded memory was corrected in the originating session; no private
memory or project-specific authority is carried into this skill.
Independent review added reversible hook setup and clarified plain-session
review, unavailable or nonconverging review, and live-contract merge authority.

**2026-11-05 — harness parity and the runtime-specific sweep.** Incident: the
loop anchored a lesson to a surface only one runtime loads, and the skill's own
text carried assumptions (hook paths, instruction files, memory tools) that do
not hold outside the runtime the loop ran in. Steps that failed: **step 3**'s
autopsy had no runtime-specific layer, and **step 4**'s enforcement had no
parity rule. Change: step 3 gains a runtime-specific-assumptions layer; step 4
gains the harness-parity rule — a behaviour-governing lesson lands on an
always-loaded surface every runtime in use loads, verified against each
runtime's own docs or installed CLI, with runtime-only surfaces named as gaps;
the skill's runtime-specific assumptions (hook paths, instruction files, memory
tools) are verified as runtime-neutral or explicitly per-runtime. This entry
is itself produced by the loop; the FORCED autonomous review gate applies — an
independent reviewer (neither the author nor the coordinator) reviews this
change, and merge follows CONVERGED.
