# RepoReady for coding agents

Analyze the reproducibility of research code from your coding agent using
[RepoReady](https://repoready.ai). RepoReady scores a codebase 0–100 and
returns findings with file:line citations and fix suggestions, via a remote
MCP server:

```
https://api.repoready.ai/api/mcp        (streamable HTTP, OAuth sign-in)
```

This repository is both a **Claude Code plugin marketplace** and an
**agent-skills source**. It bundles:

- the MCP server connection,
- a **skill** ([`skills/repoready/`](skills/repoready/SKILL.md)) that teaches
  agents the analyze → fix → re-analyze workflow,
- the **`/repoready:analyze`** command (Claude Code) to analyze the current
  repository, and **`/repoready:status`** to show your projects and running
  analyses.

## Tools

The server (version 1.1.0) offers:

| Tool | What it does |
|---|---|
| `get_account` | Who is signed in, who pays for analyses (organization, own key, plan or free trial), the organization's daily cap, connected GitHub accounts |
| `list_projects` | Your projects, found by name or by repository (`owner/repo`, a GitHub URL or the git remote), with their latest run |
| `get_project` | One project: code versions, latest results, analyses in progress, badge |
| `list_runs` | Your analyses across projects or for one project, e.g. the ones still running |
| `get_run_status` | Progress of one analysis |
| `get_report` / `get_findings` | Results: score, summary, findings with file:line citations and suggested fixes |
| `request_upload_url` | Upload a zip of your local code |
| `analyze_repo` | Start an analysis of a GitHub repository (private ones through the RepoReady GitHub App) or an upload; it joins your existing project for that repository |
| `create_share_link` / `revoke_share_link` | Make a read-only report link, and withdraw it |

Agents are told to look for existing projects before starting anything, and
to ask you before any analysis, since analyses are paid.

## Accounts

- **New to RepoReady?** Sign in once at [repoready.ai](https://repoready.ai)
  with your email (a magic-link code is sent to your inbox). If your
  organization uses RepoReady, use your institutional email — you'll join
  your organization automatically and analyses are funded by its plan.
  Otherwise you start with free trial runs.
- **Existing account?** Nothing to prepare — the OAuth sign-in below uses
  your existing account.

## Data handling & cost

Analyses run on RepoReady's servers: for local projects the workflow zips
your code (excluding `.git`, dependencies, caches, and `.env` files) and
uploads it for analysis. Don't run it on code that must not leave your
machine, and extend the zip exclusions for anything else you don't want
uploaded. Runs are metered — free trial runs or your organization's plan,
which may enforce a daily cap.

## Install — Claude Code

```
/plugin marketplace add repoready-ai/mcp-plugin
/plugin install repoready@repoready
```

Restart Claude Code, run `/mcp`, and complete the browser sign-in.
Then either run `/repoready:analyze` (or `/repoready:status`) or just ask,
e.g. *"how reproducible is this repo?"*.

Prefer no plugin? The server alone:

```
claude mcp add --transport http repoready https://api.repoready.ai/api/mcp
```

## Install — other coding agents

The server works with any MCP client that supports streamable HTTP + OAuth.

**Codex**

```
codex mcp add repoready --url https://api.repoready.ai/api/mcp
codex mcp login repoready
```

**Cursor** — add to `~/.cursor/mcp.json`:

```json
{ "mcpServers": { "repoready": { "url": "https://api.repoready.ai/api/mcp" } } }
```

**Workflow skill (optional, any agent)** — installs the RepoReady workflow
instructions into your agent's skills directory:

```
npx skills add repoready-ai/mcp-plugin
```

## claude.ai and Claude Desktop

The plugin brings the connector along: under **Customize → Plugins → Add →
Add marketplace**, sync `repoready-ai/mcp-plugin`, add the **repoready**
plugin, and click **Connect** on its RepoReady connector. Alternatively, add
the server URL as a custom connector under **Customize → Connectors**.
On Team/Enterprise plans, an organization Owner adds it once under
**Organization settings → Connectors**; members then click **Connect**.

## Claude Science

Add the server under **Connectors → Add connector → Remote URL** (the
default transport, Streamable HTTP, is the right one), then connect to sign
in. The workflow skill is optional: **Skills → Add skill → Import from
GitHub** with `repoready-ai/mcp-plugin`.

## For maintainers

The server URL in [.mcp.json](.mcp.json) is the production endpoint. To
test against a non-production host, either edit `.mcp.json` in a local
checkout installed as a local marketplace (below), or add the server
directly without the plugin:

```bash
claude mcp add --transport http repoready-dev https://<your-non-production-host>/api/mcp
```

To test the plugin before (or without) publishing, add this folder as a
local marketplace:

```
/plugin marketplace add /path/to/mcp-plugin
/plugin install repoready@repoready
```
