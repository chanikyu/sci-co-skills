---
name: bioinfo-tool-builder
description: 'Use when the user wants to CREATE a new bioinformatics program / algorithm / tool from a research goal — not just run an existing pipeline. Autonomously drives research → gap analysis → algorithm design → feasibility proof → scale-up → honest benchmark, using deep parallel subagent analysis of papers and existing tools, conda-isolated development, and two-lens review (code + pipeline flow). Triggers — "bioinformatics 프로그램/도구/알고리즘 만들어줘", "새 방법 개발", "기존 도구보다 나은 X 만들자", "build a bioinformatics tool", "novel method for …". NOT for running existing analysis skills (amplicon / shotgun / genome / strain-typing / amr-profiling) or plotting.'
---

# Bioinfo Tool Builder

Take a bioinformatics-tool **goal** and drive it end to end — research → gap → algorithm design →
feasibility proof → scale-up → **honest benchmark** — mostly **autonomously**. Survey papers and
existing tools **deeply with parallel subagents**, develop in **conda-isolated** envs, keep code
**as simple as possible**, and **review both the code and the pipeline flow**. Interrupt the user
**only at 4 critical gates**.

## Design philosophy — effortless tools (low friction)

**The #1 goal is a tool users adopt without burden** — not just correct/fast, but *easy*. This is a
first-class success criterion (in Phase 0 requirements, checked in the flow review, required at G4):

- **One-command install** — conda / pip / a single container or binary. No dependency hell.
- **Sensible defaults + auto-detect** — works out of the box; minimal required args; the user should
  not have to tune many knobs to get a good result.
- **Standard IO** — accept FASTA / FASTQ / BAM / VCF / GFF; never force a custom format or manual
  preprocessing.
- **Required: a one-command CLI** (standard-format in → result out) + `--help`; a Python API
  additionally where it helps; **actionable error messages** (validate inputs, fail fast, say how to
  fix) — not cryptic stack traces. **No CLI → not done.**
- **Minimal / auto DB handling** — auto-download or a one-liner; never "go find and format this DB yourself".
- **Laptop-friendly by default** — runs on a typical machine for typical inputs; clearly says when it
  needs a cluster/GPU; progress output for long runs.
- **Quickstart that just works** — a README with a copy-paste example + tiny example data; a container
  for portability.

Low friction + a one-command CLI is a **required floor** (table stakes) — necessary, but NOT what
beats the competitors. The win over competitors must be in **overall performance** (see Win condition).

## Win condition — closer to the truth than the competitors (CLI required)

"Better performance" means **the tool's results are closer to the ground truth than the competing
tools' results.** Accuracy against a trustworthy truth is the **PRIMARY** criterion.

- **Trustworthy ground truth first (R1).** The benchmark needs real / curated / experimental truth (or
  exact simulated truth as a controlled proxy). "Closer to reality" is only meaningful against a truth
  you trust — otherwise → **G1 STOP**.
- **Run the actual competitor tools** (each in its own pinned env, R2) on that benchmark and **compute
  each tool's error vs the truth**. The built tool wins only if its **error is lower (closer to the
  truth)** than the competitors', **across conditions**, verified with **multi-seed confidence
  intervals** (must exceed noise). A win on one condition while losing others is **not** a win.
- **Speed / memory are secondary** (tie-breakers; must not badly regress). **A one-command CLI + low
  friction is a REQUIRED floor** — necessary, but being easier or faster does **not** substitute for
  being more accurate.
- **Not closer to the truth than the competitors → STOP** and say so plainly; never sell a usability-,
  speed-, or single-condition win as "better than the competitors."

## When to use / not

- **Use** when the user wants to *build* something new: a novel method, an algorithm, a tool that
  should beat or fill a gap left by existing tools.
- **Not** for running the existing analysis skills (`amplicon-analysis`, `shotgun-analysis`,
  `genome-analysis`, `strain-typing`, `amr-profiling`) or for making figures (`scientific-data-viz`).

## Autonomy & the 4 gates (interrupt ONLY here)

Auto-proceed through everything; surface to the user **only** at these branch points:

