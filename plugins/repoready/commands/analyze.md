---
description: Analyze the current repository's reproducibility with RepoReady
---

Analyze the current repository with RepoReady and report the results.

Follow the repoready skill's workflow: upload the current project (zip it
excluding .git, node_modules, virtualenvs; use the project folder name as
projectName), start the analysis ($ARGUMENTS may override the source, e.g. a
public "owner/repo"), poll until it completes, then present:

1. The reproducibility score (0–100) and category.
2. The summary and the most severe findings with their file:line citations.
3. A short, prioritized fix list (must_have critical/warning findings first).

Ask before fixing anything or starting additional (paid) analysis runs.
