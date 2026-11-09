# Access & preservation: lasting, citable materials

Self-check v0.1 · copied from the public guide https://repoready.ai/docs/checks/access-and-preservation (English, 2026-11-07). Public text only; it says what is looked at, not how the platform assessment decides.

Access describes how others can obtain your materials; preservation keeps them available after the paper. Both sit beside the level, with license, citation and journal policy.

A repository can be renamed, rewritten or deleted after publication. Journals ask for durable copies: [PLOS Computational Biology](https://journals.plos.org/ploscompbiol/s/code-availability) recommends depositing code in a repository that issues DOIs. RepoReady reports the access conditions it finds; it does not verify archives yet.

## P1 · Access conditions

*Beside the level*

**What counts.** Each item says how it can be obtained: openly, after registration, through a committee, by purchase, for reviewers until publication, or after an embargo with its date.

**Common gaps.** A bare “available on request” is a Materials gap. Restricted data with a stated reason count from the first shared processed file onward.

**How to fix.** State the route per item. For restricted data, give the reason in the paper’s data availability statement and share processed or synthetic data downstream, so others can rerun from there.

## P2 · A lasting archive

*Beside the level*

**What counts.** Code and data sit in an archive that issues persistent identifiers, such as Zenodo, figshare, Software Heritage or a domain repository.

**Common gaps.** A GitHub repository alone, or a DOI that points to the newest version instead of the one in the paper.

**How to fix.** Connect the repository to Zenodo, so each GitHub release gets its own version DOI, and cite that version DOI.

## J · Journal policy

*Beside the level · Warnings only*

**What counts.** What journals ask for beyond the level: a software license, a citation file that names the paper, source data for every figure and a code availability statement.

**What it flags.**

- No license for the code.
- Only a content license such as CC-BY on code.
- A dependency whose license restricts use.
- No citation metadata, such as a `CITATION.cff`.
- Figure source data empty, incomplete or duplicated.
- A material the level relies on that the paper does not cite.
- Some findings here are Warnings: they point to an improvement and never change the level.

**How to fix.** Deposit one source data file per figure, use our [statement template](https://repoready.ai/code-availability-statement), and add a license ([without one, nobody may reuse the code](https://choosealicense.com/no-permission/)) and a [citation file](https://citation-file-format.github.io/):

`CITATION.cff`:

```text
cff-version: 1.2.0
message: "If you use this code, please cite the paper below."
title: "Code for: <paper title>"
version: "v1.0-paper"
doi: "<version DOI from Zenodo>"
license: MIT
authors:
  - family-names: "<Family>"
    given-names: "<Given>"
preferred-citation:
  type: article
  title: "<paper title>"
  authors:
    - family-names: "<Family>"
      given-names: "<Given>"
  doi: "<paper DOI>"
```
