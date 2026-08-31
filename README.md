# RepoReady Claude Code plugin

Analyze the reproducibility of research code from Claude Code using
[RepoReady](https://repoready.dev). The plugin bundles:

- the **RepoReady MCP server** connection (`https://api.repoready.dev/api/mcp`,
  OAuth sign-in on first use),
- a **skill** that teaches Claude the analyze → fix → re-analyze workflow,
- the **`/repoready:analyze`** command to analyze the current repository.

## Install

```
/plugin marketplace add repoready/claude-plugin
/plugin install repoready@repoready
```

First use opens a browser sign-in. Organization members: use your
institutional email ("Sign in with Microsoft") — analyses are funded by your
organization's plan.

Not using Claude Code? Point any MCP client at
`https://api.repoready.dev/api/mcp` — see the RepoReady docs.
