---
name: explain-mechanism
description: Explain one mechanism by tracing one concrete case through it, as a single visual HTML page that ends in a decision. Use when the user asks to explain how X works, why X failed or missed a case, or to show them the mechanism behind a behaviour, and wants to understand it or decide on it rather than have it fixed. One mechanism, one case; a whole layer's inventory belongs to architecture-report.
---

# Explain Mechanism

One **mechanism**, one **case**, one page, one **decision**. The reader leaves able to predict what the mechanism does with an input they have not seen yet, and able to choose between the options at the bottom of the page.

A question one function answers in a few sentences gets a chat answer; this skill is for a mechanism spanning several steps, a failure, or a decision.

| | architecture-report | explain-mechanism | diagnosing-bugs |
|---|---|---|---|
| Scope | a whole layer | one mechanism | one bug |
| Driven by | the inventory | one concrete case | a red feedback loop |
| Ends with | the description | a decision for the reader | a fix, built |

When the user wants the fix built, hand over to `diagnosing-bugs` after the decision is made. This skill builds nothing.

## The case

The **case** is a real input that exercises the mechanism: a failing row from a run, a log line, a fixture, a reported request. Every section of the page traces the same case, so the reader learns one path well instead of many vaguely. If the user names no case, pick the input that best shows the behaviour they asked about and say why you picked it. A "how does X work" question with no failure still gets a case: the representative input, plus the variant nearest the rule's threshold.

## Process

### 1. Pin the question

Write three lines before reading any code:

- **Mechanism:** the entry point and the point where the outcome is decided.
- **Case:** the input, verbatim or redacted, and where it came from.
- **Decision:** what the reader must choose. "None, understanding only" is allowed; the options section then becomes "what would change the outcome".

