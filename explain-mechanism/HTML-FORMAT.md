# Page format

The page is one self-contained HTML file: CSS and SVG inline, no script. `<details>` handles the one interactive element, the reveal. When a visual truly needs a library, load one pinned exact version from a public CDN, but a page with no script is better: it opens anywhere, offline, years later.

## Contract

- **One file.** No sibling assets, no web fonts, no images other than inline SVG.
- **Both colour schemes.** Colours are CSS tokens on `:root`, redefined under `@media (prefers-color-scheme: dark)`. `body` sets its own background. SVG strokes and fills use the same tokens (`stroke="var(--ink)"`), so diagrams flip with the page.
- **Phone width.** A content column of about 760px with 16px side gutters. No horizontal page scroll: a wide table sits in its own `overflow-x: auto` wrapper, `pre` wraps, private path chips wrap, and SVGs carry a `viewBox` with `width: 100%`. Text that must stay readable lives in HTML, never inside a scaled SVG: at 390px a 720-wide `viewBox` halves its font size.
- **Accessible.** Every outcome is a word (ASK, PASS, FAIL) as well as a colour. Every SVG has a `<title>`. Text contrast is checked in both schemes.
- **Cited.** Every claim carries a citation chip (format below). A claim with no chip does not go on the page.

## Section order: the teach order

Each section answers one question, introduces at most one new term, and uses only terms already introduced.

| # | Section | Answers | Visual |
|---|---|---|---|
| 0 | Header | What is this page, how sure is it? | title, one-line answer, meta line, evidence badge |
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
- **One-line answer** directly under the title.
- **Meta line:** repo @ short SHA, date, and the evidence basis: `recorded run`, `reproduced`, or `read only`.
- **Badge** for sensitive material: `PRIVATE — do not publish`.

## Visual vocabulary

Use these visuals, and invent a new one only when none fits.

- **Step strip.** A row of numbered boxes, one per step, wrapping on narrow screens (flex with `flex-wrap`). Under each box, the case's value at that step, in monospace. Mark the deciding step with the accent border and a label.
- **Rule card.** The predicate in monospace, then one row per constant: name, value, where it is set (cite chip), measured or placeholder.
- **Gauge.** A number line for the rule's quantity, with the threshold as a dashed marker and one dot per observation. Repeats of the same input are separate dots on one row, so variance shows at a glance. Build it in HTML (snippet below): a two-column grid with the row labels as text and the dots positioned by `left: <value>%`, so labels wrap and dots stay round at any width. Mark each dot's side of the threshold by its shape (filled or hollow) as well as its colour, and give each row its values in words for screen readers.
- **Contrast table.** Columns: variant, the one edit from the case, result, value. Sort it so each flipping pair sits on adjacent rows. Tint the rows the mechanism gets wrong.
- **Reach grid.** One row per surface (input class, call site, agent, tier, configuration). Columns: reached?, the other control in front of it and its condition, evidence.
- **Options matrix.** One row per option. Columns: what changes, fixes (evidence row ids), leaves, cost, reversible. Mark the recommended row and state why in one sentence below the table.
- **Decision block.** A bordered box at the end: the question, the options lettered A–D, the recommendation, and what the decision blocks or unblocks.

## Citation chips

- **Public code:** a link to the file at the pinned commit, labelled with the path and line: `<a class="cite" href="https://<host>/<owner>/<repo>/blob/<sha>/<path>#L12-L20">path:12-20</a>`.
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
.cite { font: 12px var(--mono); color: var(--accent); white-space: nowrap; }
.strip { display: flex; flex-wrap: wrap; gap: 8px; }
.step { flex: 1 1 130px; border: 1px solid var(--rule); border-radius: 8px; padding: 8px; background: var(--panel); }
.step.decides { border: 2px solid var(--accent); }
.decision { border: 2px solid var(--accent); border-radius: 10px; padding: 16px; }
.gauge { display: grid; grid-template-columns: minmax(110px, 36%) 1fr; gap: 2px 10px; align-items: center; font-size: .82rem; }
.track { position: relative; height: 20px; margin: 0 8px; background: linear-gradient(var(--rule), var(--rule)) center / 100% 1px no-repeat; }
.track .tau { position: absolute; top: 0; bottom: 0; border-left: 1px dashed var(--accent); }
.track i { position: absolute; top: 50%; width: 11px; height: 11px; margin: -5.5px 0 0 -5.5px; border-radius: 50%; }
.track i.above { background: var(--good); }
.track i.below { background: var(--panel); border: 2.5px solid var(--bad); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
</style>
</head>
<body><main>…</main></body>
</html>
```

One gauge row, threshold at 0.5 on a 0–1 scale; a value `v` sits at `left: v × 100%`:

```html
<div class="gauge" role="img" aria-label="Score per variant against a threshold of 0.5">
  <div>Case, two repeats</div>
  <div><div class="track"><span class="tau" style="left:50%"></span>
    <i class="below" style="left:40%"></i><i class="above" style="left:55%"></i></div>
    <span class="sr">0.40 below · 0.55 above</span></div>
</div>
```

## Build

Generate the page instead of typing it. Write citations in the source as short tokens (for example `{C:path:12-20}`) and expand them with one helper that holds the pinned commit, so the SHA is set once and every link agrees. Draw every gauge and contrast row from the recorded run output by script, never from numbers retyped by hand. Keep the template, the helper and the output together: for sensitive material that means the same private directory.
