# Connecting RepoReady (not signed in)

Read this file only when `SKILL.md`, Step 1, item 3 finds the RepoReady
tools missing, a sign-in placeholder, or `get_account` unauthorized. Read
nothing and call nothing else until the user has answered.

Tell the user, in one message and in these words:

> Every self-check needs a free RepoReady account, which takes one
> sign-in. RepoReady gets the sign-in and one account call, never your
> code, PDF or report; with a paper, also its public links. To
> connect: *the line and the sign-in for this agent, below*. Say yes
> and I will add it for you, and RepoReady's platform skill if it is
> missing. Then start the self-check again.

| This agent | The one line that adds the server | Then the sign-in |
|---|---|---|
| Claude Code | `claude mcp add --transport http repoready https://api.repoready.ai/api/mcp` | restart Claude Code, run `/mcp` and finish the browser sign-in |
| Claude Code, started by `/repoready:self-check` (the plugin brought the server) | none | run `/mcp` and finish the browser sign-in |
| Codex | `codex mcp add repoready --url https://api.repoready.ai/api/mcp` | `codex mcp login repoready` |
| Cursor | in `~/.cursor/mcp.json`: `{ "mcpServers": { "repoready": { "url": "https://api.repoready.ai/api/mcp" } } }` | sign in when Cursor's MCP settings ask |
| Another agent | in its MCP settings, the remote server `https://api.repoready.ai/api/mcp` (Streamable HTTP, OAuth) | connect it and finish the browser sign-in |

The server is already added when only the sign-in is missing: then
give only the sign-in. The browser sign-in takes the user's email (a
code comes to the inbox); a first sign-in makes the free account.

**On the user's yes, finish the install yourself:** run this agent's
line (Cursor: add the entry to `~/.cursor/mcp.json` and keep everything
already there; another agent: only if you know where its settings are,
else tell them). If the `repoready` skill is not among your skills,
also run `npx skills add repoready-ai/mcp-plugin --skill repoready`.
Change nothing else. Say what you changed, then give the sign-in: you
cannot restart the agent or finish the browser sign-in for them. If a
line fails, show it and let the user run it. Without a yes, run
nothing.

Wait for the answer. If the user declines, the self-check does not
run: say so in one sentence, pointing to
https://repoready.ai/self-check, and do not bring up the account or
the sign-in again in this check.
- **The user asked for a check with no RepoReady connection:** the
self-check cannot run without the account. Say the first sentence
above and ask whether to sign in; read nothing and call nothing until
they answer. On a no, the one sentence and the link above.
