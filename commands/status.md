---
description: Show your RepoReady projects and running analyses
---

Show the user's RepoReady status. Read-only: start nothing, share nothing.

1. `repoready:get_account` → who is signed in, who pays for analyses (and
   free-trial runs left), the organization's daily cap and today's usage.
2. `repoready:list_runs({status: 'active'})` → analyses still in progress,
   with their phase and percent.
3. `repoready:list_projects` → the most recently active projects with their
   latest run. If the current directory is a git repository, also call it
   with `repo` = `git remote get-url origin` and put that project first.
   $ARGUMENTS may name a project or repository to look up instead.

Present a short summary: account and payer, running analyses (project,
phase, percent, link), then the recent projects (name, latest run status and
score, date, link). Offer `get_findings` for a project the user wants to work
on; ask before starting any new (paid) analysis.
