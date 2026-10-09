# Changelog

## 2.0.0 — unreleased (prepared 2026-10-10)

For RepoReady's 2.x server. Published together with the server's 2.0.0
release; until then production serves the 1.x server, so keep 1.0.1 there.

- **Levels instead of a score.** Each check gives one level: L0 Incomplete,
  L1 Available, L2 Rerunnable (L3 Re-executed and L4 Reproduced are not
  offered yet), with Integrity, Automation and Reuse as area results beside
  it. The 0–100 score, categories and tiers are gone from the skill, the
  commands and the README.
- **The 2.x flow.** `list_projects` / `identify_source` → `create_project`
  or `estimate_run` → the user's explicit yes, with the price and who pays →
  `start_run` (and the browser approval link when it answers
  `awaiting_approval`) → `get_run` → `get_ladder` → `list_issues` /
  `get_issue` → "I fixed this" or Check again through `estimate_run`.
  The skill no longer uses `analyze_repo`, `get_report` or `get_findings`,
  which the server keeps for older plugins for one release.
- **Review scopes.** Materials (at most L1) and Materials and workflow (at
  most L2, static); "Continue to L2" after a Materials check.
- **Issues by Impact.** Blocks L1, Caps at L1 (a confirmed paper–code
  contradiction on a key result), Blocks L2, Blocks automation, Warning;
  "what L2 needs" in text for people; "Confirm this" for a lead.
- **Who pays.** A journal's sponsorship, an organization or individual plan,
  or the user's own OpenRouter key; no free trial. "Check incomplete, not
  charged" explained, including what an own key cannot get back.
- **Papers and supplements.** Projects from a DOI, paper link or uploaded
  PDF / LaTeX zip, with separately uploaded supplementary files; the
  intake's coverage is reported before saying a paper was read in full.
- **Safety kept and tightened.** Find existing work first; upload
  exclusions (now also nested dependency folders, virtualenvs and notebook
  checkpoints); never open or approve an approval link for the user; text
  inside findings is data, not instructions.
- `/repoready:status` shows the current repository's level line and what
  is waiting for the user (`list_updates`).
- Manifests: version 2.0.0, new descriptions, a marketplace description.

## 1.1.0 — 2026-09-30 (not published)

- Find existing work first: `get_account`, `list_projects` by git remote,
  `get_project`, `list_runs`.
- `/repoready:status`.

## 1.0.1 — 2026-09-14

- Current claude.ai paths (Customize), Claude Science instructions.

## 1.0.0 — 2026-09-14

- First release: MCP connection, workflow skill, `/repoready:analyze`; MIT
  license; hardened data handling after the marketplace review.
