# RepoReady MCP plugin development context

Repository: `repoready-ai/mcp-plugin`. This distributes the remote connection, workflow skills and Claude commands. The MCP server is a separate, private codebase.

This repository is public, and so is its history. Keep local machine paths, non-production hosts, internal branch names, credentials, hand-offs, internal decisions and test sets out of every committed file and commit message. Maintainers keep those in the private monorepo, under `docs/plugin-notes/`.

## Contract and packaging

- Production MCP connection is `https://api.repoready.ai/api/mcp`, Streamable HTTP with OAuth. Tests against a non-production server use a separately configured connection (README, "For maintainers"); never change the shipped production URL for a test.
- Keep README, both skills, commands, `.mcp.json`, `plugin.json`, `marketplace.json` and `CHANGELOG.md` consistent with the server version. Adapt consumer wording only when the corresponding contract is live on the production server.
- Preserve "find existing work first", upload exclusions (especially `.env`, `.git`, dependencies and caches), OAuth/account instructions, explicit paid-run approval and data-handling explanations.
- RepoReady also appears in the Helmholtz agent-skills marketplace, which installs from this repository's `main`. Its entry is updated by a pull request to that marketplace, separately from this repository.
- Avoid UI claims based on old notes: verify current product paths for each supported client.
