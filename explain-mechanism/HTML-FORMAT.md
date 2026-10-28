# Page format

The page is one self-contained HTML file: CSS and SVG inline, no script. `<details>` handles the one interactive element, the reveal. When a visual truly needs a library, load one pinned exact version from a public CDN — but a page for private material loads nothing remote: a diagram library comes from a local vendored copy kept next to the page. A page with no script is better: it opens anywhere, offline, years later.

## Contract

- **One file by default.** No sibling assets, no web fonts, no images other than inline SVG. A set of sibling pages for one mechanism's neighbourhood may share one assets folder and link to each other; one mechanism stays one standalone page.
- **Both colour schemes.** Colours are CSS tokens on `:root`, redefined under `@media (prefers-color-scheme: dark)`. `body` sets its own background. SVG strokes and fills use the same tokens (`stroke="var(--ink)"`), so diagrams flip with the page.
- **Phone width.** A content column of about 760px with 16px side gutters. At 390px every column's content is visible without horizontal scrolling: table cells carry a `data-label` naming their column and turn into labelled blocks on narrow screens (scaffold below), a cite inside a cell wraps (`overflow-wrap: anywhere`), `pre` wraps, private path chips wrap, and SVGs carry a `viewBox` with `width: 100%`. The `overflow-x: auto` wrapper is the last resort, for code-like tables. Text that must stay readable lives in HTML, never inside a scaled SVG: at 390px a 720-wide `viewBox` halves its font size.
- **Accessible.** Every outcome is a word (ASK, PASS, FAIL) as well as a colour. Every SVG has a `<title>`. Text contrast is checked in both schemes.
- **Cited.** Every claim carries a citation chip (format below). A claim with no chip does not go on the page. Exception: the verdict card (§1) cites by section anchor (`§4`), which a one-sentence verdict can realistically carry.

## Section order: the teach order

Each section answers one question, introduces at most one new term, and uses only terms already introduced.

| # | Section | Answers | Visual |
|---|---|---|---|
| 0 | Header | What is this page, how sure is it? | title, meta line, evidence badge |
| 1 | The answer | What happened, in one sentence? | verdict card |
| 2 | The mechanism | What are the steps? | step strip |
| 3 | The case | What did this input look like at each step? | step strip with the case's values, deciding step marked |
| 4 | The rule | What exactly decided it? | rule card + gauge |
| 5 | Predict | Can the reader now apply the rule? | one `<details>` reveal |
| 6 | Why | Which feature of the input caused it? | contrast table + gauge with variants |
| 7 | Reach | What else does this reach, and who? | reach grid |
| 8 | Options | What could change it, at what cost? | options matrix |
| 9 | Decision needed | What must the reader choose? | decision block |
| — | Evidence | What was run, when, at what cost? | collapsed `<details>` |

Drop section 6 when nothing fails. Section 7 and the decision stay in every case: "what would change the outcome" is still a decision.

## Header

- **Title:** the mechanism and the case, in plain words ("Why the rate limiter let one burst through").
- **Meta line:** repo @ short SHA, date, and the evidence basis: `recorded run`, `reproduced`, or `read only`.
- **Badge** for sensitive material: `PRIVATE — do not publish`.

The one-line answer is the verdict card in §1, not a second line here.

## Picking the form

Per section, pick the most compact form that carries its question, and omit everything the question does not need. In ascending weight: types or signatures, pseudocode, a table, a diagram, a paragraph of prose. A structure — a component tree, a call stack, the step strip, a file layout — shows what changed with `+`/`−` marks on the structure rather than a before/after pair. HTML visuals (cards, gauges, strips) only where a lighter form does not carry it: a section one pseudocode block answers gets the block.

## Visual vocabulary

Use these visuals, and invent a new one only when none fits.

- **Step strip.** A row of numbered boxes, one per step, wrapping on narrow screens (flex with `flex-wrap`). Under each box, the case's value at that step, in monospace. Mark the deciding step with the accent border and a label.
- **Rule card.** The predicate in monospace, then one row per constant: name, value, where it is set (cite chip), measured or placeholder.
- **Gauge.** A number line for the rule's quantity, with the threshold as a dashed marker and one dot per observation. Repeats of the same input are separate dots on one row, so variance shows at a glance. Build it in HTML (snippet below): a two-column grid with the row labels as text and the dots positioned by `left: <value>%`, so labels wrap and dots stay round at any width. The container is `role="group"` with an `aria-label` — `role="img"` makes its descendants presentational, so the rows' values in words for screen readers would never be read. Name the dot classes by outcome (`.right` / `.wrong`), not by side of the threshold: which side is good depends on the rule (for an error budget it is the reverse of a score). Include an axis row — 0, threshold, max — under the dots; dots with no scale cannot be read against the threshold. Give each row its values in words for screen readers.
- **Contrast table.** Columns: variant, the one edit from the case, result, value. Sort it so each flipping pair sits on adjacent rows. Tint the rows the mechanism gets wrong.
- **Reach grid.** One row per surface (input class, call site, agent, tier, configuration). Columns: reached?, who (end users, operators, tenants — a count or rate where one was measured), the other control in front of it and its condition, evidence.
- **Options matrix.** One row per option. Columns: what changes, fixes (evidence row ids), leaves, cost, reversible. Mark the recommended row and state why in one sentence below the table.
- **Decision block.** A bordered box at the end: the question, the options lettered A–D, the recommendation, and what the decision blocks or unblocks.

