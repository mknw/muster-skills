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
2. **always-loaded surface** (APPEND_SYSTEM and peers) — decision-time rules
   that should fire here and do not exist;
3. **skills** — escape-hatch rows without an authority clause; stale defaults;
   era-wrong examples;
4. **modules, packages, extensions** — hooks and affordances;
5. **memories** — ambiguities and silences that were read the wrong way;
6. **in-session habit** — successful uses of the wrong path reinforce it.

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
  owns the file.

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
