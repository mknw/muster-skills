---
name: reviewing-changes
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow the repo's documented conventions?) and Spec (does it match what the originating issue or spec asked for?). Runs both as parallel sub-agents and reports them side by side, never merged. Use before opening a PR, when reviewing a worker's PR before merge, or when the user asks to review a branch, a PR, or work-in-progress "since X".
---

Two-axis review of the diff between `HEAD` (or a PR head) and a fixed point:

- **Standards** — does the code follow this repo's documented conventions?
- **Spec** — does it faithfully implement what was asked?

Both axes run as **parallel sub-agents** so they cannot pollute each other's
context, then this skill aggregates their findings **without merging them**.

## Relationship to the built-in `/code-review`

They answer different questions and neither replaces the other.

|          | Built-in `/code-review`                                                    | `reviewing-changes`                                            |
| -------- | -------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Question | **Is it wrong?** — correctness bugs, plus reuse/simplification/efficiency | **Is it this repo's, and is it what was asked for?**            |
| Axes     | One, effort-scaled                                                          | Two, deliberately unmerged                                      |
| Inputs   | The diff                                                                    | The diff **+ the repo's conventions + the originating spec**    |
| Can act  | Yes — `--fix` applies findings, `--comment` posts inline PR comments       | No. It reports                                                  |

**Run the built-in first** — it can fix what it finds — then this skill, to
catch convention drift and scope creep against the spec. Neither of those is a
bug, so neither is in the built-in's remit. If the user asks for "a review"
with no further qualification and the diff has not been through the built-in
yet, say so in one line and carry on; do not do the built-in's job here.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag,
`main`, `origin/main`, `HEAD~5`. If they did not specify one, default to the
default branch's remote ref (`origin/main` or `origin/master`) and say so. For
a PR, fetch its head and diff against its base.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so
the comparison is against the merge-base). Also capture the commit list with
`git log <fixed-point>..HEAD --oneline`.

Before spawning anything, confirm the ref resolves (`git rev-parse
<fixed-point>`) and the diff is non-empty. A bad ref or an empty diff fails
**here**, not inside two parallel sub-agents.

### 2. Find the repo's review map

If `docs/reviewing.md` exists, read it first. It is a **map**, not a rulebook:
pointers to where the repo keeps its conventions, its spec-resolution order,
and its gates — authoritative only for facts stated nowhere else. Follow its
pointers rather than re-deriving them.

Without one, discover from the usual suspects: `CLAUDE.md` / `AGENTS.md`,
`CONTRIBUTING`, a glossary, `docs/adr/`, the README, and any README in the
directories the diff touches. Never fail for lack of a file — a repo with no
written conventions still gets the Spec axis and the smell baseline. Either
way, the final report names which sources the Standards brief was built from.

### 3. Identify the spec source

Default resolution order (a repo's `docs/reviewing.md` may override it):

1. **Issue references in the commit messages** — `#123`, `Closes #45`.
2. **The PR body**, if a PR exists for the branch (`gh pr view --json body`).
3. **The branch name**, which often carries the number — `issue-153-neo4j-prune`.
4. A path the user passed as an argument, or a plan/spec doc matching the
   feature.

Fetch with `gh issue view <n> --comments` (fall back to `gh pr view <n>` —
GitHub shares one number space). If nothing is found, ask the user where the
spec is; if they say there is none, skip the Spec sub-agent and report "no
spec available".

**The issue body is the spec. The project board is not.** Board fields
(Status / Priority / order) are scheduling, read-only context — never a
finding.

### 4. Assemble the Standards brief

Three sources, in this order of authority:

**(a) The repo's documented conventions**, gathered in step 2. These are
**hard** — a breach is a violation, not a judgement call. Quote each
convention from its source when briefing the sub-agent; the sub-agent cannot
see the repo map or this file.

**(b) The deep-module vocabulary.** If the diff introduces or reshapes a
module boundary and a `codebase-design` skill is available, call the Skill
tool with `codebase-design` and use its vocabulary (depth, interface, seam,
leverage, locality) in the finding. If the skill is not installed, say so in
the report and fall back to plain-language boundary findings — silently
dropping the module-boundary lens is the failure mode here.

**(c) The Fowler smell baseline** below. Two rules bind it: **the repo
overrides** — where a documented standard endorses something the baseline
would flag, suppress it — and **every smell is a judgement call**, a labelled
heuristic ("possible Feature Envy"), never a violation. Skip anything tooling
already enforces (formatter, linter, type-checker).

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 5. Spawn both sub-agents in parallel

Both in **one message**, so they actually run concurrently.

**Standards** — dispatch the Agent tool with `subagent_type: code-reviewer` if
that agent type is registered (it carries the confidence gate, the
HIGH/CRITICAL-require-proof rule, and the clean-review-is-valid instruction —
restating any of that inline would fork it). Where no `code-reviewer` type
exists, degrade to a general-purpose sub-agent and carry those three rules
inline in the brief. Pass it:

- the full diff command and the commit list;
- the conventions from step 4(a), **pasted in full**;
- the smell baseline from step 4(c), **pasted in full**, with its two binding
  rules;
- the brief: _"Report — per file/hunk — (a) every place the diff breaches a
  documented repo convention: quote the convention and the hunk; and (b) any
  baseline smell you spot: name it and quote the hunk. Convention breaches are
  hard violations; baseline smells are always judgement calls and a documented
  convention overrides the baseline. Skip anything the formatter/linter/
  type-checker enforces. Under 400 words."_

**Spec** — a general-purpose sub-agent. Pass it the diff command, the commit
list, and the fetched spec text (not just its number — the sub-agent may not
have `gh` context). The brief:

> Report: (a) requirements the spec asked for that are missing or partial;
> (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements
> that look implemented but where the implementation looks wrong. Quote the spec
> line for each finding. Ignore project-board fields — they are scheduling, not
> spec. Under 400 words.

If there is no spec, skip this sub-agent and say so in the report.

### 6. Aggregate and report

Present the two reports under `## Standards` and `## Spec` headings, verbatim
or lightly cleaned. Do **not** merge, rerank, or deduplicate across them — the
two axes are deliberately separate.

End with one line: findings per axis, and the worst issue _within each axis_.
Do not pick a single winner across axes; that is exactly the reranking the
separation exists to prevent.

**Where the report lands.** When the review is of a PR, the outcome goes on
the PR as a comment: at most ~500 visible characters — verdict, severity
counts, the items that matter — with the full two-axis report in a collapsed
`<details>` block in the same comment. Whoever later applies fixes reports
what changed the same way. The PR timeline is the durable audit trail; chat
and orchestration messages are not. For a local, pre-PR review, the chat
report above suffices.

When this review is a merge gate inside a coordinated run, the
`dispatching-work` doctrine governs the surrounding loop: reviews are
coordinator-commissioned, post-review changes get a fresh reviewer on the
deltas until convergence, and the reviewer's model escalates with risk.

**This skill reports. It does not fix.** If the user wants the findings
applied, point them at the built-in `/code-review --fix` or ask them to say so
explicitly.

**Zero findings on an axis is a valid result.** Say "no findings" and move on.
Manufactured nits to justify the invocation are the primary failure mode here.

## Why two axes

A change can pass one and fail the other:

- Follows every convention, implements the wrong thing → **Standards pass, Spec fail.**
- Does exactly what the issue asked, breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately is what stops one from masking the other.
