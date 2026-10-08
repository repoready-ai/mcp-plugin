# RepoReady MCP plugin development context

Snapshot: 2026-10-02. Verify actual Git history and remote branches before work.

Repository: `repoready-ai/mcp-plugin`. This distributes the remote connection, workflow skill and Claude commands. The server implementation and 2.0 contracts live in `repoready-ai/repoready-monorepo` on staging.

At migration, local main and cached origin/main = `ed84863` (v1.0.1). Local `feat/mcp-v1.1` = `56fd16f` (v1.1.0), adding existing-project lookup by git remote and `/repoready:status`. Its remote publication was not verified. This context change is prepared on that existing v1.1 worktree, preserving its work. Select an explicitly pushed branch in cloud; do not assume local v1.1 is available there.

## Contract and packaging

- Production MCP connection is `https://api.repoready.ai/api/mcp`, Streamable HTTP with OAuth. Staging uses a separately configured connection; never change the shipped production URL just to run a local test.
- Keep README, skills/repoready/SKILL.md, commands, .mcp.json, plugin.json and marketplace.json consistent with the selected server version. The current README still describes 0–100 scores; the monorepo's 2.0 target is levels 0–3, with 3 best. Adapt consumer wording only when the corresponding contract is available on the target server.
- Preserve “find existing work first” behavior, upload exclusions (especially .env, .git, dependencies and caches), OAuth/account instructions, explicit paid-run approval and data-handling explanations.
- RepoReady also appears in the Helmholtz marketplace. Its source/manifest updates are separate from this repository. Historical local notes describe the fork review, not current PR state; verify before changing or publishing there.
- Avoid UI claims based on old notes: verify current product paths for each supported client. Claude Science skill import and claude.ai plugin connector installation are different flows.

## Coordination

| Date | Owner | Branch / baseline | Area | State / next step |
| --- | --- | --- | --- | --- |
| 2026-10-02 | Codex local | feat/mcp-v1.1 @ 56fd16f | Shared context, agent guidance, Claude settings | Local documentation/setup change; no manifest, runtime endpoint, version, server, publishing or paid analysis changed. |

Read the monorepo's DEVELOPMENT_CONTEXT.md and docs/MCP_SERVER.md at the matching pushed branch when changing tools. If the cloud task only has this repo, request the relevant server contract or inspect it using authorized repository access. Record ownership and contract changes here before overlapping Claude's work.

Save plans in docs/plans, durable lessons in docs/memory, and handoffs here. Keep machine credentials and personal integration details outside the shared repository.

## Context migration verification (2026-10-02)

Shared Markdown links and JSON settings validated. The setup script was exercised on an isolated temporary checkout for correct paths, preservation of unrelated settings, repeated-run idempotence and refusal to overwrite malformed settings. A scan of migrated plans/memory found no matches for common private-key, API-token or credential-URL patterns; this is a limited pattern scan, not a guarantee. No application code was changed, so the full runtime suites were not run. Claude was not restarted or asked to run a live model task during verification.

155 existing local worktrees across the two repositories were configured to use their repository's canonical migrated memory and their own docs/plans. Existing unrelated local settings were preserved; backups of pre-existing settings are kept locally under /private/tmp/repoready-agent-settings-20261002T100407Z. A local workspace-level CLAUDE.md supplies routing for older branches without the new shared files. The remote/cloud environment itself was not modified; commits and owner-authorized pushes are still required for cloud visibility.

## Review UX contract work — 2026-10-02

Codex owns `codex/review-ux-plugin-2026-10-02` (base `56fd16f`) in sibling `repoready-mcp-plugin-review-ux` for the client documentation accompanying monorepo `codex/review-ux-2026-10-02`. Scope: capability-gated 2.0 workflow, supplements, requirements, author/reviewer intent and the total check ceiling. Production v1 instructions, endpoint and manifests are preserved. No publication or paid analysis is authorised.

Review UX documentation is prepared in the task branch above: `docs/review-ux-v2-contract.md`, linked from the skill and README. Plugin JSON/local links and whitespace checks passed. Server/runtime verification is in the monorepo review-UX handoff. Nothing was published; the production endpoint and manifests are unchanged.
