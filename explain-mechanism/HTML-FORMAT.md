# Page format

One self-contained HTML file: CSS inline, no script, `<details>` for the only interactive parts. A page for private material loads nothing remote. The forms are drawn by [`visualizing`](../visualizing/FORMS.md); this file says which form goes where.

## Contract

- **One look.** The bounds, measured in a headless browser at 1280 × 800 with the details closed: the answer and the whole flow are inside the first 800 px (the flow's bottom edge as the browser reports it); the rule ends under 1200 px and the page under 1500 px; the **open text**, every word outside `<style>`, `<pre>`, `<table>` and `<details>` once tags are stripped, is under 200 words. The parts' caps below are what make the bounds reachable: a page built at every cap measures 739, 1101 and 1453 px and 153 words. What does not fit goes in the notes file, linked from the details.
- **Phone width.** A 760 px column with 16 px gutters; at 390 px nothing scrolls sideways (the table and pseudocode recipes in FORMS.md are built for it).
- **Both schemes.** Tokens on `:root`, redefined under `prefers-color-scheme: dark`; `body` sets its background.
- **Cited.** Every name and number carries a cite chip: `<a class="cite" href="https://<host>/<owner>/<repo>/blob/<sha>/<path>#L12-L20">path:12-20</a>` for code the reader can open, `<code class="cite">~/private/run.txt</code>` (text, never a link) for private material. The answer line cites by part (`§rule`).
- **Accessible.** Every outcome is a word as well as a colour; text contrast checked in both schemes.

## Parts, top to bottom

| part | question it answers | form (FORMS.md) | bound |
|---|---|---|---|
| **Answer** | what happened, and what must I choose? | one sentence, then the decision in one line, then the meta line (repo @ SHA · date · `recorded run` / `reproduced` / `read only` · `PRIVATE` badge when sensitive) | 3 lines |
| **Flow** | where did the case branch? | control flow, the case's path marked, the deciding node tagged | 6 nodes, 2 exits each; a longer mechanism shows its stages and links a per-stage page from the details |
| **Rule** | what exactly decided it, on what data? | pseudocode with the case's numbers inline; under it, the types or fields the predicate reads | 8 lines + 7 lines |
| **Options** | what could change it? | table: option · changes · cost · reversible; the recommended row marked, one sentence why | 4 rows, each cell one line at desktop width (about five words); a longer "changes" goes in the notes |
| **Details** (closed) | how sure, and what else? | `<details>` holding: a gauge or table of the variants when there was an ablation; the reach as a table (surface · reached? · who · evidence); the evidence line (what ran, when, cost); the link to the notes file | — |

Drop the variants when nothing was ablated. Everything else stays in every page.

The flow and the rule show the same path on purpose: the flow is where the reader finds the branch, the rule is where they compute it. A reader who can do both can predict the next input.

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
body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 var(--sans); }
main { max-width: 760px; margin: 0 auto; padding: 20px 16px 32px; }
h1 { font-size: 1.3rem; margin: 0 0 2px; }
h2 { font-size: .9rem; margin: 14px 0 6px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.meta { font-size: .85rem; color: var(--muted); margin: 0; }
.answer { border-left: 3px solid var(--accent); padding: 2px 12px; margin: 10px 0; }
.answer p { margin: 6px 0; }
.decision { font-weight: 600; }
pre, code { font-family: var(--mono); font-size: 0.88em; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; margin: 6px 0; line-height: 1.4; }
.cite { font: 12px var(--mono); color: var(--accent); }
a.cite { white-space: nowrap; }
code.cite, td .cite { white-space: normal; overflow-wrap: anywhere; }
tr.rec { background: var(--good-bg); }
details { margin-top: 20px; border-top: 1px solid var(--rule); padding-top: 8px; }
summary { cursor: pointer; color: var(--muted); }
/* then the flow, pseudo, table and gauge rules from visualizing/FORMS.md */
</style>
</head>
<body><main>
<h1>Why the limiter rejected the burst</h1>
<p class="meta">repo @ a1b2c3d · 2026-10-30 · reproduced</p>
<div class="answer"><p>The fourth request in the burst took the count past the limit of 100 (<a class="cite" href="#rule">§rule</a>).</p>
<p class="decision">Decide: raise the limit (A), count per route (B), or accept it (C). Recommended: B.</p></div>
<h2>Flow</h2> …
<h2 id="rule">Rule</h2> …
<h2>Options</h2> …
<details><summary>Details: variants, reach, evidence, notes</summary> …</details>
</main></body>
</html>
```

## Build

Generate the page from the notes file instead of typing it: citations as short tokens (`{C:path:12-20}`) expanded by one helper that holds the pinned commit; every gauge dot and variant row read from the recorded run output, never retyped. Template, helper, notes and output stay together; for sensitive material that is the same private directory.
