# Workflow: what a rerun needs

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/workflow (English, 2026-11-06). Public text only; it says what is looked at, not how the platform assessment decides.

L2 Rerunnable adds what a rerun needs: versions and identifiers, how inputs were prepared, which script makes which result, instructions that match the repository, and controlled randomness.

A workflow turns available materials into something others can rerun. Documentation or automation can supply each item: a pinned workflow that runs with one command counts. Small omissions stop it: an unnamed version, a renamed script, a path that exists on one laptop. Of over 9,000 R files from Harvard Dataverse, 74% failed to complete without error ([Trisovic et al., 2022](https://doi.org/10.1038/s41597-022-01143-6)). An L2 check assesses this area.

## B1 · Dependencies and versions are listed

*What L2 needs*

**What counts.** A standard file lists every package the code imports, each with a version or range: `requirements.txt`, `environment.yml`, `pyproject.toml`, `renv.lock` or `DESCRIPTION`.

**What it flags.**

- No dependency file at all.
- Imported packages missing from the file, or listed without any version.
- A package the code imports that the file installs only as a dependency of another package: a Warning, since its version is not fixed.

**How to fix.** Generate the list from a clean environment that runs your analysis, give every package a version, and update it in the same commit as the code.

## B2 · The exact code version is identified

*What L2 needs*

**What counts.** The paper cites an immutable version holding the code behind every result, and each fork, model and tool version it names is pinned and matches.

**What it flags.**

- No version cited, only a branch or a concept DOI, or a cited tag that does not exist.
- Result code only on the default branch, not in the cited version.
- A fork, another repository or a model used without a fixed tag, commit or revision.
- A tool version the paper states that the pins, lock file or logs contradict.

**How to fix.** Tag and archive the version you submit and cite its version DOI. Pin forks and models to a commit or revision, and copy versions from the lock file:

```bash
git tag -a v1.0-paper -m "Code as submitted with the manuscript"
git push origin v1.0-paper
```

## B3 · Data sources have stable identifiers

*What L2 needs*

**What counts.** Each dataset has an accession, DOI, versioned record or release URL; live services carry a release or query date; controlled data say where and how to apply.

**What it flags.**

- A dataset named only in prose, without accession, DOI or versioned record.
- Data identified only as a table in an article’s supplement.
- A changeable link: a cloud drive, a personal or mutable URL, a model without a revision.
- Controlled data with no access procedure.
- A placeholder where the identifier belongs.
- A link that resolves to another file.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** List each dataset with source, identifier, version and access in the README, pin models to a revision, and replace personal links. The [Materials guide](https://repoready.ai/docs/checks/materials#inputs) table works.

## B4 · Data preparation steps are documented

*What L2 needs*

**What counts.** Every input that shared code does not produce, deposited processed data included, comes with its steps: tool, version, non-default parameters and any manual curation.

**What it flags.**

- An input no shared code produces, such as a hand-edited table or a model without its training code.
- Steps described only in prose, without tool, version or parameters.
- A file only commented-out code writes.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Make each step a script or workflow rule, re-enable or remove commented-out steps, and describe any manual step exactly:

`Snakefile`:

```text
rule filter_cells:
    input:  "data/raw/counts.h5ad"
    output: "data/processed/filtered.h5ad"
    params: min_genes=200
    shell:  "python -m pipeline.filter {input} {output} --min-genes {params.min_genes}"

rule train_model:
    input:  "data/processed/filtered.h5ad"
    output: "models/classifier.pt"
    shell:  "python -m pipeline.train {input} {output} --seed 0"
```

## B5 · Code is linked to the paper’s results

*What L2 needs*

**What counts.** A table or entry links each key figure, panel, table and reported number to the one script, notebook section or command that produces it.

**What it flags.**

- No map from results to code.
- A map that skips some figures, panels or tables.
- Variant copies of the code for one result, such as `analysis_v2.py` beside `analysis_final.py`.

**How to fix.** Add a results table to the README, one row per paper item, keep one copy of each script, and say what any other script is for:

`README.md`:

```markdown
## Results

| Paper item | Command                            | Output                           |
|------------|------------------------------------|----------------------------------|
| Figure 2   | Rscript analysis/figure2.R         | results/figure2/figure2.csv      |
| Figure 3B  | python -m analysis.fig3 --panel b  | results/figure3/panel_b.csv      |
| Table 2    | python -m analysis.evaluate_cohort | results/claims/table2_auroc.json |
```

## B6 · Instructions explain how to run the analysis

*What L2 needs*

**What counts.** The README, paper or linked docs cover setup, where inputs go or how they are fetched, the run order and every manual step, or that there is none.

**What it flags.**

- Setup, input placement, run order or manual steps missing, or no README at all.
- Data read from a folder outside the repository that no doc names, or a promised download that never happens.

**How to fix.** Write a short “How to reproduce” section: setup, where each input goes, then each step with its command and the outputs it creates, in order.

## B7 · Documented commands agree with the code

*What L2 needs*

**What counts.** Every command, file, option, variable, folder and install name the docs give matches the repository exactly, and result notebooks are saved without errors.

**What it flags.**

- A command, file, option, variable or folder that does not match the repository, such as `data.csv` for `Data.csv.gz`.
- An install name that belongs to another package.
- A result notebook saved with an error.
- Leftover placeholder text like `<your-path>` in an instruction.
- Result code that stops and waits for a person, such as `breakpoint()`, `input()` or `View()`.
- A documented run whose configuration turns off saving the outputs the README promises, such as `save_img: False` (a Warning).
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** In a fresh clone, check every name the README uses, create the folders it writes to, replace placeholders and save notebooks without errors.

## B8 · Machine assumptions documented

*What L2 needs*

**What counts.** Result code builds paths from the project folder or a setting and has no unexplained check for one host, system or personal environment.

**What it flags.**

- Author-machine paths like `/Users/you/data`.
- A script tied to one host, system or your own shell profile.

**How to fix.** Build paths from the project root, let data locations be overridden, and explain any check that refuses other systems:

```python
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]   # repository root, from src/pipeline.py
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))
counts = DATA / "raw" / "counts.h5ad"
```

## B10 · Randomness of key results is controlled

*What L2 needs*

**What counts.** Each key result that depends on random draws has its random steps seeded, library defaults included, or the paper reports how it varies across runs.

**What it flags.**

- A stochastic key result with unseeded random steps and no reported spread. Seeding every other call is an Automation item.

**How to fix.** Set a seed for each key result’s random steps, for example `random_state=0` in each library call, or report the spread over several runs.

## G1 · A tidy repository

*Beside the level · Warnings only*

**What counts.** The repository holds only what the analysis needs, and no credentials.

**What it flags.**

- System or editor junk, scratch copies, duplicates, large binaries or files your `.gitignore` excludes.
- Functions nothing calls and files the analysis never reads.
- A committed API key, which only you see.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Add a `.gitignore`, remove what no result needs, and revoke any committed key and purge it from the history.

## G4 · Hardware, tools and versions

*Beside the level · Warnings only*

**What counts.** The README states GPU, memory and run time and names any commercial software with its version, and the cited code is the code you maintain.

**What it flags.**

- GPU, memory or run-time needs not stated.
- A step that needs commercial software.
- Code last changed long before the paper was accepted, so analyses added in revision may be missing.
- The cited version and the current code differ.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Note hardware needs and run time in the README, name commercial steps, and cite a new release when the code changes.
