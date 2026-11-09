# Software reuse: code others can build on

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/software-reuse (English, 2026-11-06). Public text only; it says what is looked at, not how the platform assessment decides.

Reuse asks whether others can install and use your method, tool or package. Checked without a paper, it is the answer: Reusable when R1–R4 are met, else Reuse: n of 4. In a paper project it stands beside the paper’s level and never changes it.

A method that others can install and run on their own data travels further than the paper. The [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html) make a good checklist: documentation, installation, example usage, tests and a license.

## R1 · Installation

*Software reuse · beside the level*

**What counts.** The software installs with one standard command from a package index or the repository, with its dependencies declared.

**What it flags.**

- No packaging file, so the software does not install with one command.
- Usable only as scripts from inside the analysis folder, not as a module.
- The README does not say how to install it.

**How to fix.** Package the method separately from the analysis, with a `pyproject.toml` or an R `DESCRIPTION`:

`pyproject.toml`:

```text
[project]
name = "cellfilter"
version = "1.2.0"
description = "Quality filtering for single-cell count matrices"
requires-python = ">=3.10"
dependencies = ["numpy>=1.26", "anndata>=0.10"]
license = "MIT"

[project.optional-dependencies]
test = ["pytest"]
```

## R2 · Documented interface and examples

*Software reuse · beside the level*

**What counts.** A README or documentation site explains inputs, outputs and options, with a short example that runs on test data.

**What it flags.**

- Public functions without reference documentation, or described only in the paper’s Methods.
- Command-line arguments read without a parser that prints help.
- Parameters fixed in the code rather than options, configuration or function arguments.
- Uninformative errors on bad input.
- The README shows no installation or usage example.

**How to fix.** Document the public functions and ship a small example dataset with a worked example. The check counts how many code files the examples reach.

## R3 · Automated tests

*Software reuse · beside the level*

**What counts.** Tests check the core functionality on small, shipped data, ideally against known results.

**What it flags.**

- No test folder or test files.
- No continuous integration that runs the tests.

**How to fix.** Add tests that run in seconds on shipped data, and run them on every change.

## R4 · Releases and license

*Software reuse · beside the level*

**What counts.** Numbered releases with a changelog, each archived with a DOI, under an open license. The license is checked once, under Journal policy; this area shows that result.

**What it flags.**

- Not on a package index and not archived with a DOI or in Software Heritage.
- No license, or one that restricts reuse (checked once, under Journal policy).
- No changelog or release notes.
- No citation metadata.

**How to fix.** Release with version numbers, note changes per release and archive each one, for example with Zenodo.