Then classify the material (see [Sensitivity](#sensitivity)). The class decides where every file goes and what you may run, so it comes first. For sensitive material, name the one target its runs may reach in the same three lines.

Done when: the three lines exist and the sensitivity class is set.

### 2. Trace the case

Read the source at one pinned commit and record its SHA. Confirm the SHA is reachable on the remote (`git branch -r --contains <sha>` is non-empty) before using link chips; if it is not, cite with the local-path chip form instead. Walk the case from the entry point to the step that decides its outcome. For each step, write down what the case looks like as it enters, what the step does to it, and `path:line`. Read the configuration that sets the step's behaviour, the test that pins it and the fixture the case came from, and cite each of them.

Evidence is often taken at a different seam from the one production runs: a test or an eval may call the deciding step directly, on an input built the way production would build it. Say which steps the evidence covers and which you only read.

Done when: every step from entry to outcome has a citation and the case's own value at that step, and each step is marked as measured or read. "Data flows through" is not a value.

### 3. Extract the rule

Write the exact predicate the deciding step evaluates, in code form. For every number in it, give its value, where it is set (a constant, config, an environment default), and whether anyone measured it or it is a placeholder. Then put the case's own numbers next to the rule.

Done when: a reader could compute the case's outcome by hand from the rule and the case's numbers.

### 4. Diagnose

Skip this step when nothing fails or surprises. Otherwise, use the strongest evidence you can get: a recorded run beats a reproduction, and a reproduction beats a reading of the code.

When a reproduction is cheap and permitted, **ablate**: change one feature of the case at a time and run each variant. The variant pairs where one edit flips the outcome are the diagnosis. For the feature you suspect, run three controls: remove it, swap it for something neutral of the same size, and move it. Together they tell content apart from length and from position. Repeat each variant at least twice and report the rate (k of n), not one verdict. A case that sits on the threshold and flips from run to run is a different finding from one that fails every time, and the fix differs too.

Before the first call, write the target into the script and have the script refuse to run anywhere else. Environments fall back silently, and a run against the wrong target measures nothing. Have the script print each variant's definition next to its result, so a later edit to the script cannot orphan earlier output. Record the UTC time and cost of each run.

State the cause in one sentence, using the variant pairs as evidence.

Done when: the cause is pinned by at least one contrast pair (the case fails, a one-edit variant passes), or it is plainly marked as inferred from reading.

### 5. Map the reach

List what else the same weakness reaches: the other inputs your variants exposed (a variant that fails and that no existing test or fixture covers is the most important row: propose it as a new one), the other call sites, agents, tiers or configurations that run the same rule, and the other controls that stand in front of it, each with the condition under which it applies. Say who is affected.

Done when: every reach row cites evidence (a run or a `path:line`) or is marked unmeasured.

### 6. Lay out the options

Write two to four options. For each one: what changes and where it would land (`path:line`), which rows of the evidence it fixes, which it leaves, what it costs (code, latency, money, false positives), and how reversible it is. Include "accept the risk" when that is a legitimate choice, and reject options the evidence rules out with one line each. Make one recommendation and say why.

Done when: every option is scored against the same evidence rows and one is recommended.

### 7. Render the page

Build the page by following [HTML-FORMAT.md](HTML-FORMAT.md). The sections follow the **teach order**: each one builds only on what came before it, so the reader is never asked to hold a term that has not been introduced. Every visual replaces a paragraph, and takes the most compact form that carries its question (HTML-FORMAT.md, "Picking the form"). A section's prose stays at three sentences or fewer, and a sentence that could be a table row becomes one.

Done when: every section in the teach-order table is present or dropped by its stated rule, every gauge and contrast row is generated from the recorded output files (the build reads them, not a copy), and the build leaves no unexpanded citation token.

### 8. Verify and deliver

Re-open every cited `path:line` and confirm it still says what the page claims. Check that the tags balance. Run a terms pass: list each term at its first use, and fail on any term used before the section that introduces it. If a headless browser is available, screenshot the file at the path you deliver, after its last write — 390px wide in the light scheme and desktop width in the dark scheme — then look at both: unreadable labels, clipped chips, a table that needs sideways scrolling, and squashed shapes only show up there. Screenshots of sensitive material go in the same private directory. For sensitive material, confirm the file's mode with `ls -l`. Then give the user the absolute path, the one-line answer and the decision being asked for.

Done when: every citation has been re-read, every term is introduced before its first use, and the path delivered.

## Sensitivity

Material is **sensitive** when it holds a security weakness that is not yet fixed, real personal or company data, credentials, or measurements the user keeps private. For sensitive material:

- The page and every working file (scripts, run logs, scratch notes) go to the private local directory the user or the project's instructions name for private material; if none is named, ask once before writing anything. Create them under a restrictive umask (`umask 077`), check `ls -l` shows owner-only access, keep them outside any repository, and keep them out of shared temporary directories.
- A reproduction may send the case only to a target the material is already allowed to reach. That target is named in step 1, and the step 4 script asserts it and refuses every other one.
- Screenshots use a local headless browser on a `file://` URL. Never a remote or hosted browser service, and never a server bound beyond loopback.
- A run that costs money needs the user's go, unless a standing budget covers it. This is what step 4's "cheap and permitted" means.
- A private page loads nothing remote: no CDN, no web fonts, no hosted renderer. A diagram library such as Mermaid ships from a local vendored copy kept in the same private directory.
- Nothing about it leaves the machine: no publishing, no commit, no issue or PR text. Anything written elsewhere about the work (a summary, a PR, an example in a doc) calls it "a private worked example" and borrows none of its wording, names or numbers. Invent the values for examples.
- Redact secrets everywhere, sensitive or not: write `<REDACTED>` in their place.

Everything else is written where the user asks for it. When they don't say, use the OS temp directory (`$TMPDIR`, falling back to `/tmp`; `%TEMP%` on Windows) as `<tmpdir>/explain-<mechanism>-<timestamp>.html`.

## Design record

**Convention:** every change to this skill records its date, what prompted it, and what changed. A change with no entry here is unreviewed drift.

**2026-10-28 — fix round 1 (Opus review on PR #8).** Prompted by the review's 1 BLOCKING, 6 SHOULD, 4 NIT. Sensitivity now states a run rule beside the file rule: a reproduction goes only to a target named in step 1 and asserted by the script, screenshots use a local headless browser on `file://`, paid runs need the user's go, and a private page loads nothing remote (local vendored diagram library). Narrow-screen table rule (`data-label` block cells, wrapping cites) and an outcome-named gauge with `role="group"`, axis rows, and outcome-named classes replace side-of-threshold classes. Description loses its deliverables list (the body carries them) and gains the "understand or decide rather than fix" discriminator; a one-line gate in the body keeps single-function questions in chat. Step 7 gained its Done when; step 8 gained the terms pass, sideways-scroll check, and screenshot-after-last-write; step 2 confirms the pinned SHA is on the remote before link chips. Reach grid gained a **who** column; the one-line answer and the verdict card merged into one; the README inspiration note now links its two sources.

**2026-10-28 — v1.** Prompted by the owner's request for a skill that explains one mechanism for a decision, delivered as a visual page rather than a Markdown file. Shaped by two outside ideas, rewritten here: compact visual representations in place of prose (HumanLayer's `show-me`) and building understanding one step at a time towards a concrete win (Matt Pocock's `teach`). Kept distinct from `architecture-report`: one mechanism traced through one case towards a decision, not a layer's inventory. Dogfooded on a private worked example before review, which added: marking which steps the evidence measured (step 2), the three ablation controls, rates over verdicts and variant definitions printed with results (step 4), uncovered failing variants as reach rows (step 5), the headless screenshot check (step 8), the no-borrowed-values rule for examples (Sensitivity), and HTML rather than SVG gauges (HTML-FORMAT.md).
