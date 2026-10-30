---
name: explain-mechanism
description: Explain one mechanism by tracing one concrete case through it, as one visual page read at a glance that ends in a decision. Use when the user asks to explain how X works, why X failed or missed a case, or to show them the mechanism behind a behaviour, and wants to understand it or decide on it rather than have it fixed. One mechanism, one case; a whole layer's inventory belongs to architecture-report.
---

# Explain Mechanism

One **mechanism**, one **case**, one page read **at a glance**, one **decision**. The reader leaves able to predict what the mechanism does with an input they have not seen, and to choose between the options at the bottom. The page carries what one look needs; everything found on the way goes in a notes file beside it, linked from the page's details.

A question one function answers in a few sentences gets a chat answer. When the user wants the fix built, hand over to `diagnosing-bugs` after the decision; this skill builds nothing.

| | architecture-report | explain-mechanism | diagnosing-bugs |
|---|---|---|---|
| Scope | a whole layer | one mechanism | one bug |
| Ends with | the description | a decision for the reader | a fix, built |

## Process

Investigate fully, show little. Steps 1 to 4 fill the notes file; step 5 draws the page from it.

1. **Pin.** Three lines before reading code: the **mechanism** (entry point to the step that decides the outcome), the **case** (a real input, verbatim or redacted, and where it came from; with no failure, the representative input plus the variant nearest the rule's threshold), the **decision** the reader must make ("what would change the outcome" when there is none). Classify the material ([Sensitivity](#sensitivity)); it decides where every file goes. Done when: the three lines and the class exist.
2. **Trace.** At one pinned commit (SHA recorded, confirmed on the remote with `git branch -r --contains` before any code link), walk the case from entry to the deciding step: the case's value entering each step, what the step does, `path:line`, and whether a run measured it or you read it. Read the configuration that sets the rule's constants, the test that pins it and the fixture the case came from. Done when: every step has a cite and the case's own value, marked measured or read.
3. **Extract the rule.** The deciding predicate in code form; for each constant its value, where it is set, and measured or placeholder; the case's numbers beside it; the types or fields the predicate reads. Done when: a reader could compute the case's outcome by hand.
4. **Diagnose and weigh.** Skip when nothing fails or surprises. Otherwise **ablate** when a reproduction is cheap and permitted: one edit per variant; for the suspect feature, remove it, swap it for a neutral one of the same size, move it; at least two runs each, reported as k of n. The script carries its target and refuses any other, prints each variant's definition beside its result, and records UTC time and cost. Then the **reach** (other inputs, call sites, tiers that run the same rule, and who is affected) and two to four **options**, each scored against the same evidence rows with cost and reversibility, one recommended. Done when: the cause is pinned by a flipping pair or marked as read-only inference; every option is scored.
5. **Render.** Build the page from the notes by following [HTML-FORMAT.md](HTML-FORMAT.md), then screenshot it with a local headless browser at 390 px light and desktop dark, after the last write. Re-open every cite. Done when: the page fits one desktop screen with its details closed, its open text is under 200 words, both screenshots were looked at, every cite still says what the page claims, and the user has the absolute path, the one-line answer and the decision asked. When the case was an item on a syncing board, record the path on that item.

## Sensitivity

Material is **sensitive** when it holds an unfixed security weakness, real personal or company data, credentials, or measurements the user keeps private. Then: page, notes, scripts and screenshots go to the private local directory the project names for private material (ask once if none is named), created under `umask 077`, outside any repository; a reproduction reaches only the target named in step 1, and a paid run needs the user's go unless a standing budget covers it; screenshots come from a local headless browser on `file://`; the page loads nothing remote, a diagram library ships as a local vendored copy; nothing about it leaves the machine, and anything written elsewhere calls it "a private worked example" with invented values. Secrets are `<REDACTED>` everywhere, sensitive or not.

Everything else goes where the user asks, else `<tmpdir>/explain-<mechanism>-<timestamp>.html` with its notes beside it.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-30 — at a glance.** Prompted by the owner: pages ran to ten dense sections, which is the chat answer again in another format, and lacked control flow, pseudocode and data shapes. The page is now five parts on one screen (answer, flow, rule with its data shapes, options, collapsed details) with a 200-word bound, and the investigation moves to a notes file the details link; the lesson from Matt Pocock's `wait-what` applies to the skill itself, since a model copies the length of its instructions, so this file went from 110 lines to half. How each form is drawn moved to `visualizing`; this skill keeps only where each form goes. The independent review on PR #10 (11 SHOULD, 12 NIT) was folded in: one screenshot rule, one source for each section's form, cites on the flow and pseudocode, the phone table fix.

**2026-10-29 — board hook.** Prompted by the `syncing-board` skill: a mechanism page delivered for a board item is recorded on the item. One sentence in step 5.

**2026-10-28 — fix round 1 (Opus review on PR #8).** Prompted by the review's 1 BLOCKING, 6 SHOULD, 4 NIT. Sensitivity gained a run rule beside the file rule; narrow-screen table rule and an outcome-named gauge; the description gained the "understand or decide rather than fix" discriminator; step 2 confirms the pinned SHA is on the remote.

**2026-10-28 — v1.** Prompted by the owner's request for a skill that explains one mechanism for a decision, delivered as a visual page. Shaped by HumanLayer's `show-me` and Matt Pocock's `teach`, rewritten. Dogfooded on a private worked example, which added the measured-or-read marking, the three ablation controls, rates over verdicts, and the headless screenshot check.
