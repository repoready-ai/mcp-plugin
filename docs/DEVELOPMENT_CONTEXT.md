# RepoReady MCP plugin development context

Snapshot: 2026-10-02, updated 2026-10-10 (plugin 2.0.0 hand-off below). Verify actual Git history and remote branches before work.

Repository: `repoready-ai/mcp-plugin`. This distributes the remote connection, workflow skill and Claude commands. The server implementation and 2.0 contracts live in `repoready-ai/repoready-monorepo` on staging.

At migration, local main and cached origin/main = `ed84863` (v1.0.1). Local `feat/mcp-v1.1` = `56fd16f` (v1.1.0), adding existing-project lookup by git remote and `/repoready:status`. Its remote publication was not verified. This context change is prepared on that existing v1.1 worktree, preserving its work. Select an explicitly pushed branch in cloud; do not assume local v1.1 is available there.

## Contract and packaging

- Production MCP connection is `https://api.repoready.ai/api/mcp`, Streamable HTTP with OAuth. Staging uses a separately configured connection; never change the shipped production URL just to run a local test.
- Keep README, skills/repoready/SKILL.md, commands, .mcp.json, plugin.json and marketplace.json consistent with the selected server version. Since 2.0.0 (branch `claude/plugin-v2`) the plugin describes the 2.x server: one level per check on the ladder L0 Incomplete, L1 Available, L2 Rerunnable, L3 Re-executed, L4 Reproduced (L3 and L4 not offered yet), no score. Production serves 1.x until R1, so `main` keeps 1.0.1 until then. Adapt consumer wording only when the corresponding contract is available on the target server.
- Preserve “find existing work first” behavior, upload exclusions (especially .env, .git, dependencies and caches), OAuth/account instructions, explicit paid-run approval and data-handling explanations.
- RepoReady also appears in the Helmholtz marketplace. Its source/manifest updates are separate from this repository. Historical local notes describe the fork review, not current PR state; verify before changing or publishing there.
- Avoid UI claims based on old notes: verify current product paths for each supported client. Claude Science skill import and claude.ai plugin connector installation are different flows.

## Coordination

