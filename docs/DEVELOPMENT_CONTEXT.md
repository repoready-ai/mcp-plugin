# RepoReady MCP plugin development context

Snapshot: 2026-10-26 (plugin 2.0.0 published; 2.0.1 with the to-dos prepared, not published). Verify actual Git history and remote branches before work.

Repository: `repoready-ai/mcp-plugin`. This distributes the remote connection, workflow skill and Claude commands. The server implementation and its contracts live in RepoReady's monorepo (its plan, Track C, covers this plugin; see `docs/plans/README.md`).

This repository is public: keep local machine paths, non-production hosts, internal branch names of other repositories and credentials out of every committed file, these development notes included.

## Contract and packaging

- Production MCP connection is `https://api.repoready.ai/api/mcp`, Streamable HTTP with OAuth. Tests against a non-production server use a separately configured connection (README, "For maintainers"); never change the shipped production URL for a test.
- Keep README, `skills/repoready/SKILL.md`, commands, `.mcp.json`, `plugin.json`, `marketplace.json` and `CHANGELOG.md` consistent with the server version. Since 2.0.0 the plugin describes the 2.x server: one level per check on the ladder L0 Incomplete, L1 Available, L2 Rerunnable, L3 Re-executed, L4 Reproduced (L3 and L4 not offered yet), no score. Adapt consumer wording only when the corresponding contract is live on the production server.
- Preserve "find existing work first", upload exclusions (especially `.env`, `.git`, dependencies and caches), OAuth/account instructions, explicit paid-run approval and data-handling explanations.
- RepoReady also appears in the Helmholtz agent-skills marketplace, which installs from this repository's `main` (plugin and skill source). Its entry is updated by a pull request to that marketplace, separately from this repository.
- Avoid UI claims based on old notes: verify current product paths for each supported client. Claude Science skill import and claude.ai plugin connector installation are different flows.

## Coordination

