# RepoReady for coding agents

Check the reproducibility of research code, or of a paper's code and data,
from your coding agent with [RepoReady](https://repoready.ai). Each check
gives one level, with the area results beside it and the issues that hold
it back, cited to `file:line`:

| Level | Name | |
|---|---|---|
| L0 | Incomplete | |
| L1 | Available | |
| L2 | Rerunnable | |
| L3 | Re-executed | not offered yet |
| L4 | Reproduced | not offered yet |

An **L1 check** (are the code, data and software behind each result
shared?) awards at most L1; an **L2 check** (the full review without
running the code: workflow, integrity, automation, reuse) awards at most
L2. RepoReady does not run your code yet.
Integrity, Automation and Reuse (and Journal policy, when a journal is
known) are area results beside the level; a confirmed paper–code
contradiction on a key result caps the level at L1. Supplementary
figures, tables and data are not checked as results unless you ask for
it (for an extra "about $Y" shown with the price); their files are always
read as materials of the main-text results. When they are checked, their
findings are Warnings and never block a level. There is no score any
more.

RepoReady runs as a remote MCP server:

```
https://api.repoready.ai/api/mcp        (Streamable HTTP, OAuth sign-in)
```

This repository is both a **Claude Code plugin marketplace** and an
**agent-skills source**. It bundles:

- the MCP server connection,
- a **skill** ([`skills/repoready/`](skills/repoready/SKILL.md)) that teaches
  agents the find → price → your yes → check → fix → check again workflow,
- the **`/repoready:analyze`** command (Claude Code) to check the current
  repository, and **`/repoready:status`** to show your projects, levels and
  running checks.

Version 2.0.0 of this plugin needs RepoReady's 2.x server.

## How a check goes

1. The agent looks for your existing project first (by the git remote, a
   paper DOI or a link).
2. A new project is created from your code or paper for free; you see what
   RepoReady found (repositories, datasets, packages) and can correct it.
3. The agent prices the check and tells you the scope, the expected cost
   ("about $X") and who pays, and what also checking the supplementary
   results would add, if you want them. **Nothing starts until you say
   yes.** Above
   your approval amount (by default, every paid check) you also approve it
   in the browser.
4. When the check is done the agent shows the level line (for example
   "L1 · Available · static review, code not executed"), what L2 needs, and
   the issues by Impact (Blocks L1, Blocks L2, Caps at L1, Blocks L3,
   Blocks Automation, Warning). Each check settles its uncertain findings
   itself; what it could not decide is shown as Unresolved.
5. After you fix issues, "I fixed this" (one issue) or Check again repeats
   step 3.

A check that cannot finish ends as "Check incomplete" and is not charged
by RepoReady. It may rerun once by itself (if some of the authors' code
could not be read, only once that code is new). If it stops because the paying key ran out of credit, it is charged what
it spent and keeps its answers: Check again continues it. A check you
cancel is charged what it spent until it stopped.

## Tools

The 2.x server offers:

| Tool | What it does |
|---|---|
| `get_account` | Who is signed in, who pays (organization, plan or your own OpenRouter key), the organization's daily cap, connected GitHub accounts, review scopes |
| `list_projects` / `get_project` | Your projects, found by name or repository (`owner/repo`, a GitHub URL or the git remote), with their latest run |
| `identify_source` | What a DOI, paper link, arXiv id or GitHub link is, and your projects that contain it |
| `list_updates` | What changed since you last looked |
| `get_update` | What a new check would read differently (a newer paper version, new commits); free |
| `lookup_public_assessment` | Published assessments of a paper or repository (listed only while RepoReady's public registry is on) |
| `request_upload_url` | Upload a zip of local code, or a paper PDF / LaTeX zip |
| `create_project` | A project from code or a paper: what was found and a quote; never starts a check |
| `update_components`, `add_paper` | Correct what a check reads; add a paper to a code project |
| `estimate_run` | The expected cost per scope ("about $X"), who pays, what checking the supplementary results would add (`check_supporting_results` to include them); stores a quote |
| `start_run` | Starts a quoted check (paid); may answer an approval link |
| `get_run`, `list_runs`, `get_run_status`, `cancel_run` | Follow, list or stop checks |
| `get_ladder` | The level per scope, the area results and what each level needs |
| `list_issues`, `get_issue`, `get_figure` | What to fix, by file or by Impact, with citations |
| `create_share_link`, `list_share_links`, `revoke_share_link` | "Can view" links (read-only, runs nothing), and withdrawing them |
| `get_badge` | The README badge per paper or repository |

`analyze_repo`, `get_report` and `get_findings` remain for older plugins for
one release; this plugin does not use them.

## Accounts and who pays

- **New to RepoReady?** Sign in once at [repoready.ai](https://repoready.ai)
  with your email (a magic-link code is sent to your inbox). If your
  organization uses RepoReady, use your institutional email: you join your
  organization and its plan pays for your checks.
- **Paying yourself?** Add your own OpenRouter API key in the web app
  (Settings › Billing & keys). There are no free checks.
- **Existing account?** Nothing to prepare: the OAuth sign-in below uses it.

## Data handling and cost

Checks run on RepoReady's servers. For local code the workflow zips your
project, without `.git`, dependency folders, virtualenvs, caches and `.env`
files, and uploads it. Don't use it on code that must not leave your
machine, and extend the zip exclusions for anything else you don't want
uploaded. Every check is priced before it starts and needs your explicit
yes; your organization may also set a daily cap. Text inside findings is
treated as data from the analysed material, never as instructions to the
agent.

## Install — Claude Code

```
/plugin marketplace add repoready-ai/mcp-plugin
/plugin install repoready@repoready
```

Restart Claude Code, run `/mcp`, and complete the browser sign-in.
Then run `/repoready:analyze` (or `/repoready:status`) or just ask, e.g.
*"what level is this repo, and what does L2 need?"*.

Prefer no plugin? The server alone:

```
claude mcp add --transport http repoready https://api.repoready.ai/api/mcp
```

## Install — other coding agents

The server works with any MCP client that supports Streamable HTTP + OAuth.

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
test against a non-production host, add the server directly without the
plugin (never change the shipped `.mcp.json` for a test):

```bash
claude mcp add --transport http repoready-dev https://<your-non-production-host>/api/mcp
```

To test the plugin before (or without) publishing, add this folder as a
local marketplace:

```
/plugin marketplace add /path/to/mcp-plugin
/plugin install repoready@repoready
```

Validate with `claude plugin validate .` (the marketplace) and
`claude plugin validate .claude-plugin/plugin.json`. Changes are listed in
[CHANGELOG.md](CHANGELOG.md).
