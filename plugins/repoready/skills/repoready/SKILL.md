---
name: repoready
description: Use when the user wants to check, improve, or certify the reproducibility of a research codebase — "analyze this repo with RepoReady", "how reproducible is this code", "get the RepoReady score up", or before submitting/publishing research code. Drives the RepoReady MCP tools end to end.
---

# RepoReady analysis workflow

RepoReady analyzes a research codebase (optionally with a manuscript) and
returns a 0–100 reproducibility score plus findings with file:line citations.
All analysis runs on RepoReady's servers via the `repoready` MCP tools.

## Authentication

Tools fail with 401/unauthorized until the user has signed in once: tell them
to run `/mcp` and complete the browser sign-in (organization members enter
their institutional email and confirm the magic-link code from their inbox).

## Analyzing the current project (local code)

1. `request_upload_url` → returns `uploadKey` + `uploadUrl`.
2. Zip the project from its root, excluding bulky/irrelevant dirs:
   `zip -r /tmp/code.zip . -x '.git/*' -x 'node_modules/*' -x '.venv/*' -x '__pycache__/*'`
3. Upload: `curl -sf -X PUT -H 'Content-Type: application/zip' --upload-file /tmp/code.zip '<uploadUrl>'`
   (quote the URL — it contains `&`).
4. `analyze_repo` with `{source: {type: 'upload', uploadKey}}`. Pass
   `projectName` (repo/folder name) so repeated analyses accrue to one project.

For a **public GitHub repo**, skip the upload:
`analyze_repo({source: {type: 'github', repoFullName: 'owner/repo', ref: '<branch|tag|sha>'}})`.

## Waiting for results

Runs take several minutes. Poll `get_run_status` about every 30 seconds
(use the returned `estimatedSecondsRemaining` to pace). Do not re-submit
while a run is in progress. Status `failed` → report `errorMessage` to the
user, do not retry in a loop.

## Acting on results

- `get_report` → overall score, category, summary, section overview. Report
  the score and the 2–3 most important problem areas to the user.
- `get_findings` → findings sorted most-severe-first with `citations`
  (`file.py:42`), `suggestions`, `tier` (must_have/should_have/nice_to_have),
  and `confidence`. Default filter returns improvement-and-worse.

**The core loop**: read the findings, open the cited files, fix the issues in
the codebase yourself (start with `critical`/`warning` + `must_have`), then run
a fresh `analyze_repo` and compare scores. Repeat until the user's target is
reached.

- `create_share_link` → public read-only report URL; offer it when the user
  wants to show results (PR description, supervisor, reviewers).

## Notes

- The org may have a daily analysis cap — if a run is rejected for the cap,
  tell the user to try again later; don't retry automatically.
- Each analysis costs real money; don't launch runs the user didn't ask for,
  and prefer one re-analysis after a batch of fixes over one per fix.
