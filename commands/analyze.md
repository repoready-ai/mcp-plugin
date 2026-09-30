---
description: Analyze the current repository's reproducibility with RepoReady
---

Analyze the current repository with RepoReady and report the results.

Follow the repoready skill's workflow:

1. Look for existing work first: `list_projects` with `repo` = the git
   remote. If a run is still in progress, wait for it instead of starting
   another; if the latest completed run is recent and the code has not
   changed since, offer its results before re-analyzing.
2. Before starting a new analysis, tell the user who pays (`get_account`)
   and get their OK.
3. Upload the current project (zip it excluding .git, node_modules,
   virtualenvs, .env files; pass `repo` = the git remote, or the project
   folder name as projectName when there is no remote) and start the
   analysis ($ARGUMENTS may override the source, e.g. "owner/repo" or a
   GitHub URL). Poll until it completes, then present:

   1. The reproducibility score (0–100) and category.
   2. The summary and the most severe findings with their file:line citations.
   3. A short, prioritized fix list (must_have critical/warning findings first).

Ask before fixing anything or starting additional (paid) analysis runs.
