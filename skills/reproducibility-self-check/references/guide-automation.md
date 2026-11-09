# Automation: one command, locked and seeded

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/automation (English, 2026-11-06). Public text only; it says what is looked at, not how the platform assessment decides.

Automation removes manual work when you or others repeat the workflow: one command, locked versions, fetched inputs and recorded seeds. It is reported as an area result beside the level, not as a step toward L3.

Automation makes a workflow cheap to repeat, for you and for anyone checking it. A pinned workflow that runs with one command also supplies much of what L2 needs. The result reads complete, complete with access required (for controlled data whose retrieval is scripted for whoever has access), or the items still open. Seeds are not always enough: the [PyTorch notes](https://docs.pytorch.org/docs/stable/notes/randomness.html) warn that results can differ between CPU and GPU.

## C1 · One command produces the results

*Automation · beside the level*

**What counts.** A `Makefile`, `Snakefile`, Nextflow pipeline or `run.sh` regenerates every key result without manual or graphical steps. It may start from a deposited, documented intermediate dataset.

**What it flags.**

- Scripts in an order only you know, a graphical step, or a start from an undocumented intermediate.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Put every step into one entry point, from fetching data to the last figure. Make tracking services optional and say how to run without them:

`Makefile`:

```text
.PHONY: all data smoke
all: data results/table1.csv results/figure2.pdf

data:
	bash scripts/get_data.sh

results/table1.csv: data
	python -m analysis.table1 --out $@

results/figure2.pdf: results/table1.csv analysis/figure2.R
	Rscript analysis/figure2.R

smoke:
	python -m analysis.table1 --subsample 0.01 --out /tmp/table1_smoke.csv
```

## C2 · The software environment is pinned

*Automation · beside the level*

**What counts.** Exact versions of every package in a lock file or container, a base image pinned by digest or tag, and runtime version stated.

**What it flags.**

- Version ranges, a `latest` base image, a stale lock, or results from a runtime the pins exclude.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Lock from a clean environment that runs your analysis and produce the results in it. Containers start from a versioned base image:

```bash
# Python: lock every direct and indirect version in uv.lock
uv lock

# R: record the R version and every package version in renv.lock
Rscript -e 'renv::snapshot()'
```

## C3 · Input retrieval is automated

*Automation · beside the level*

**What counts.** The run command downloads each open input from a persistent identifier and checks its checksum; the docs say which token any protected download needs.

**What it flags.**

- Links someone must click, unzip and move by hand, or a download without a checksum.
- A download that needs an account or token nobody explains.
- Data only an access procedure provides. With scripted retrieval the result reads complete, access required.

**How to fix.** For restricted data, offer a small open subset. Call a fetch step from your one command, such as [pooch](https://www.fatiando.org/pooch/), and name the token variable:

```bash
#!/usr/bin/env bash
# scripts/get_data.sh: fetch and verify every open input
set -euo pipefail
mkdir -p data/raw
curl -fL -o data/raw/counts.csv.gz \
  "https://zenodo.org/records/0000000/files/counts.csv.gz"
sha256sum -c data/checksums.sha256
```

## C4 · Random seeds and variability are controlled

*Automation · beside the level*

**What counts.** Beyond what L2 asks of key results: every stochastic call in result code is seeded, GPU steps use deterministic settings, and remaining variation is documented.

**What it flags.**

- An unseeded random call, such as an unseeded split.
- GPU steps without deterministic settings, or a library that varies even when seeded.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Take the seed from the command line, set every generator in one place, use reproducible parallel streams, and report the spread over seeds, as the [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) asks:

```python
import argparse, random
import numpy as np
import torch

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=0)
args = parser.parse_args()

random.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)
torch.use_deterministic_algorithms(True)  # error on nondeterministic ops
```

## G2 · Tests and notebooks

*Beside the level · Warnings only*

**What counts.** Result notebooks are saved after one clean run from top to bottom, and no code quietly changes a result. Tests and continuous integration are asked of software meant for reuse (R3 Automated tests).

**What it flags.**

- Result notebooks not run top to bottom in a fresh kernel, such as cells run out of order.
- Code that silently changes results: a quiet fallback, a disabled save, an unreachable branch.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Restart the kernel and run each notebook top to bottom before saving, and make errors fail loudly.