| Date | Owner | Branch / baseline | Area | State / next step |
| --- | --- | --- | --- | --- |
| 2026-10-02 | Codex local | feat/mcp-v1.1 @ 56fd16f | Shared context, agent guidance, Claude settings | Local documentation/setup change; no manifest, runtime endpoint, version, server, publishing or paid analysis changed. |
| 2026-10-10 | Claude local (monorepo Track C, C.2) | claude/plugin-v2 from feat/mcp-v1.1 @ 752a28d, worktree `../repoready-mcp-plugin-v2` | Plugin 2.0.0: skill, commands, README, manifests, CHANGELOG | Built and committed locally; not pushed, not published. Next: owner's pushes at R1 (see the hand-off below). |
| 2026-10-12 | Claude local (build agent of the lead session, C.2) | claude/plugin-v2 @ b0ccc0b | Skill, analyze command, README, CHANGELOG brought in line with the R1 server (no confirm intent, expected cost only, today's words) | Committed locally; not pushed, not published. See "Plugin 2.0.0 brought in line with the R1 server" below. |
| 2026-10-13 | Claude local (Track C agent of the monorepo lead session) | claude/plugin-v2-1013 from claude/plugin-v2 @ 26bdfa5, worktree `../repoready-mcp-plugin-track-c` | Skill, commands, README, CHANGELOG, decisions memory: tonight's server and the scope labels L1 check / L2 check | Committed locally; not pushed, not published. See "Plugin 2.0.0 on the server of 2026-10-13" below. |

Read the monorepo's DEVELOPMENT_CONTEXT.md and docs/MCP_SERVER.md at the matching pushed branch when changing tools. If the cloud task only has this repo, request the relevant server contract or inspect it using authorized repository access. Record ownership and contract changes here before overlapping Claude's work.

Save plans in docs/plans, durable lessons in docs/memory, and handoffs here. Keep machine credentials and personal integration details outside the shared repository.

## Context migration verification (2026-10-02)

Shared Markdown links and JSON settings validated. The setup script was exercised on an isolated temporary checkout for correct paths, preservation of unrelated settings, repeated-run idempotence and refusal to overwrite malformed settings. A scan of migrated plans/memory found no matches for common private-key, API-token or credential-URL patterns; this is a limited pattern scan, not a guarantee. No application code was changed, so the full runtime suites were not run. Claude was not restarted or asked to run a live model task during verification.

155 existing local worktrees across the two repositories were configured to use their repository's canonical migrated memory and their own docs/plans. Existing unrelated local settings were preserved; backups of pre-existing settings are kept locally under /private/tmp/repoready-agent-settings-20261002T100407Z. A local workspace-level CLAUDE.md supplies routing for older branches without the new shared files. The remote/cloud environment itself was not modified; commits and owner-authorized pushes are still required for cloud visibility.

## Review UX contract work — 2026-10-02

Codex owns `codex/review-ux-plugin-2026-10-02` (base `56fd16f`) in sibling `repoready-mcp-plugin-review-ux` for the client documentation accompanying monorepo `codex/review-ux-2026-10-02`. Scope: capability-gated 2.0 workflow, supplements, requirements, author/reviewer intent and the total check ceiling. Production v1 instructions, endpoint and manifests are preserved. No publication or paid analysis is authorised.

Review UX documentation is prepared in the task branch above: `docs/review-ux-v2-contract.md`, linked from the skill and README. Plugin JSON/local links and whitespace checks passed. Server/runtime verification is in the monorepo review-UX handoff. Nothing was published; the production endpoint and manifests are unchanged.

## Plugin 2.0.0 hand-off — 2026-10-10

Owner of this lane: Claude (local, for monorepo Track C item C.2). Branch `claude/plugin-v2`, created from `feat/mcp-v1.1` @ `752a28d` in the worktree `../repoready-mcp-plugin-v2`; the rewrite is commit `bb1075b`, this hand-off the commit after it. Nothing pushed, merged, tagged or published; `.mcp.json` (production URL) unchanged; no paid check run.

Server contract read (read-only) from the monorepo's local `staging` working tree at `eaebbad8`, which then held another session's staged, uncommitted MCP changes (the C.1 server work of `claude/item-1-14-5b-mcp-v3`): `docs/MCP_SERVER.md`, `docs/plans/32-track-c-surfaces.md` (C.1–C.3), `apps/api/src/modules/mcp/` (tool names, inputs, output schemas), `apps/api/src/modules/assessment/level-text.ts`. Re-check the tool names against the merged server before publishing.

Files: `skills/repoready/SKILL.md`, `commands/analyze.md`, `commands/status.md`, `README.md`, `CHANGELOG.md` (new), `.claude-plugin/plugin.json` and `marketplace.json` (2.0.0, new descriptions, marketplace `metadata.description`), `docs/CLOUD_SETUP.md` (validator commands), `docs/memory/plugin-v2-decisions.md` (new, the ten decisions taken under row 57), `docs/memory/MEMORY.md`, this file.

Checks run: `claude plugin validate .` (marketplace, strict: passed); `claude plugin validate .claude-plugin/plugin.json` (passed with one warning: the root `CLAUDE.md` is not loaded as plugin context, expected, it is development context; `--strict` fails on that warning only); `claude plugin validate skills` and `commands` (passed); `claude --plugin-dir . plugin details repoready` (2.0.0; skills analyze, repoready, status; MCP server repoready; about 146 tokens always on, the skill about 3.4k on invoke); `python3 -m json.tool` on both manifests, `.mcp.json` and `.claude/settings.json`; local Markdown links; `git diff --check`; every tool name in the skill, commands and README exists in the staging server; C.2's "Done when" grep (`0–100|reproducibility score|free trial|trial runs|must_have|Level [0-9N] of 3` over README, skills, commands) finds nothing; the zip exclusions tested with Info-ZIP. Not run: an agent session against staging end to end (a paid Materials check: needs the owner's or lead's go and a separately configured staging connection).

Next steps for the owner (publishing):
1. Before R1: optionally run the flow once against staging with a separate connection (`claude mcp add --transport http repoready-staging https://api.repoready.dev/api/mcp`, local plugin marketplace), on a small public repository in the Materials scope, after saying yes to its price.
2. At R1, when production serves MCP 2.0.0: push `feat/mcp-v1.1` and `claude/plugin-v2` (or merge `claude/plugin-v2` into `main`), push `main`, tag `v2.0.0` (`claude plugin tag` can make a `repoready--v2.0.0` tag). Do not merge into `main` before R1: `main` is what `/plugin marketplace add repoready-ai/mcp-plugin`, `npx skills add` and the Helmholtz skill source install, and production's 1.x server lacks the 2.x tools.
3. Then the Helmholtz pull request (C.3, below), and re-point the plugin checkouts' memory to the main checkout (Track E).

### Helmholtz entry (monorepo C.3): text that must change

Checked read-only in `helmholtz-agent-skills`, branch `repoready-plugin` @ `2f17682`; not edited.
- `sources.json:43-55` tracks this plugin's `main` (`"ref": "main"`, `"path": "skills"`): the skill-only install picks up 2.0.0 as soon as it is on `main`, so `main` must not get 2.0.0 before R1. `"about"` (`:52`) "Analyze research code for reproducibility via the RepoReady MCP server." may stay, or become "Check research code for reproducibility via the RepoReady MCP server."
- `.claude-plugin/marketplace.json:77-90`: `"version": "1.0.1"` → `"2.0.0"`; `"description": "Research-code reproducibility analysis via RepoReady MCP"` → "Reproducibility checks for research code via RepoReady MCP: one level per check, cited issues to fix".
- `README.md:39`: "Score research code for reproducibility and act on cited findings via RepoReady MCP." → "Check research code for reproducibility (one level per check, L0 Incomplete to L2 Rerunnable) and act on cited issues via RepoReady MCP."
- `docs/third-party/repoready.md:5-6`: "Score a research codebase for reproducibility (0–100) and act on findings with file:line citations via the RepoReady MCP server." → "Check a research codebase, or a paper's code and data, for reproducibility: one level per check (L0 Incomplete, L1 Available, L2 Rerunnable; L3 Re-executed and L4 Reproduced not offered yet) with the area results beside it, and issues with file:line citations to fix, via the RepoReady MCP server."
- same file `:14-18`: "(institutional email joins an org plan; otherwise a free trial)" → "(institutional email joins your organization's plan; otherwise add your own OpenRouter API key: there are no free checks)"; "Runs are metered: trial runs or your organization's plan, which may enforce a daily cap." → "Every check is priced first and starts only after your yes; your organization's plan or your own OpenRouter key pays, and organizations may set a daily cap. A check that cannot finish is not charged." The data-handling sentence (zip without `.git`, dependency folders and `.env` files) stays.
- same file, claude.ai section: "The plugin bundles the skill, the command, and the RepoReady MCP connector" → "the skill, the `/repoready:analyze` and `/repoready:status` commands, and the RepoReady MCP connector".
- Before the pull request, check the state of the earlier upstream review pull request and the local branch `cursor/4fe7d4f0` (needs network).

## Plugin 2.0.0 brought in line with the R1 server — 2026-10-12

Owner of this change: Claude (build agent of the monorepo lead session, overnight). Branch `claude/plugin-v2`, on `b0ccc0b`; the change is the commit after it. Nothing pushed, merged, tagged or published; `.mcp.json` and the manifests' version (2.0.0) unchanged (no field change needed it); no paid check run, no live MCP call.

Server contract read (read-only) at the R1 release head: monorepo `staging` `d1e02bcd` in `repoready-monorepo-staging/.claude/worktrees/day-integration`: `docs/MCP_SERVER.md` (2.0.0), `apps/api/src/modules/mcp/mcp-v2-tools.service.ts` (`priceText`, `quoteOut`, tool descriptions), `mcp-v2-schemas.ts` (intents, quote options, issue rows), `mcp-ladder-text.ts` (Impact labels and order, supplementary findings), `apps/api/src/config/investigate.json` (`userConfirm.enabled: false`), `apps/web-app/app/lib/state-words.ts`, decision-log rows 86-95 of `docs/plans/00-overview.md`.

What changed:
- **No "Confirm this"** (decision-log row 92): the skill no longer offers `intent: 'confirm'` or reads `confirmFirst`; it says every check confirms its uncertain findings itself (`get_run.confirming`), the server refuses `confirm` with `intent_retired`, and "I fixed this" (which checks the project again first, then the issue; owner only, never on a sponsorship) is the only follow-up on one finding. `confirmFirst` / `confirmPriceHintUsd` are named as deprecated, to be ignored.
- **Expected cost only** (rows 86, 91): the user hears "about $X" (`expectedUsd`, else `priceUsd`; the server's `next` / `note` texts word it); `ceilingUsd`, `chargeUsd`, `holdUsd` are machine fields never quoted. Skill, `commands/analyze.md`, README (flow and tools table) and CHANGELOG.
- **Words**: Impact labels and order as `IMPACT_LABELS` / `IMPACT_ORDER` (Blocks L1, Blocks L2, Caps at L1, Blocks L3, Blocks Automation, Warning); supplementary findings are Warnings (row 87); finding states Missing / Warning / Unresolved / Available / Not applicable (row 93; `notDecided` = Unresolved); no preview.
- **Other contradictions with the release server fixed or filled in**: `get_update` (free, what a new check would read), `lookup_public_assessment` only when listed (registry off by default, row 95), `targetJournal` and the Journal policy area, `checkVersion` `{type, value}`, `rootCauses`, the agent-policy refusals, `payer.free`, `recipientEmail` only on request, badge issuing and the README pull request not MCP tools, a revised manuscript only through the web app.

Checks run: `python3 -m json.tool` on both manifests, `.mcp.json`, `.claude/settings.json`; `claude plugin validate .` (passed), `claude plugin validate .claude-plugin/plugin.json` (passed with the expected root-`CLAUDE.md` warning), `claude plugin validate skills` and `commands` (passed); `claude --plugin-dir . plugin details repoready` (skill about 4.3k tokens on invoke, 146 always on); every backticked snake_case name in the skill, commands and README is a registered tool or a server value at `d1e02bcd`; local Markdown links; `git diff --check`; C.2's "Done when" grep finds nothing.

Notes for the server lane (not plugin blockers): `docs/MCP_SERVER.md` says "26 tools in all", but `d1e02bcd` registers 27 (the 26 plus `get_update`; `lookup_public_assessment` is a 28th while the registry is on). The `list_issues` markdown still words a lead "(not decided in this check)" where the web says "Unresolved"; `priceText` reads "up to $Y" for a quote stored before `expectedUsd` without a price; `cancel_run` can still say "The free-trial check is given back".

Next step (unchanged): publish at R1 as in the 2026-10-10 hand-off's steps 2-3, after production serves MCP 2.0.0 from this release head. Re-read the tool list against production once it is live.

## Plugin 2.0.0 on the server of 2026-10-13

Owner of this change: Claude (Track C agent of the monorepo lead session). Branch `claude/plugin-v2-1013`, created from `claude/plugin-v2` @ `26bdfa5` in the worktree `../repoready-mcp-plugin-track-c` (no existing checkout was switched). Nothing pushed, merged, tagged or published; `.mcp.json` and the version (2.0.0) unchanged; no paid check, no live MCP call.

Server contract read (read-only): monorepo `claude/integration-1013` @ `8583813a` (`apps/api/src/modules/mcp/`: 28 tools registered, 27 while the registry is off; the diff since `d1e02bcd`), its `docs/memory` (`funds-graceful`, `expected-cost-holds`), decision-log rows 116-145, and the uncommitted work of `claude/b6-b7` (`list_issues` `reviewScope` / `outsideScope` / `scopeNote` after a Materials check).

What changed:
- **Scope labels** (owner 2026-10-13): the user hears "L1 check" (are the code, data and software behind each result shared?) and "L2 check" (the full review without running the code: workflow, integrity, automation, reuse); `scope` ids `materials` / `workflow` unchanged; "Materials" stays the area name; where a tool text still says "Materials and workflow" the agent says "L2 check" (decision 13).
- **"Unresolved"** in the tools' issue markdown (was "not decided in this check").
- **Materials hold code, data or both and can have several roles** (`contents`, `roles`) where the user reviews what was found.
- **Check incomplete from a dry payer key**: charged what it spent, no rerun, its answers kept; Check again on the same payer continues it without paying for them again. **Cancel**: charged what it spent until it stopped; the project keeps its last finished check.
- **After an L1 check** `list_issues` may leave out Workflow and Automation findings (`outsideScope`, `scopeNote`; on `claude/b6-b7`, not yet merged): the skill offers "Continue to L2".

Checks run: `python3 -m json.tool` on both manifests, `.mcp.json`, `.claude/settings.json`; `claude plugin validate .` (passed), `claude plugin validate .claude-plugin/plugin.json` (passed with the expected root-`CLAUDE.md` warning), `claude plugin validate skills` and `commands` (passed); the Helmholtz `scripts/lint_skills.py skills` (1/1 passed); `claude --plugin-dir . plugin details repoready` (2.0.0; skill about 4.4k tokens on invoke, 146 always on); every backticked snake_case name in README, skill and commands exists in the server code at `8583813a`, and all 28 registered tools are in the README table; local Markdown links; `git diff --check`; C.2's Done-when grep finds nothing.

Next step: R1 is out (2026-10-13), so production should serve MCP 2.0.0: re-read production's `tools/list` once, then the owner pushes `feat/mcp-v1.1`, `claude/plugin-v2` and this branch (or merges this branch into `main`), pushes `main` and tags `v2.0.0`. Then the Helmholtz pull request (monorepo C.3; the entry text is committed on Helmholtz branch `claude/repoready-plugin-v2`).
