---
name: self-improve
description: Turn a lesson from this session into a durable edit. Fires the moment you own a mistake to the user — an apology, a "that was me", a recovery report — and on a user correction or countermand, rework caused by a process gap, or the user saying "this must not happen again" / "learn from this". Finds the home (an existing skill, a new one, or memory), drafts the minimal edit, and asks the user before writing anything.
---

# self-improve — from lesson to durable edit

A lesson that lives only in the conversation dies with it. This skill runs the
moment one surfaces and ends with the user approving (or declining) a concrete
edit to the place that would have prevented it.

## 1. Name the lesson

State, in one or two sentences: what went wrong (or almost did), what the
correct behaviour was, and the **mechanism** — the missing flag, the unstated
rule, the wrong default — not just the symptom. A lesson without a mechanism
is a war story; only the mechanism generalises. If the session merely feels
improvable but nothing concrete surfaced, there is no lesson yet — stop.

Owning a mistake to the user IS the firing moment: the same message that says
"here is what happened and here is the repair" names the lesson — deferring it
until the user demands durability is the failure mode this trigger exists to
close. The noise gate is severity, applied silently: a lesson is worth asking
about when the recovery required repairing state or redoing work, or when the
same mistake has now happened twice. A stumble the next tool call absorbed — a
retried command, a transient error, a wrong guess self-corrected — produces no
proposal; over-asking teaches the user to decline reflexively, which kills the
channel.

## 2. Find the home

Route by scope, most specific first:

- **An existing skill already governs the moment where it went wrong** → the
  lesson is an edit to that skill, placed at the step it should have caught.
  This is the common case; search the available skills before concluding
  otherwise.
- **No skill governs it, but the lesson will recur across sessions or
  projects** → propose a new skill (load `writing-for-agents` before drafting
  it; its invocation and pointer rules decide the frontmatter).
- **It is personal or project-local context rather than process** — a
  preference, a machine quirk, a one-repo fact → it belongs in memory, not a
  skill.
- **The environment can enforce it better than prose** — a lint rule, a CI
  check, a wrapper script, a hook → propose that instead; an enforced rule
  beats a remembered one.

## 3. Draft the minimal edit

Write the exact text (or rule/hook) you propose to add, honouring the target's
own conventions. Minimal means the mechanism and its trigger, stated
positively — what to do, at the step where it applies — plus at most one line
of the incident as evidence. A lesson is not a changelog entry: no narrative,
no apology, no restatement of what the document already says.

## 4. Ask, then apply

The user's word is the gate — always, including when the user's own message
suggested the improvement: they approve the *edit*, not the idea. Skills drift
one unreviewed "obvious" change at a time; this step is what prevents that.

Ask with the structured question tool (`AskUserQuestion` in Claude Code; plain
text where no such tool exists), shaped by the decision:

- **Home** — when more than one candidate home is defensible, a single-choice
  question listing them, each with a one-line why; the recommended one first.
- **Changes** — one question per lesson: **multi-select** when the draft
  decomposes into independent additions the user can take à la carte;
  **single-select** when the drafts are alternatives (two wordings, two
  placements — taking both would be wrong). Each option's description carries
  the proposed text verbatim or names exactly where it goes.
- **Refinements** — at most one or two extra questions, only where the user's
  answer genuinely changes the edit: scope (this project or the generic set?),
  strictness (hard rule or default-with-exceptions?), trigger breadth.

State the lesson in one line above the questions. On approval, apply exactly
the selected options and commit wherever the home is version-controlled. On
decline, drop it without residue.