- **G1 — not evaluable:** no measurable success metric / benchmark can be defined → ask.
- **G2 — reuse / wrap / build:** three outcomes — (i) an existing tool already solves it → **reuse**,
  stop; (ii) the *algorithm* exists but the gap is **usability / interface / integration** → **wrap or
  extend** it into a low-friction tool (often the highest-value outcome, per the design philosophy) —
  don't rebuild the algorithm from scratch; (iii) a genuine algorithmic gap → **build new**. **Resolve
  G2 before starting the POC** — never build from scratch when a wrapper suffices.
- **G3 — Go/No-Go:** POC vs the **actual competing tools** (SOTA), not just a trivial baseline →
  proceed only if it's **more accurate — closer to the ground truth — than the competitors**; else stop.
- **G4 — final:** the honest benchmark report (wins / losses / limits).

Everything between gates runs without asking. Before any **heavy install or large compute job**,
report the resource estimate and confirm (suite convention).

## Pipeline (phases)

### Phase 0 — Goal → precise problem + evaluation FIRST
- Convert the goal into `{inputs, outputs, constraints (scale / runtime / accuracy), ONE primary
  success metric}`.
- Secure a **benchmark** (dataset with ground truth + metric) using the **truth tiers** below.
  Write `spec/problem_def.md` + `spec/benchmark/`. → **G1** if no tier is reachable.

### Phase 1 — Landscape (deep, parallel subagents)
- Fan out subagents: (a) **papers** (bioRxiv / PubMed / Semantic Scholar / Scholar via web + Exa),
  (b) **existing tools** (GitHub / Bioconda / PyPI / registries). Each returns *structured* findings:
  method, assumptions, complexity (time/mem), IO formats, benchmark used, known limitations.
- Synthesize → `survey/taxonomy.md` + `survey/sota_baseline.md` + the candidate **gap**.
- → **G2** (reuse / wrap / build): reuse if already solved; **wrap/extend** if only the
  usability / interface is the gap; build new only for a real algorithmic gap. Resolve before coding.

### Phase 2 — Gap → strategy + algorithm
- State the specific limitation exploited (the differentiator).
- Design the algorithm + **complexity analysis** + **IO/format contract** (FASTA/FASTQ/BAM/VCF/GFF).
- List assumptions + failure modes; pick the **riskiest assumption**. Write `design/`.
- Write an explicit **implementation plan** `design/plan.md` — the **build order** (module by module,
  in dependency order), each item's **dependency** + **done-criterion (the test that must pass)**, and
  which item **de-risks the riskiest assumption first**. Keep pieces small (KISS); note which standard
  libraries to reuse instead of hand-rolling; the CLI is a listed deliverable. The POC (Phase 3) builds
  the riskiest item first.
- → **Flow review (lens A) BEFORE any coding** (see Review layer).

### Phase 3 — Feasibility (de-risk first)
- Create the **project dev env** (see Environment strategy). Test the **riskiest assumption first**
  on **tiny, known-answer** data. Build the POC (simplest thing that could work).
- Compare POC vs the SOTA baseline on the benchmark metric. → **Code review (lens B)**.
- → **G3** Go/No-Go. No → STOP with the reason (never force scale-up).

### Phase 4 — Scale-up (correctness → then speed)
- Validate on progressively larger / realistic data; multiple datasets + ablations vs SOTA;
  **held-out validation** (avoid overfitting the dev benchmark).
- **Reproducible packaging** (pinned `environment.yml`, tests, versions, docs, `MANIFEST.md`)
  **+ the low-friction UX** (one-command install, sensible defaults, `--help`, quickstart README +
  tiny example data, container, actionable errors — see Design philosophy).
- → **Code review + final Flow review** (both also check the usability bar), then **G4** honest
  report (no cherry-picking; usability weighted alongside accuracy/speed).

## Deep survey — how to fan out

Launch several subagents **in parallel** (one message, multiple Agent calls). Give each a distinct
lens (one search angle each: by method family, by tool registry, by benchmark, by application).
Each returns a small structured summary, not raw dumps. Synthesize into the taxonomy + SOTA + gap.
A completeness critic subagent asks "what's missing?" and its gaps become another round.

