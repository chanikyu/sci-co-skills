---
name: scientific-workflow-viz
description: Use when the user wants an IMAGE PROMPT for a high-quality BioRender-style scientific figure — workflow, pipeline, mechanism, comparison, timeline, or multi-panel infographic — to paste into FigureLabs, BioRender AI, or any AI image tool. Follows a 5-step process (analyze the content → choose the design → set the components → choose the illustrations → write the prompt) with a FLEXIBLE layout (any number of panels/steps/stages; default 16:9). Triggers — "워크플로우 그림", "scheme/pipeline/mechanism figure", "BioRender 스타일", "scientific workflow infographic", or "이미지 프롬프트" for a figure/diagram. Invoke when the user asks to visualize a method/process/comparison as a figure.
---

# Scientific Workflow Viz

Produce a **ready-to-paste image prompt** for a high-quality, BioRender-style scientific figure. The primary output is a TEXT PROMPT (the user renders it in FigureLabs / BioRender AI / any AI image tool). **Optionally**, if the user provides a Google Gemini API key, you can render the prompt straight to an image with **Google "Nano Banana"** (Gemini image API) — see the section below.

The layout is **flexible** — do NOT force a fixed 3-panel structure. Choose the design that fits the content.

## The 5-step process (follow in order)

1. **Analyze the content.** Read what the figure must convey. Extract the key entities, the steps/relationships, and the single main message. If unsure about a method, read the docs/code first — never invent steps.
2. **Decide the design type.** Pick the layout that matches the content (see the menu below). The number of panels / steps / stages is whatever the content needs — 2, 3, 4, a cycle, columns, levels, etc. Do not default to 3 panels.
3. **Set the components.** Decide the concrete blocks: how many panels/steps/stages, what each one is, and how they connect (arrows, increasing scope, side-by-side, loop…).
4. **Choose the illustrations.** For each component, decide the icons / mini-diagrams (microbe cluster, abundance bar chart, DNA helix, molecule, gut-lining, matrix grid, network, table, gauge, etc.). Ground them in the real content.
5. **Write the prompt.** Assemble steps 2–4 into the house style and output it in a **plain code block (NO markdown blockquote `>`)**.

## House style (always)

- **Open with:** `A high-quality BioRender-style scientific <figure type> titled "<title>".` (figure type = "workflow infographic", "pipeline diagram", "comparison figure", "mechanism schematic", "timeline", …)
- **Aesthetic:** professional flat scientific icons; white background; dark-grey text; clean typography; soft color-coded sections with rounded borders / colored header bars; clear arrows.
- **Size:** **default 16:9** unless the user specifies otherwise (e.g. square, A4, poster).
- **Color:** distinct soft color per section, used consistently. Use the deck's brand accent if part of one (e.g. `#4A90E2` for xMeta).
- **Honesty:** ground in the real method; tag "(optional)" / "(proposed)"; don't invent stages.

## Design menu (step 2 — pick what fits, not fixed)

- **Linear pipeline** — input → step 1 → step 2 → … → output (one row).
- **Multi-panel** — 2–4 colored panels (e.g. Input / Core Workflow / Output; or Problem / Approach / Result). Panel count follows the content.
- **Comparison** — 2+ side-by-side columns, head-to-head on shared rows.
- **Stacked levels** — top-to-bottom or left-to-right by increasing scope (e.g. species → community → host).
- **Cycle / loop** — steps arranged in a circle.
- **Mechanism / network** — nodes + labeled arrows (e.g. T → M → Y mediation, cross-feeding handoff).
- **Hybrid** — e.g. a core pipeline with an optional branch, or a panel that itself contains a sub-diagram.

## Output rules

- Emit the prompt in a **plain code block (no `>` blockquote)** so it copies cleanly.
- **Always add two reminders:** (a) AI image tools render text/equations wrong → re-type labels in PowerPoint; (b) for the best style match, attach a reference figure to FigureLabs and say "match this layout".
- After the prompt, offer the optional one-command render with Nano Banana (below).

## Optional: render with Google Nano Banana (Gemini image API)

If the user wants the actual image (not just the prompt) and has a **Google Gemini API key**,
render it directly with `nano_banana.py` (in this skill dir; stdlib only, no install).

1. **Get a key** at https://aistudio.google.com/apikey (Google AI Studio).
2. **Provide it as an environment variable — never in a file, never committed.** In a Claude
   Code session the user can type: `! export GEMINI_API_KEY="<their-key>"` (or `GOOGLE_API_KEY`).
3. **Render** the prompt you produced:

```bash
python nano_banana.py --prompt-file prompt.txt --out figure.png --aspect 16:9
# or: python nano_banana.py --prompt "A high-quality BioRender-style ..." --out figure.png
```

Options: `--model` (default `gemini-2.5-flash-image`; pass a newer image model to use it),
`--aspect` (16:9 default per house style), `--api-key` (fallback if no env var).

**Security & honesty:** treat the key as a secret — read it from `GEMINI_API_KEY`, never
print, store, or commit it. The image is AI-generated, so the same caveat holds: **re-type
any labels/equations in PowerPoint** — the model still garbles text. Prefer this for quick
drafts; for a submission-grade schematic, refine the labels afterward.

## Examples (each is ONE design choice, not the only shape)

**Multi-panel workflow (3 panels):**
```
A high-quality BioRender-style scientific workflow infographic titled "How xReact works." Multi-panel, color-coded, left to right, colored header bars, rounded borders, large arrows. Flat scientific icons, white background, dark-grey text, 16:9.
PANEL (1) "Input" (light-blue): microbial community as a taxa-abundance bar chart + a chemical card "chemical (drug / diet / unknown) + dose".
PANEL (2) "Core xReact Workflow" (cream/yellow): Box 1 "Perturbation Atlas" (chemical x species grid -> growth up/down; "AGORA2 + FVA, calibrated with Maier 2018"); Box 2 "Community Rebalancing" (before/after bars; "reweight -> shifted STRUCTURE, no per-sample simulation"); Box 3 "Functional Change (xFeed)" (metabolite exchange; "shifted FUNCTION"); Box 4 (green, "optional") "Host Outcome (xHost)".
PANEL (3) "Output" (green): before->after bars + list "taxa up/down, metabolites changed".
Large arrows (1)->(2)->(3).
```

**Comparison (2 columns):**
```
A high-quality BioRender-style scientific comparison figure titled "Two routes to causal inference." Two side-by-side panels, colored headers, white background, flat icons, 16:9.
LEFT "Mendelian Randomization" (grey): instrument(SNP) -> exposure -> outcome, with a dashed red "pleiotropy" arrow and limitation badges "weak instruments", "needs large GWAS".
RIGHT "xHost" (blue): longitudinal multi-omics -> cross-lagged M(t)->Y(t+1) -> mediator->outcome, badge "E-value sensitivity".
Bottom banner: "Both observational; xHost applies where MR's instruments are too weak."
```

## Pitfalls

- **Don't force 3 panels** — match the design to the content (step 2).
- Don't over-stuff one block — split into steps/boxes.
- Captions = one short phrase; icons carry the meaning.
- Use the deck's accent color; default 16:9.
- Ground in the real method; mark optional/proposed parts.
