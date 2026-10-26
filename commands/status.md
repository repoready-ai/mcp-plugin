---
description: Show your RepoReady projects, levels and running checks
---

Show the user's RepoReady status. Read-only: start nothing, approve nothing,
share nothing.

1. `get_account` → who is signed in, who pays by default (organization,
   plan, own OpenRouter key, or nobody yet: then they add their key in the
   web app), the organization's daily cap and today's usage.
2. `list_updates` → what changed since they last looked (finished checks,
   approvals waiting in the browser).
3. `list_runs({status: 'active'})` → checks still running, with phase and
   percent.
4. `list_projects` → the most recently active projects with their latest
   run. If the current directory is a git repository, also call it with
   `repo` = `git remote get-url origin`, put that project first and read its
   level with `get_ladder` (the `headline` per scope) and its to-dos with
   `list_todos({projectId, status: 'open'})` (`counts`, `next`). $ARGUMENTS
   may name a project, repository or paper to look up instead; when it asks
   for the to-dos ("todos", "what to do"), show that project's plan as the
   repoready skill's "The to-do plan" says.

Present a short summary: account and payer; anything waiting for the user
(an approval link, a finished check); running checks (project, phase,
percent, link); then the recent projects (name, latest run and its status,
date, link) and, for the current repository, its level line as the tool
gives it ("L1 · Available · …") and its to-dos in one line ("6 steps to do ·
2 of 8 done; next: …", from `list_todos`). Never show a score or a level as
a fraction. Offer the whole to-do plan (`list_todos`, `format: 'markdown'`;
only what is left: `status: 'open'`) for a project the user wants to work
on; ask before any new (paid) check.