## Citation chips

- **Public code:** code the reader can open at the link — the pinned SHA is reachable on the remote (step 2 confirms with `git branch -r --contains`); a SHA that is not, or a repository the reader cannot open, uses the local-path chip form instead: `<a class="cite" href="https://<host>/<owner>/<repo>/blob/<sha>/<path>#L12-L20">path:12-20</a>`.
- **Private material:** the local path as text, never a link, allowed to wrap: `<code class="cite">~/private/run.txt</code>`.
- Cite the definition rather than a call site, unless the call site is the claim.

## Predict, then reveal

After the rule, give the reader one variant of the case and ask what the rule does with it. Put the answer, with the observed value, inside `<details><summary>Reveal</summary>…</details>`. Choose the variant that shows the surprise: the one-edit change that flips the outcome.

## Scaffold

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>…</title>
<style>
:root {
  --bg: #fbfaf7; --panel: #ffffff; --ink: #1d232b; --muted: #5b6573; --rule: #d9dde3;
  --accent: #3554d1; --bad: #b42318; --bad-bg: #fde8e6; --good: #1a7f4b; --good-bg: #e3f4ea;
  --warn: #9a6200; --warn-bg: #fdf1dc;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #12151a; --panel: #1a1f26; --ink: #e6e9ee; --muted: #9aa4b2; --rule: #2c333d;
    --accent: #8ea2ff; --bad: #ff8a80; --bad-bg: #3a1d1b; --good: #6fd39b; --good-bg: #16301f;
    --warn: #f0b85a; --warn-bg: #362a14;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.55 var(--sans); }
main { max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }
pre, code { font-family: var(--mono); font-size: 0.9em; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
code.cite { white-space: normal; overflow-wrap: anywhere; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--rule); vertical-align: top; }
.cite { font: 12px var(--mono); color: var(--accent); }
a.cite { white-space: nowrap; }
td .cite { white-space: normal; overflow-wrap: anywhere; }
.strip { display: flex; flex-wrap: wrap; gap: 8px; }
.step { flex: 1 1 130px; border: 1px solid var(--rule); border-radius: 8px; padding: 8px; background: var(--panel); }
.step.decides { border: 2px solid var(--accent); }
.decision { border: 2px solid var(--accent); border-radius: 10px; padding: 16px; }
.gauge { display: grid; grid-template-columns: minmax(110px, 36%) 1fr; gap: 2px 10px; align-items: center; font-size: .82rem; }
.track { position: relative; height: 20px; margin: 0 8px; background: linear-gradient(var(--rule), var(--rule)) center / 100% 1px no-repeat; }
.track .tau { position: absolute; top: 0; bottom: 0; border-left: 1px dashed var(--accent); }
.track i { position: absolute; top: 50%; width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; }
.track i.right { background: var(--good); }
.track i.wrong { background: var(--panel); border: 2.5px solid var(--bad); }
.track-axis { display: flex; justify-content: space-between; margin: 0 8px; font-size: .75rem; color: var(--muted); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
@media (max-width: 600px) {
  td { display: block; }
  td::before { content: attr(data-label); font-weight: 600; }
}
</style>
</head>
<body><main>…</main></body>
</html>
```

One gauge row, threshold at 0.5 on a 0–1 scale; a value `v` sits at `left: v × 100%`:

```html
<div class="gauge" role="group" aria-label="Score per variant against a threshold of 0.5">
  <div>Case, two repeats</div>
  <div><div class="track"><span class="tau" style="left:50%"></span>
    <i class="wrong" style="left:40%"></i><i class="right" style="left:55%"></i></div>
    <span class="sr">0.40 wrong · 0.55 right</span></div>
  <div></div>
  <div class="track-axis"><span>0</span><span>threshold 0.5</span><span>1</span></div>
</div>
```

## Build

Generate the page instead of typing it. Write citations in the source as short tokens (for example `{C:path:12-20}`) and expand them with one helper that holds the pinned commit, so the SHA is set once and every link agrees. Draw every gauge and contrast row from the recorded run output by script, never from numbers retyped by hand. Keep the template, the helper and the output together: for sensitive material that means the same private directory.
