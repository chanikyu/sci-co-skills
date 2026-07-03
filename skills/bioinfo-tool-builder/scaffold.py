"""
scaffold.py — create the bioinfo-tool-builder project structure + skeleton report / manifest.
Keep it simple: just directories and two skeleton files.
"""
import os

_DIRS = [
    "spec/benchmark", "survey", "design", "poc",
    "scaleup/implementation", "package/tests", "logs",
]

_REPORT = """# {tool} — build report

Goal: {goal}

## Gate decisions
- G1 (evaluable?):
- G2 (reuse / wrap / build):
- G3 (Go/No-Go after POC):
- G4 (final benchmark):

## Summary
_(filled at G4: wins / losses / limits, honestly)_
"""

_MANIFEST = """# MANIFEST — reproducibility ({tool})

Preserve specs so the build is reproducible even if envs are removed.

## Conda envs
| env | role (dev / baseline / simulator) | environment.yml | key versions |
|-----|-----------------------------------|-----------------|--------------|
| scico-build-{tool} | dev (kept) | package/environment.yml | |

## Data
| dataset | source (SRA/ENA/Zenodo/…) | checksum | truth tier |
|---------|---------------------------|----------|------------|

## Baseline commands
_(exact command + version + params for each SOTA baseline)_
"""

_PLAN = """# Implementation plan — {tool}

Build order (dependency order, smallest pieces first; **build the riskiest item first**):

| # | Module / file | Purpose | Depends on | Done when (test passes) |
|---|---------------|---------|------------|-------------------------|
| 1 |               |         | —          |                         |
| 2 |               |         |            |                         |

- **Riskiest assumption** de-risked by item #: __
- **POC** = the items needed to test that assumption on tiny known-answer data.
- **Reuse (don't hand-roll):** standard libs / existing tools — __
- **CLI (required deliverable):** `{tool} <input> [options]` → result; `--help`.
"""


def scaffold(project_dir, tool_name, goal=""):
    """Create <project_dir> with the standard layout + skeleton report.md and package/MANIFEST.md."""
    for d in _DIRS:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)
    with open(os.path.join(project_dir, "report.md"), "w") as fh:
        fh.write(_REPORT.format(tool=tool_name, goal=goal or "(describe)"))
    with open(os.path.join(project_dir, "package", "MANIFEST.md"), "w") as fh:
        fh.write(_MANIFEST.format(tool=tool_name))
    with open(os.path.join(project_dir, "design", "plan.md"), "w") as fh:
        fh.write(_PLAN.format(tool=tool_name))
    return project_dir
