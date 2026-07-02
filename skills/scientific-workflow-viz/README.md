# 🧫 scientific-workflow-viz

<sub>[← SciCo-Skills](../../README.md) · a skill in the SciCo-Skills suite</sub>

Produce a **ready-to-paste image prompt** for a high-quality, **BioRender-style** scientific
figure — a workflow, pipeline, mechanism, comparison, timeline, or multi-panel infographic.
The primary output is a TEXT PROMPT (paste into FigureLabs / BioRender AI / any AI image tool);
**optionally**, render it straight to an image with **Google "Nano Banana"** (Gemini image API).

> This is the *concept-figure* sibling of [`scientific-data-viz`](../scientific-data-viz):
> use this for schematics/diagrams (no data behind them); use `scientific-data-viz` to plot
> real data.

## The 5-step process

1. **Analyze the content** — key entities, steps/relationships, single main message.
2. **Decide the design** — linear pipeline · multi-panel · comparison · stacked levels ·
   cycle/loop · mechanism/network · hybrid (panel count follows the content — never forced to 3).
3. **Set the components** — the concrete blocks and how they connect.
4. **Choose the illustrations** — icons / mini-diagrams grounded in the real method.
5. **Write the prompt** — assembled in the house style, in a plain code block.

**House style:** flat scientific icons, white background, dark-grey text, soft color-coded
sections with rounded borders / colored header bars, clear arrows, default 16:9.

## Optional: render with Google Nano Banana

If you have a **Google Gemini API key**, render the prompt directly (stdlib-only helper,
no install):

```bash
export GEMINI_API_KEY="your-key"        # from https://aistudio.google.com/apikey — never commit it
python nano_banana.py --prompt-file prompt.txt --out figure.png --aspect 16:9
```

Options: `--model` (default `gemini-2.5-flash-image`), `--aspect`, `--api-key`. The key is
read from `GEMINI_API_KEY` / `GOOGLE_API_KEY` and never stored or printed. AI-generated
images still garble text — **re-type labels/equations in PowerPoint** for a final figure.

Full rules, the design menu, and examples: **[`SKILL.md`](SKILL.md)**.
