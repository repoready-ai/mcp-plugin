# Changelog

## 2.0.0 — unreleased (prepared 2026-10-10, brought in line with the release server 2026-10-12)

For RepoReady's 2.x server. Published together with the server's 2.0.0
release; until then production serves the 1.x server, so keep 1.0.1 there.

Brought in line on 2026-10-13 with the server on monorepo
`claude/integration-1013` (`8583813a`, 28 tools with the registry lookup,
27 without):

- **Issue lists say "Unresolved"** for an issue the check could not decide
  (the server's markdown no longer says "not decided in this check").
- **Materials hold code, data or both and can have several roles**
  (`contents`, `roles` in `create_project`'s and `update_components`'
  rows); the skill names them where the user reviews what was found.
- **Check incomplete when the payer's key runs dry**: charged what it
  spent, no automatic rerun, its answers kept; Check again on the same
  payer continues it without paying for them again. The plain "Check
  incomplete, not charged" stays for the check's own doubt.
- **Scope labels** (owner 2026-10-13): "L1 check" and "L2 check" for the
  user, in place of "Materials" and "Materials and workflow"; the `scope`
  ids `materials` / `workflow` are unchanged; "Materials" stays the area
  name.
- **Cancel**: a cancelled check is charged what it spent until it stopped,
  and the project keeps its last finished check.
- **After a Materials check**, `list_issues` may leave out the Workflow and
  Automation findings (`outsideScope`, `scopeNote`, being added on the
  server's `claude/b6-b7`): the skill says they are not assessed in that
  scope and offers "Continue to L2".

Brought in line on 2026-10-12 with the server of the R1 release
(monorepo `staging` `d1e02bcd`, `docs/MCP_SERVER.md` 2.0.0):

- **No "Confirm this".** The `confirm` intent and `confirmFirst` are gone
  from the skill: every check confirms its uncertain findings itself
  (`get_run` shows `confirming`), the server refuses `confirm` with
  `intent_retired`, and the only follow-up on one finding is "I fixed this"
  (it checks the project again first, then that issue).
- **The expected cost only.** The agent tells the user "about $X"
  (`expectedUsd`, as the server's `next` / `note` texts word it), never the
  ceiling; `ceilingUsd`, `chargeUsd` and `holdUsd` stay machine fields.
- **Today's words.** Impact as the server returns it (Blocks L1, Blocks L2,
  Caps at L1, Blocks L3, Blocks Automation, Warning) and in that order;
  findings on supplementary results are Warnings, never blockers; finding
  states Missing, Warning, Unresolved, Available, Not applicable (an issue
  with `notDecided` is Unresolved); levels are no preview.
- **New server fields and tools described:** `get_update` (what a new check
  would read), `lookup_public_assessment` only while the public registry is
  on, `targetJournal` and the Journal policy area, `checkVersion` choices,
  `rootCauses`, the agents' policy refusals, badges issued in the web app
  only, `payer.free` (a journal's sponsorship), share links sent by email
  only on the user's request.

- **Levels instead of a score.** Each check gives one level: L0 Incomplete,
  L1 Available, L2 Rerunnable (L3 Re-executed and L4 Reproduced are not
  offered yet), with Integrity, Automation and Reuse as area results beside
  it. The 0–100 score, categories and tiers are gone from the skill, the
  commands and the README.
- **The 2.x flow.** `list_projects` / `identify_source` → `create_project`
  or `estimate_run` → the user's explicit yes, with the expected cost and who pays →
  `start_run` (and the browser approval link when it answers
  `awaiting_approval`) → `get_run` → `get_ladder` → `list_issues` /
  `get_issue` → "I fixed this" or Check again through `estimate_run`.
  The skill no longer uses `analyze_repo`, `get_report` or `get_findings`,
  which the server keeps for older plugins for one release.
- **Review scopes.** Materials (at most L1) and Materials and workflow (at
  most L2, static); "Continue to L2" after a Materials check.
- **Issues by Impact.** Blocks L1, Blocks L2, Caps at L1 (a confirmed
  paper–code contradiction on a key result), Blocks L3, Blocks Automation,
  Warning; "what L2 needs" in text for people.
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
