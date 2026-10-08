# Shared agent guidance

Read `docs/DEVELOPMENT_CONTEXT.md` and `docs/memory/MEMORY.md` at session start, then the relevant plan from `docs/plans/README.md`. Read `CLAUDE.md` for repository commands and app-specific `AGENTS.md` / `CLAUDE.md` before editing an app. Do not import `CLAUDE.md` back into this file: Claude imports this file from there.

## Save context in the repository

- Shared instructions belong in `AGENTS.md`; Claude-specific setup belongs in `CLAUDE.md` and `.claude/settings.json`.
- Plans belong in `docs/plans/`; use descriptive filenames and keep the index current. Update the existing plan for follow-up work.
- Durable project decisions and lessons belong in `docs/memory/`, indexed by `docs/memory/MEMORY.md`. Keep the index short; put detail in topic files. Do not save secrets, personal account details, session transcripts or machine-specific credentials there.
- Current status, branch ownership and handoffs belong in `docs/DEVELOPMENT_CONTEXT.md`. At handoff, record the actual branch/commit, files touched, checks completed and next step. Treat dated status as a snapshot and recheck Git before acting.
- Do not use `~/.claude/plans`, private auto-memory or temporary scratchpads as the sole source for a project decision or deliverable. Promote useful conclusions into the repository before finishing a task. Historical local copies are migration sources, not authoritative plans.
- Latest explicit user instructions take precedence. A newer dated decision supersedes an older entry. Imported historical notes are leads to verify, not proof of the current implementation or deployment.

## Concurrent work and delivery

- Inspect `git status`, `git worktree list` and relevant branch history before edits. Work on a task branch in its own worktree; do not switch another agent's checkout or stash its changes.
- Record task ownership before overlapping work. Never overwrite another agent's edits. Confirm existing in-flight work before integration into a shared branch.
- Do not push, merge into a shared release branch, publish, deploy, or run paid analysis without authorization for that action. A cloud task explicitly requesting a PR authorizes the task branch push and PR, not a release merge or deployment. Otherwise provide local changes and a handoff for the owner.
- Keep verification proportionate. Prefer the cheapest decisive checks. Automated live analyses default to low effort and must respect the explicitly authorized cost ceiling; no paid probe is implied by a code or documentation task.
- Never commit `.env` values, tokens or database dumps. Configure external credentials in the environment's secret store; use a disposable local database for tests.

## Claude setup

Run `python3 scripts/configure-agent-context.py` once in a new checkout (also as part of cloud setup). It preserves existing local settings and resolves Claude's absolute auto-memory path to this checkout's `docs/memory`. New plans always stay inside the checkout; Claude rejects plan directories outside its project root. `.claude/settings.json` routes new plans to `docs/plans`. Reload/restart Claude after settings change, then use `/context` and `/memory` to confirm the loaded instructions and memory directory. If automatic memory is unavailable or disabled by policy, explicitly read and update the same repository documents.

## Plugin constraints

This is the client plugin/skills distribution, not the SaaS implementation. The MCP server lives in the monorepo API. Keep `.mcp.json`, `.claude-plugin` manifests, commands, skill and README consistent. Preserve upload exclusions, account/data-handling explanations, OAuth and cost approval. Production endpoint is `https://api.repoready.ai/api/mcp`; use an explicitly configured development connection for staging tests. Do not infer permission to start a paid analysis from permission to edit this repository.
