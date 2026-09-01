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
  repository.

## Accounts

- **New to RepoReady?** Sign in once at [repoready.ai](https://repoready.ai)
  with your email (a magic-link code is sent to your inbox). If your
  organization uses RepoReady, use your institutional email — you'll join
  your organization automatically and analyses are funded by its plan.
  Otherwise you start with free trial runs.
- **Existing account?** Nothing to prepare — the OAuth sign-in below uses
  your existing account.

## Install — Claude Code

```
/plugin marketplace add repoready/claude-plugin
/plugin install repoready@repoready
```

Restart Claude Code, run `/mcp`, and complete the browser sign-in.
Then either run `/repoready:analyze` or just ask, e.g. *"how reproducible is
this repo?"*.

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
npx skills add repoready/claude-plugin
```

## claude.ai and Claude Desktop

Add the server URL as a custom connector under **Settings → Connectors**.
On Team/Enterprise plans, an organization Owner adds it once under
**Organization settings → Connectors**; members then click **Connect**.

## For maintainers

The server URL in [.mcp.json](.mcp.json) defaults to production and can be
overridden per machine without editing the plugin:

```bash
export REPOREADY_MCP_URL="https://<your-non-production-host>/api/mcp"
```

To test the plugin before (or without) publishing, add this folder as a
local marketplace:

```
/plugin marketplace add /path/to/repoready-claude-plugin
/plugin install repoready@repoready
```