| Date | Owner | Branch / baseline | Area | State / next step |
| --- | --- | --- | --- | --- |
| 2026-10-02 | Codex local | feat/mcp-v1.1 @ 56fd16f | Shared context, agent guidance, Claude settings | Done; no manifest, endpoint, version or publishing change. |
| 2026-10-10 | Claude local (monorepo Track C, C.2) | claude/plugin-v2 from feat/mcp-v1.1 @ 752a28d | Plugin 2.0.0: skill, commands, README, manifests, CHANGELOG | Committed (bb1075b, b0ccc0b); not pushed. |
| 2026-10-12 | Claude local (C.2) | claude/plugin-v2 @ 26bdfa5 | Brought in line with the 2.0.0 server (no confirm intent, expected cost only, today's words) | Committed; not pushed. |
| 2026-10-13 | Claude local (Track C) | claude/plugin-v2-1013 from claude/plugin-v2 @ 26bdfa5 | Scope labels L1 check / L2 check, Unresolved, contents and roles, the funds stop, cancel | Committed (b893372); not pushed. |
| 2026-10-26 | Claude local (build agent of the monorepo lead session) | claude/plugin-v2-1013 @ b893372 | Release fixes: supplementary results opt-in, conditional rerun, public CHANGELOG, internal details scrubbed | Committed; not pushed. See the hand-off below. |
| 2026-10-26 | Claude local (build agent of the monorepo lead session) | claude/plugin-v2.0.1-todos from main @ bbf26d9 (v2.0.0) | Plugin 2.0.1: the to-do plan through the server's `list_todos` | Committed; not pushed. Publish only after production serves `list_todos`. See the 2.0.1 hand-off below. |

Read the monorepo's MCP server contract (`docs/MCP_SERVER.md`, `apps/api/src/modules/mcp/`) on its production branch when changing tools. If a cloud task only has this repository, request the relevant server contract. Record ownership and contract changes here before overlapping work.

Save plans in docs/plans, durable lessons in docs/memory, and handoffs here. Keep machine credentials and personal integration details outside the shared repository.

## History in brief

- **2026-10-02, context migration.** Shared agent guidance, `docs/`, `.claude/settings.json` and `scripts/configure-agent-context.py` added; the setup script was tested on an isolated checkout (paths, preserved settings, idempotence, refusal to overwrite malformed settings). A pattern scan of migrated notes found no credentials (a limited scan, not a guarantee).
- **2026-10-02, review-UX lane.** A separate Codex branch prepared client documentation for the server's review UX. Kept from it in 2.0.0: supplementary files on upload and no claim of full coverage unless the tool says so (`docs/memory/plugin-v2-decisions.md`, decision 7).
- **2026-10-10 to 2026-10-13, plugin 2.0.0.** The skill, commands and README rewritten for the 2.x server and kept in line with it as the server changed (decisions in `docs/memory/plugin-v2-decisions.md`; user-facing changes in `CHANGELOG.md`). Checks each time: both manifests, `.mcp.json` and `.claude/settings.json` parse; `claude plugin validate` on `.`, `.claude-plugin/plugin.json`, `skills` and `commands` (only the expected root-`CLAUDE.md` warning); every backticked tool or field name exists in the server code; local Markdown links; `git diff --check`; the Done-when grep (`0–100|reproducibility score|free trial|trial runs|must_have|Level [0-9N] of 3` over README, skills, commands) finds nothing.

## Release fixes and hand-off — 2026-10-26

Owner of this change: Claude (build agent of the monorepo lead session), on the owner's "yes please" to making the release check's fixes 1-4. Branch `claude/plugin-v2-1013`, from `b893372`; the change is the commit after it. Nothing pushed, merged, tagged or published; `.mcp.json` unchanged; no paid check, no live MCP call.

Server facts checked read-only against the monorepo's production branch (`apps/api/src/modules/mcp/mcp-v2-tools.service.ts`, `mcp-v2-schemas.ts`, `screen/check-outcome.ts`, `screen/check-incomplete.service.ts`) and its staging branch (same MCP arguments):
- `estimate_run` takes `check_supporting_results` (intents `screen`, `check_again`; off by default: supplementary results are listed as not checked, the supplementary files are still read as materials of the main-text results). Each quote option has `supportingExtraUsd` ("+ about $Y"; 0 when the quote includes them). `start_run` has no such argument: it runs what the quote priced.
- An uncharged incomplete check reruns automatically once (a person's own check or a link's second attempt; not a funds stop, not a rerun); when it could not read some of the authors' code, only once one of those repositories has new code.

What changed:
- `skills/repoready/SKILL.md`: supplementary results not checked by default (words section), the opt-in in step 3 (`supportingExtraUsd`, re-estimate with `check_supporting_results: true`, that quote's "about $X" includes the extra, a changed choice needs a new yes), "may rerun once" with its condition (words section and step 4).
- `commands/analyze.md`: the opt-in in step 3; supplementary findings are Warnings when checked.
- `README.md`: supplementary results only on request, the extra shown with the price, "may rerun once" with its condition, `estimate_run` row.
- `CHANGELOG.md`: a public 2.0.0 entry dated 2026-10-26 (the owner may change the date), without internal branches, commits or the "keep 1.0.1" note, with the current scope names.
- Internal details scrubbed: this file (no local paths, non-production hosts, other repositories' branches or commits), `docs/CLOUD_SETUP.md`, `docs/plans/README.md`, `docs/memory/plugin-v2-decisions.md` (decision 14 added), `docs/memory/MEMORY.md`.

Checks run: see the commit message and the lead session's report (`claude plugin validate` on `.`, `.claude-plugin/plugin.json`, `skills`, `commands`; JSON parses; `git diff --check`; the Done-when grep; a grep for local paths, non-production hosts and internal branch names in shipped files).

What remains for the owner:
1. Smoke test against production with the plugin installed from this folder (`/plugin marketplace add <this folder>`, `/plugin install repoready@repoready`), `/mcp` sign-in, then `get_account`, `list_projects` and `estimate_run` (free); optionally one L1 check after saying yes to its price.
2. Fast-forward `main` to this branch and push `main` (this updates `/plugin marketplace add repoready-ai/mcp-plugin`, `npx skills add` and the Helmholtz installs at once).
3. Tag `v2.0.0` and push the tag.
4. Rebase the Helmholtz fork's 2.0.0 entry branch onto upstream `main`, push it to the fork and open the pull request to the Helmholtz marketplace.
5. The website's MCP docs page still says "v1.0.1"; update it to 2.0.0.
6. Optional, server side: agents see issues but not the to-dos with alternatives or Other findings unless `get_findings` / `get_report` may be used read-only (the skill forbids both).

## Plugin 2.0.1, the to-dos — hand-off 2026-10-26

Owner of this change: Claude (build agent of the monorepo lead session), on the owner's question whether the missing to-dos were fixed. Branch `claude/plugin-v2.0.1-todos`, from the published `main` (`bbf26d9`, v2.0.0). Nothing pushed, merged, tagged or published; `.mcp.json` unchanged; no live MCP call, no paid check.

Server contract (monorepo, decision-log row 261; Track C): a new read-only tool `list_todos` (`projectId`; `status` open / all, default all; `goal` l1 / l2 / beside / level; `format` markdown; `limit` / `cursor`, paged by finding). It answers the web app's To-dos plan: `summary`, `counts` (total, done, toDo), `goals` (label, note, progress), `next`, and `blocks` (one per finding: `title`, `why`, `tag`, `state`, `goalLabel`, `groupLabel`, `issueIds`, `steps` with `n`, `text`, `alternatives`, `line`, `done`, `resolves`, `issueIds`, `findIds`, `who`, `whoText`). Allowed at "Read only". It is on the monorepo's staging line, not yet in production.

What changed: `skills/repoready/SKILL.md` (requirements with the fallback to `list_issues`, step 1, step 5 with "The to-do plan", step 6 works through the steps, "I fixed this" with a step's issue id, `get_findings` / `get_report` still forbidden), `commands/status.md` (the current repository's to-dos in one line, the whole plan on request), `commands/analyze.md` (ends with the to-dos), `README.md` (how a check goes, the tool table, version line), both manifests 2.0.1, `CHANGELOG.md` (2.0.1 entry), `docs/memory/plugin-v2-decisions.md` (decision 15).

Checks: `claude plugin validate` on `.`, `.claude-plugin/plugin.json`, `skills` and `commands`; the manifests, `.mcp.json` and `.claude/settings.json` parse; `git diff --check`; the Done-when grep; every backticked tool and field name exists in the server's `list_todos` output schema.

What remains for the owner:
1. Deploy the server change to production (the monorepo's release flow).
2. Smoke test with this folder installed against production: `/mcp` sign-in, `list_todos` on a project with a check (free, read only), "only what to do".
3. Fast-forward `main` to this branch, push `main`, tag `v2.0.1` and push the tag; then the Helmholtz entry's version line if it names one.
