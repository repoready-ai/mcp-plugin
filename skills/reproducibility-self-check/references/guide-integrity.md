# Integrity: paper and code agree

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/integrity (English, 2026-11-06). Public text only; it says what is looked at, not how the platform assessment decides.

RepoReady compares what the paper states with what the code and its saved outputs do. A confirmed contradiction that changes a reported key result caps the level at L1: a rerun would reproduce the code, not the paper.

Paper and code are revised separately, and details drift: a reviewer asks for a one-sided test, the text changes, the script does not. An L2 check compares them for every key result.

## B9 · Outputs correspond to the reported results

*Caps at L1*

**What counts.** The code behind each key result does what the paper states: method, parameters, statistics, data processing and splits, and every reported number and quantity.

**What it flags.**

- Method: the paper says Louvain, the code runs Leiden.
- Parameter: 200 genes stated, 300 in the code.
- Statistics: a different test, sidedness, correction, interval or n.
- Data processing: exclusions, replaced values, transformations or alignment the Methods do not state.
- Splits: a different train/test split or sample selection, or a test set that overlaps training.
- Reported values: a number the code, its saved outputs or the deposit do not give.
- Quantities: a metric computed differently from how the paper defines it.
- A comparison the check could not complete, named so you can verify it.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Revise text and code together, describe every processing step and split in the Methods, and save each reported value with its script and a test:

`tests/test_paper_values.py`:

```python
import json

def test_table2_auroc_matches_paper():
    with open("results/claims/table2_auroc.json") as fh:
        result = json.load(fh)
    assert 0.90 <= result["mean"] <= 0.92  # the paper reports 0.91
```

## G3 · Paper, data and docs agree

*Beside the level · Warnings only*

**What counts.** The paper states each value consistently, each sample, dataset and version has one name, references point to the right target, and docs match code and paper.

**What it flags.**

- The paper contradicts itself, such as a legend and the Methods with different thresholds.
- One item with two names, such as a strain, sample or dataset.
- A reference or identifier pointing to the wrong target or none, such as a malformed ontology ID.
- Documentation that contradicts the code or the paper, such as a README describing an older pipeline.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Correct the passage each one cites, and use one name per item across paper, deposits and code.
