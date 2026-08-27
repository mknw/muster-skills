---
name: self-improve
description: Turn a lesson from this session into a durable edit — a mistake just recovered from, a user correction or countermand, rework caused by a process gap, or the user saying "this must not happen again" / "learn from this". Finds the home (an existing skill, a new one, or memory), drafts the minimal edit, and asks the user before writing anything.
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

Present to the user: the lesson (one line), the chosen home and why, and the
draft edit verbatim. Ask whether to apply it — the user may redirect the home
or trim the edit; their word is the gate. On approval, apply it, and commit it
wherever the home is version-controlled. On decline, drop it without residue.
