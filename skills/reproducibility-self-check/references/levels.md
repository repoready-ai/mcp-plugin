# Reproducibility levels

Self-check v0.1 · copied from the public pages https://repoready.ai/docs/levels and the homepage ladder (English, 2026-11-06), shortened where a self-check does not apply (it never retries dead links or runs code). Public text only.

Each level says what the evidence supports, and each builds on the one before it. Levels apply to papers: every finished check of a paper returns one level. Software checked on its own, without a paper, gets no level: its answer is the [Software reuse](https://repoready.ai/docs/checks/software-reuse) result, "Reusable" or "Reuse: n of 4"; analysis code without its paper waits for the paper.

## The five levels

| Level | Name | Short | What it means |
|---|---|---|---|
| L0 | Incomplete | An essential material is confirmed missing. | A key result lacks code, an input or software that a third party can obtain. The report names the item, the result it blocks and the materials read. |
| L1 | Available | Code, inputs and software for every key result. | The code that computes each key result, its inputs and its software can be obtained, some after registration, application or purchase. Conditions are shown beside the level. |
| L2 | Rerunnable | L1 plus what a rerun needs. | L1 plus the exact code version, the environment with versions, data identifiers, the steps with their parameters, the run order, instructions that agree with the code, no machine-only paths, and seeded or reported randomness for key results. Documentation or automation can supply each item. |
| L3 | Re-executed | L2 plus a run in an independent sandbox. | Coming soon. The key results' workflow ran in an independent sandbox without the authors' help. |
| L4 | Reproduced | L3 plus matching key values. | Coming soon. The key reported values match within a stated tolerance. |

L3 and L4 need evidence from running the code. A self-check never awards them.

## How a level is awarded

Each area counts its own requirements: met, missing, not applicable, not assessed in this check. A level is awarded when its own requirements and every lower level are met. Strengths never offset a gap, and there is no combined score.

Supplementary results, such as supplementary figures and tables, never block a level. The supplementary files are read for the key results, but the supplementary results themselves are not checked. Only key results decide the level.

What L2 needs can be complete while L1 is not. The workflow result stays visible; the level rises once the missing input is shared.

## What a finding blocks

| Label | Meaning |
|---|---|
| Blocks L1 | A key result lacks its code, an input or the software it needs. |
| Blocks L2 | A rerun of a key result lacks something it needs: a version, an identifier, a step, the run order or controlled randomness. |
| Caps at L1 | The paper and the code behind a key result contradict each other in a way that changes a reported result. The level stays at L1: a rerun would reproduce the code, not the paper. |
| Blocks Automation | Running every step takes more than one locked, seeded command. Automation is an area result, so this never lowers the level. |
| Warning | Worth fixing, but blocks no level: a placeholder link in the docs, commented-out steps, scripts or files nothing uses, an external service, an archived copy of a dead link, anything a supplementary result lacks. Journal policy and good practice findings are always Warnings. |

## Access and restricted data

Available means a third party can obtain the material under stated conditions, not that it is public. Conditions are shown beside the level and never change it.

- Registration, a data access committee, purchase and commercial software count as available, with a note.
- Reviewer-only data ("released at publication") and an embargo with a date count as available, with a note.
- A bare "available on request" is a gap: such requests mostly go unanswered.
- Restricted data with a stated reason: the level is decided from the first shared point. With processed data shared and the steps before them specified, it reads "raw data restricted · reproducible from processed data". With nothing shareable, L0 reads "restricted data (declared)", and code and workflow are still shown.

## Levels and areas

| Area | Relation to the level | Question |
|---|---|---|
| Materials | What L1 needs | Can a third party obtain the code, inputs and software of every key result? Registration, controlled access and purchase count, with a note; a bare "available on request" does not. |
| Workflow | What L2 needs | Could someone rerun each key result: versions, identifiers, steps, run order, instructions that agree with the code, and controlled randomness? Documentation or automation can supply each item. |
| Integrity | Caps at L1 | Do the paper's methods, parameters, statistics and numbers agree with the code? A confirmed contradiction that changes a reported key result caps the level at L1. |
| Automation | Area result, one route to L2 | One command, a pinned environment, automated inputs and seeds throughout. It can supply what L2 needs, but it is not a level. |
| Access & preservation | Beside the level | How each material can be obtained and whether it is archived. Access notes never change the level. |
| Software reuse | Area result, beside the level | Can others install and use a method, tool or package beyond this paper? It never raises a paper's level. |

## What a check covers

A check reads the code, paper, supplements, data and documentation; the code is not executed. A CSV can hold the scientific result: missing cosmetic plotting code alone is not a gap, but statistics inside a plotting script are part of the analysis.