## Code simplicity (mandate)

- **KISS / DRY / YAGNI** — the **simplest code that passes the tests**; no speculative generality.
- Prefer **battle-tested libraries / existing tools** over hand-rolled code (check Bioconda / PyPI
  first); standard libs (Biopython, pysam, scikit-bio, numpy, pandas) over custom parsers; standard
  IO formats — don't invent formats.
- Every implementation gets a **simplification pass** (code-simplifier): dead code out, flatten
  nesting, small focused files (<~400 lines), clear names. **Modify minimally** (smallest diff).

## Review layer (two lenses, independent subagents)

CRITICAL / HIGH findings **block the next gate** until fixed.

- **A — Pipeline-flow review (logic / architecture):** algorithm sound? assumptions valid?
  complexity OK for target scale? data flow correct, **no train/test leakage**, benchmark fair, SOTA
  reproduced correctly? gates placed right? **does the flow actually test the claim it makes?** Runs
  **after Phase 2 (before coding)** and again **at the end**.
- **B — Code review (implementation):** correctness, edge cases, error handling, security (untrusted
  input / file paths); **is there a simpler way?**; naming; focused files; tests present + meaningful.
  Use a language reviewer (e.g. `python-reviewer`) + `code-simplifier`. Runs **after each implementation**.

## Environment strategy (conda — isolated per concern)

- **Project dev env `scico-build-<tool>`** — created once the design fixes language + deps (start of
  the POC). All development / tests / runs go through `conda run -n scico-build-<tool>`. Its pinned
  `environment.yml` is the reproducibility artifact.
- **Baseline envs** — each SOTA tool in its **own** version-pinned env/container (fair comparison,
  no dependency clashes).
- **Simulator / benchmark envs** — read simulators (ART, CAMISIM, …) and data tooling in conda too.
- Just-in-time; **confirm heavy installs first**; log every command.

**Lifecycle / cleanup:** specs are **always preserved** (write each env's `environment.yml` + versions
+ data checksums + commands to `package/MANIFEST.md` before any removal → reproducible even if deleted).
**Keep** the project dev env (it's the tool's runtime). **Transient** baseline / simulator envs: after
the benchmark is recorded, report their disk footprint and **offer to remove (user confirms)**. Never
auto-delete without confirmation.

## Risk mitigations (built in)

- **R1 — benchmark absence → truth tiers** (use the highest reachable): 1) established community
  benchmark with truth (CAMI/CAMISIM, GIAB, Zymo mock, BUSCO, …); 2) **simulate data with known
  truth** (ART, wgsim, InSilicoSeq, CAMISIM, BadRead) — always available; 3) orthogonal proxy /
  multi-tool consensus (label as proxy, not truth); 4) invariant / known-property checks. No tier →
  **G1 STOP**. Runtime/memory are always measurable.
- **R2 — compute/data → two-scale:** a **tiny tier** that always runs locally (POC + tests + CI) and
  a **full-scale tier** run only after G3, with a resource estimate reported first. Reproduce each
  baseline in its own pinned env; a baseline that won't run → report **"unavailable"**, never fake its
  numbers. Fetch public data (SRA/ENA, Zenodo) with checksums + provenance.
- **R3 — trust the numbers → no-claim-without-test:** a metric is reported only if it comes from the
  tested harness on the defined benchmark; else labeled *unvalidated*. Harness = known-answer unit
  tests + invariant/property tests + differential tests vs a trusted tool + regression fixtures +
  **null/sanity baselines** (random / majority) + strict dev vs **held-out** split. Every "we beat
  SOTA" claim is **adversarially verified** by an independent subagent trying to refute it (leakage,
  overfit, unfair baseline params, metric misuse, off-by-one) — it survives only if refutation fails.

## ML / deep-learning mode (when the tool needs it)

Same phases + gates; these ML-specific rules apply on top.

