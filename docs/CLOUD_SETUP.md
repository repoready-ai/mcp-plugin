# Plugin cloud setup

Connect `repoready-ai/mcp-plugin` and select a pushed branch that contains the task's baseline and these shared documents. Local feat/mcp-v1.1 is ahead of main; its publication must be verified. This is a static plugin repository with no package.json or application dependency installation.

Run from the checkout root:

```sh
python3 scripts/configure-agent-context.py
```

This routes Claude plans and automatic memory into the repository, preserving existing local settings. Restart/reload Claude and verify /context and /memory. Codex reads AGENTS.md; both agents use docs/plans, docs/memory and DEVELOPMENT_CONTEXT.md. Credentials, authenticated browser sessions and local-only branches are not inherited.

Validate all JSON manifests, check local Markdown links and review consistency among README, .mcp.json, .claude-plugin manifests, commands and skill. Read the matching monorepo server contract before tool changes. Actual plugin installation and OAuth/client smoke tests require an appropriately configured client; a syntax check is not evidence of successful sign-in or a live tool call.

Use a separate development MCP connection for staging. An edit task does not authorize paid analyses, publishing/version releases, marketplace writes or changes to production endpoint configuration. Task branch pushes and PR creation require explicit authorization (a request to create a PR provides it); shared-branch integration remains owner-controlled.
