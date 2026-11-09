# Materials: code, inputs and software

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/materials (English, 2026-11-06). Public text only; it says what is looked at, not how the platform assessment decides.

L1 Available needs three things for every key result: the code that computes it, the inputs it reads and the software it needs, each obtainable by a third party.

Without the code, data and software behind a result, no documentation lets anyone check it, so Materials decide L1. The [FAIR principles](https://doi.org/10.1038/sdata.2016.18) ask that data can be retrieved through a persistent identifier.

## A1 · Code for each result is available

*What L1 needs*

**What counts.** Public code, in a repository or archive, computes the values in every key figure, table and dataset. Statistics inside plotting scripts count; cosmetic plotting alone does not.

**What it flags.**

- No public code computes the values of a key result.
- The code computes only some of the values, or a different quantity.
- Values from an interactive analysis, or from a named tool without the settings needed to redo them.
- A panel of experimental data whose statistical test is not shared, or is named without its settings.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Share every script that computes a reported value, analyses added during revision included, and name it in the README.

## A2 · Input data can be obtained

*What L1 needs*

**What counts.** Every file the code reads is shared, produced by the code or deposited with an identifier. Registration, controlled access, purchase, reviewer-only links and dated embargoes count.

**What it flags.**

- A file the code reads that is shared nowhere, or only “on request”.
- A data deposit that lacks a file the code reads.
- The only link is dead, after retries and a web-archive lookup. A link whose server refuses access is a Warning when a known mirror serves the same file: replace the link.
- The experimental data a panel shows are not shared.

**How to fix.** Deposit data you produced in an archive that issues DOIs. For controlled data, name the committee, how to apply and where the files go:

`README.md`:

```markdown
## Data

| Dataset        | Source  | Identifier             | Version | Access                |
|----------------|---------|------------------------|---------|-----------------------|
| Raw counts     | Zenodo  | 10.5281/zenodo.0000000 | v2      | open                  |
| Patient cohort | EGA     | EGAD00000000000        | 2024-03 | data access committee |
| Reference      | Ensembl | GRCh38                 | 110     | open                  |
```

## A3 · Required software can be obtained

*What L1 needs*

**What counts.** Besides your own code, every package, tool, model and service it depends on, such as `scanpy` or a pretrained model, can be obtained from a package index, model hub, public repository or archive. Commercial software counts.

**What it flags.**

- A package, tool, model or weights nobody can obtain: never released, or deleted without an archive.
- A dependency found only in the project’s own materials, not published.

**How to fix.** Release in-house tools and weights, or archive the versions you used. Name commercial software with version, vendor and the steps that need it.