- **Escalate only if needed (KISS):** always try a **classical baseline first** — a non-ML method
  and a simple ML model (logistic regression / random forest / gradient boosting on features) —
  **before** deep learning. DL must **beat the simple baseline beyond noise (multi-seed)** or you
  ship the simple one. Don't use DL for DL's sake (STOP).
- **Leakage-controlled splits (CRITICAL — biology-specific):** random splits **leak**. Split by
  **sequence homology/identity** (cluster with MMseqs2 / CD-HIT, split by cluster) or by organism /
  taxon / time / chromosome / patient — whatever stops near-duplicates crossing train↔test. The
  **flow review (lens A) checks this explicitly**; a **shuffled-label sanity run** (must score
  ≈ random) catches hidden leakage.
- **Scarce labels → transfer, not scratch:** fine-tune a pretrained foundation model
  (ESM-2 / DNABERT-2 / Nucleotide Transformer / scGPT …) or use self-supervised / augmentation /
  few-shot instead of training a big model from little data.
- **Task-appropriate metric:** imbalanced data → **AUPRC / MCC / per-class**, not raw accuracy;
  check **calibration** if probabilities are used.
- **Evaluation rigor (extends R3):** fixed seeds + deterministic; **nested CV** when tuning
  (outer = evaluation, inner = tuning); held-out judged **once**; train/val curves for overfitting;
  **multi-seed mean ± sd + CI** so a "DL wins" claim isn't within noise; null baselines
  (majority-class, shuffled-label). Adversarial verify also checks: homology leakage, tuning on
  test, seed / best-of-N cherry-picking, metric misuse.
- **Compute (extends R2):** DL needs a **GPU**. Tiny tier = CPU-runnable subset / tiny model for POC
  + tests + CI; full training = GPU, with **GPU-hours / VRAM estimate reported + confirmed first**.
  No GPU available → prefer fine-tuning / classical ML, and state that full training was not run.
- **Env:** the dev env adds `pytorch` (+ cuda when a GPU is present); seeds, config, data splits, and
  model weights are recorded in `package/MANIFEST.md`. Deliver a **model card** (task, training data,
  splits, limits, biases) at G4.

## Honesty / STOP conditions

- Existing tool suffices → STOP, reuse (G2). POC fails the gate → STOP with the reason (G3).
- Report benchmark **losses**, not just wins; state every assumption + threshold.
- Never claim improvement without a truth source; never fabricate a baseline's numbers.

## Output structure (per project)

```
<project>/
  spec/       problem_def.md, benchmark/ (data + ground truth + metric)
  survey/     papers.md, tools.md, taxonomy.md, sota_baseline.md
  design/     algorithm.md (+ complexity, IO contract), plan.md (build order + done-criteria), risks.md, flow_review.md
  poc/        code + results_vs_baseline.md, code_review.md
  scaleup/    implementation/, benchmark_report.md
  package/    environment.yml (pinned), tests/, MANIFEST.md (envs + data provenance), docs
  logs/       per-phase logs (subagent outputs, tool runs)
  report.md   executive summary + go/stop decisions at each gate
```

Use `scaffold.py` to create this structure:

```python
import sys; sys.path.insert(0, "/Users/kyukyu/.claude/skills/bioinfo-tool-builder")
import scaffold
scaffold.scaffold("/path/to/project", tool_name="my-tool", goal="…")
```

## Operating procedure (every run)

1. **Scaffold** the project dir (`scaffold.py`).
2. **Phase 0** — problem_def + benchmark (truth tiers). → G1 if not evaluable.
3. **Phase 1** — parallel-subagent survey → taxonomy + SOTA + gap. → **G2** reuse / wrap / build
   (resolve before any POC).
4. **Phase 2** — algorithm + complexity + IO contract + **implementation plan (`plan.md`)** + riskiest assumption. → **flow review**.
5. **Phase 3** — dev env; de-risk; POC; vs baseline. → **code review** → G3 Go/No-Go.
6. **Phase 4** — scale-up; held-out; package; MANIFEST. → **code + flow review** → G4 report.
7. **Cleanup** — offer to remove transient baseline/simulator envs (specs preserved); keep dev env.
