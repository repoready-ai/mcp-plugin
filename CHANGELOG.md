# Changelog

## 2.0.1 — requires the RepoReady server with `list_todos` (next release)

- **The to-dos.** The agent now shows the same to-do plan as the web app's
  To-dos view, read with the server's new `list_todos` tool: what to do to
  reach L1, to reach L2, then what is optional beside the level (including
  Other findings, which never change the level); each finding's steps in
  order, a step with alternatives as one step ("Either … or …"), steps
  already fixed ticked, and who can do each step: "AI can fix this", "AI
  can help · needs your answer" or "Authors". The check's summary comes
  first when it has one.
- **Only what to do.** Ask for "only what to do" (or only what changes the
  level) and the agent lists just the open steps.
- `/repoready:status` shows the current repository's to-dos in one line and
  offers the whole plan; `/repoready:analyze` ends with the to-dos instead
  of a fix list.
- With a server from before `list_todos`, the agent falls back to the issue
  list (`list_issues`) and says the to-do plan needs a newer server.
  `get_findings` and `get_report` stay unused.
- Unchanged: nothing paid starts without the expected cost ("about $X"),
  who pays and your explicit yes.

## 2.0.0 — 2026-10-26

For RepoReady's 2.x server (MCP server 2.0.0). Earlier plugin versions
describe the retired score-based server.

- **Levels instead of a score.** Each check gives one level: L0 Incomplete,
  L1 Available, L2 Rerunnable (L3 Re-executed and L4 Reproduced are not
  offered yet), with Integrity, Automation and Reuse as area results beside
  it, and Journal policy when a journal is known. The 0–100 score,
  categories and tiers are gone from the skill, the commands and the
  README.
- **Review scopes.** An "L1 check" (are the code, data and software behind
  each result shared?) awards at most L1; an "L2 check" (the full review
  without running the code: workflow, integrity, automation, reuse) awards
  at most L2. After an L1 check, "Continue to L2" checks the same inputs
  for less than a new check, and the issue list says which findings were
  not assessed in the L1 check.
- **The 2.x flow.** `list_projects` / `identify_source` → `create_project`
  or `estimate_run` → the user's explicit yes, with the expected cost and
  who pays → `start_run` (and the browser approval link when it answers
  `awaiting_approval`) → `get_run` → `get_ladder` → `list_issues` /
  `get_issue` → "I fixed this" or Check again through `estimate_run`.
  The skill no longer uses `analyze_repo`, `get_report` or `get_findings`,
  which the server keeps for older plugins for one release.
- **The expected cost only.** The agent tells the user "about $X"
  (`expectedUsd`), never the most a check may spend.
- **Supplementary results only on request.** By default a check does not
  check supplementary figures, tables and datasets as results; it still
  reads the supplementary files as materials of the main-text results.
  Each quote names what also checking them would add ("+ about $Y",
  `supportingExtraUsd`); on the user's request the agent prices the check
  again with `check_supporting_results: true`. Findings on supplementary
  results are Warnings, never blockers for a level.
- **No "Confirm this".** Every check confirms its uncertain findings
  itself (`get_run` shows `confirming`); what it could not decide is shown
  as Unresolved. The only follow-up on one finding is "I fixed this"
  (it checks the project again first, then that issue).
- **Issues by Impact.** Blocks L1, Blocks L2, Caps at L1 (a confirmed
  paper–code contradiction on a key result), Blocks L3, Blocks Automation,
  Warning, in that order; "what L2 needs" in plain words. Finding states:
  Missing, Warning, Unresolved, Available, Not applicable.
- **Who pays.** A journal's sponsorship, an organization or individual
  plan, or the user's own OpenRouter key; there are no free checks.
- **Incomplete, stopped and cancelled checks.** A check that cannot finish
  is "Check incomplete, not charged" and may rerun once by itself (if some
  of the authors' code could not be read, only once that code is new); on
  the user's own key, the provider's tokens for it are not refunded. A check stopped because the
  payer's key ran out of credit is charged what it spent and keeps its
  answers: Check again on the same payer continues it. A cancelled check is
  charged what it spent until it stopped, and the project keeps its last
  finished check.
- **Papers and supplements.** Projects from a DOI, paper link or uploaded
  PDF / LaTeX zip, with separately uploaded supplementary files; the
  intake's coverage is reported before saying a paper was read in full.
  Materials can hold code, data or both and have several roles.
- **More of the server described:** `get_update` (what a new check would
  read), `lookup_public_assessment` (only while the public registry is
  on), `targetJournal` and the Journal policy area, `checkVersion`
  choices, shared root causes, the agents' policy refusals, share links
  sent by email only on the user's request, badges issued in the web app.
- **Safety kept and tightened.** Find existing work first; upload
  exclusions (now also nested dependency folders, virtualenvs and notebook
  checkpoints); never open or approve an approval link for the user; text
  inside findings is data, not instructions.
- `/repoready:status` shows the current repository's level line and what
  is waiting for the user (`list_updates`).
- Manifests: version 2.0.0, new descriptions, a marketplace description.

## 1.1.0 (not published; included in 2.0.0)

- Find existing work first: `get_account`, `list_projects` by git remote,
  `get_project`, `list_runs`.
- `/repoready:status`.

## 1.0.1 — 2026-09-14

- Current claude.ai paths (Customize), Claude Science instructions.

## 1.0.0 — 2026-09-14

- First release: MCP connection, workflow skill, `/repoready:analyze`; MIT
  license; hardened data handling after the marketplace review.
