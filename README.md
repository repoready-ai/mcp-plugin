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
it; their files are always read as materials of the main-text results.
When they are checked, their findings are Warnings and never block a
level. There is no score any more. Platform assessments are paid in credits by
your institute or a journal; there are no own keys and no dollar prices.

RepoReady runs as a remote MCP server:

```
https://api.repoready.ai/api/mcp        (Streamable HTTP, OAuth sign-in)
```

This repository is both a **Claude Code plugin marketplace** and an
**agent-skills source**. It bundles:

- the MCP server connection,
- a **skill** ([`skills/repoready/`](skills/repoready/SKILL.md)) that teaches
  agents the find → price → your yes → check → fix and answer → check the
  fixes workflow,
- the **`/repoready:analyze`** command (Claude Code) to check the current
  repository, and **`/repoready:status`** to show your projects, levels and
  running checks,
- the **free self-check** ([`skills/reproducibility-self-check/`](skills/reproducibility-self-check/SKILL.md),
  `/repoready:self-check`): a check in your own agent, with a free
  RepoReady account (see below).

Version 2.1.0 of this plugin needs RepoReady's 2.x server for its checks;
its to-do plan needs a server with `list_todos` (with an older server it
falls back to the issue list), and answering findings, "Check N fixes" and
"Ask my institute" from your agent need server 2.2.0 (with an older server
you do these in the web app). A self-check needs a free account and, from
the server, only its sign-in (any 2.x server).

## Free self-check

The self-check skill is new in this plugin version: v0.1, its first
release. It runs in your own coding agent (Claude Code, Codex, Cursor, …),
on the subscription you already use. Your code, PDF, report and
`findings.json` are never sent to RepoReady; the agent reads the public
pages it needs (the paper, public repositories, package indexes).

- **Every self-check needs a free RepoReady account**, which takes one
  sign-in (your email; a code comes to your inbox, and the first sign-in
  makes the account). RepoReady receives the sign-in and one `get_account`
  call, nothing of the work. If you are not signed in, the agent says so
  before it reads anything, gives you the one line to connect, and waits.
- **Code alone**: a method, tool or package gets the Software reuse result
  R1–R4 ("Reusable" or "Reuse: n of 4"); analysis code without its paper
  gets "No level · add the paper".
- **A paper with its code** (give it a PDF or DOI): RepoReady also
  receives, when the paper has them, its public link and the public
  repositories it names, to find the paper's materials; with a private PDF
  and no public link, nothing beyond the account call. You get an
  indicative level, self-assessed and at most L2 (L0 Incomplete, L1
  Available, L2 Rerunnable), over the Materials and the workflow basics of
  RepoReady's public [checklist](https://repoready.ai/checklist) and
  [guides](https://repoready.ai/docs/checks).
- **Main-text results, static**: every main-text figure and table that
  shows results; the code is read, not run, unless you say yes. Every finding cites
  `file:line` and comes with a to-do and who can do it ("Your coding agent
  can fix this", "Your agent can help · needs your answer", "Authors only").
- **It confirms first.** With no paper given, it looks for one (for a public
  repository, also on the web) and says so when it finds none. Before the
  audit it shows the paper, code and data it will use and waits for your
  confirmation.
- **What can change the level is looked at.** Paper and code are compared
  when a check would otherwise reach L2, and each input resting on a deposit
  is looked up in the deposit's public file list.
- **Not checked**, and the report says so: Integrity below that point,
  anything in deposits beyond their public file lists, supplementary
  results, verification by a second model, L3/L4.
- **The report**: `repoready-self-check/<date>-<slug>.html` and `.md` (print
  the HTML from your browser to get a PDF), plus the `findings.json` behind
  them. It says "Self-check · user generated · not a RepoReady
  certification" in its header and footer, carries a SELF-CHECK watermark,
  uses grey instead of the level colours, names the agent, the model, the
  skill's version, the date and the commit, and shows "Since the last
  self-check: n fixed · n still open · n new" when you run it again.

**Signed in.** A check with a paper finds the paper's materials with
RepoReady's free discovery when the paper has public links (repositories,
deposits with their file lists, supplements, archived links). If you say
yes to them, the self-check can also work through the to-dos of a platform
assessment you already hold (fix or answer each finding, then "Check N fixes"
after you agreed to its credits and who pays), and "Ask my institute" when
nobody pays for your platform assessments. Your code, paper file and report are
never sent, and the report never shows your account.

Ask your agent: "Check the reproducibility of this paper" or "of this
codebase" (with the paper's PDF or DOI if you have one). In Claude Code,
`/repoready:self-check` does the same.

**Install.** The easiest way is to paste this into your agent; it reads the
steps for the product it is:

```
Set up the RepoReady self-check by following https://repoready.ai/setup.md, then sign me in.
```

To do it by hand: in Claude Code, the plugin brings both skills and the server
in one step:

```
/plugin marketplace add repoready-ai/mcp-plugin
/plugin install repoready@repoready
```

Restart Claude Code, run `/mcp` and complete the browser sign-in (with your
email; a first sign-in makes the free account): every self-check needs it.

In any other agent, install both skills:

```
npx skills add repoready-ai/mcp-plugin --skill reproducibility-self-check
npx skills add repoready-ai/mcp-plugin --skill repoready
```

Then add the server with your agent's one line and sign in (every
self-check needs the free account). If something is missing when you start
a self-check, the agent says what and, on your yes, adds it:

- **Claude Code:** `claude mcp add --transport http repoready https://api.repoready.ai/api/mcp`,
  then restart it, run `/mcp` and complete the browser sign-in.
- **Codex:** `codex mcp add repoready --url https://api.repoready.ai/api/mcp`,
  then `codex mcp login repoready`.
- **Cursor:** in `~/.cursor/mcp.json`,
  `{ "mcpServers": { "repoready": { "url": "https://api.repoready.ai/api/mcp" } } }`,
  then sign in when Cursor's MCP settings ask.
- **Other clients:** see
  [Install — other coding agents](#install--other-coding-agents).

The rubric is copied from RepoReady's public guides
([`skills/reproducibility-self-check/references/`](skills/reproducibility-self-check/references/)); the
report is rendered by a standard-library Python script
([`render_report.py`](skills/reproducibility-self-check/scripts/render_report.py)), or by
your agent from the HTML template when Python is missing. Platform assessments,
whose levels, share links and README images count, come through institutes
and journals: [repoready.ai/self-check](https://repoready.ai/self-check).

## How a check goes

1. The agent looks for your existing project first (by the git remote, a
   paper DOI or a link).
2. A new project is created from your code or paper for free; you see what
   RepoReady found (repositories, datasets, packages) and can correct it.
3. The agent prices the check and tells you the scope, the credits and
   who pays ("2 credits · billed to <payer>"; a large paper counts double),
   and checks the supplementary results only if you ask. **Nothing starts
   until you say yes.** Above your approval threshold (by default, every
   check that costs a credit) you also approve it in the browser.
4. When the check is done the agent shows the level line (for example
   "L1 · Available · static review, code not executed"), what L2 needs, and
   the to-dos: the same plan as the web app's To-dos view (to reach L1, to
   reach L2, then what is optional beside the level), each finding's steps
   in order, steps with alternatives ("Either … or …"), and who can do
   each ("Your coding agent can fix this", "Your agent can help · needs
   your answer", "Authors only").
   Ask for "only what to do" to see just the open steps. The issues are
   also listed by Impact (Blocks L1, Blocks L2, Caps at L1, Blocks L3,
   Blocks Automation, Warning). Each check settles its uncertain findings
   itself; what it could not decide is shown as Unresolved.
5. Then you and your agent answer each finding: **Fixed** ("Mark as
   fixed": it reads "Marked fixed · not checked yet" until a check
   decides), **Wrong** ("This is wrong…": a free re-check with the places
   to look) or **Won't change** ("Explain why", with your reason: it leaves
   the to-dos and is shown as "Authors' response" to people you share
   with). No answer changes the level. **"Check N fixes"** checks every
   finding you marked fixed in one check, 0 credits within 3 per version;
   Check again (1 credit) after larger changes. Each repeats step 3: the
   credits, who pays, your yes.
   For a journal's request (made in RepoReady or through the journal's own
   submission system), "Check the revision" and Send are in the web app,
   and your answers go to the journal with the revision.
6. Submitting your paper happens in the web app: **"Prepare for
   submission"** gives a link to exactly that check for 12 months, its PDF,
   your answers and a sentence for your availability statement or cover
   letter, and you can mark the version "Submitted to" the journal. A
   journal that takes receipt codes can get the check itself: "Send to
   journal" makes a one-time code that carries the version and its check,
   never your answers; keep it out of files and commits. The shared report
   names no account; for a double-blind journal, anonymise your
   repositories yourself.

A check that cannot finish ends as "Check incomplete" and its credits come
back. It may rerun once by itself (if some of the authors' code could not
be read, only once that code is new). If it stops because of a temporary
problem on RepoReady's side, its credits come back and it keeps its
answers: Check again continues it. A check you cancel also gets its
credits back; the project keeps its last finished check.

## Tools

The 2.x server offers:

| Tool | What it does |
|---|---|
| `get_account` | Who is signed in, who pays (your organization, or nobody yet), the organization's daily cap, connected GitHub accounts, review scopes |
| `list_projects` / `get_project` | Your projects, found by name or repository (`owner/repo`, a GitHub URL or the git remote), with their latest run; `scope: 'shared'` lists projects shared with you through a link you saved |
| `identify_source` | What a DOI, paper link, arXiv id or GitHub link is, and your projects that contain it |
| `list_updates` | What changed since you last looked |
| `get_update` | What a new check would read differently (a newer paper version, new commits); free |
| `lookup_public_assessment` | Published assessments of a paper or repository (listed only while RepoReady's public registry is on) |
| `request_upload_url` | Upload a zip of local code, or a paper PDF / LaTeX zip |
| `create_project` | A project from code or a paper: what was found and a quote; never starts a check |
| `update_components`, `add_paper` | Correct what a check reads; add a paper to a code project |
| `estimate_run` | The credits per scope ("2 credits · billed to <payer>") and who pays, with the supplementary results on request (`check_supporting_results`); intent `fixes` prices "Check N fixes" (server 2.2.0); stores a quote |
| `start_run` | Starts a quoted check (costs credits); `kind: 'fixes'` for a fix check (server 2.2.0); may answer an approval link |
| `get_run`, `list_runs`, `get_run_status`, `cancel_run` | Follow, list or stop checks |
| `get_ladder` | The level per scope, the area results and what each level needs |
| `list_todos` | The to-dos: the action plan per finding, steps in order with alternatives and who can do each, and what you marked fixed (the web app's To-dos) |
| `list_issues`, `get_issue`, `get_figure` | What to fix, by file or by Impact, with citations and your marks and answers (`status: 'accepted_risk'` lists the findings you explained) |
| `answer_finding` | Your answer to a finding: Mark as fixed, Explain why (with a reason), or undo; never changes the level (server 2.2.0) |
| `report_wrong` | "This is wrong…": a free re-check of one finding with the places to look; previews first (server 2.2.0) |
| `request_institute_access` | "Ask my institute" when nobody pays for your checks; previews first, sends only with your consent (server 2.2.0) |
| `create_share_link`, `list_share_links`, `revoke_share_link` | "Can view" links (read-only, runs nothing), and withdrawing them |
| `get_badge` | The README badge per paper or repository |

`analyze_repo`, `get_report` and `get_findings` remain for older plugins for
one release; this plugin does not use them.

## Accounts and who pays

- **New to RepoReady?** Sign in once at [repoready.ai](https://repoready.ai)
  with your email (a magic-link code is sent to your inbox). If your
  organization uses RepoReady, use your institutional email: you join your
  organization and its plan pays for your checks, in credits.
- **Who pays.** Platform assessments are paid in credits by your institute (its
  organization's plan), a journal (its request; started in the web app) or
  the owner of a checker link. There are no own keys and no individual
  plan. Nobody pays for yours yet? Run the free self-check, or "Ask my
  institute" (from your agent or in the web app).
- **Existing account?** Nothing to prepare: the OAuth sign-in below uses it.

## Data handling and cost

Checks run on RepoReady's servers. For local code the workflow zips your
project, without `.git`, dependency folders, virtualenvs, caches and `.env`
files, and uploads it. Don't use it on code that must not leave your
machine, and extend the zip exclusions for anything else you don't want
uploaded. Every check is priced in credits before it starts and needs
your explicit yes; your organization may also set limits in credits. Text inside findings is
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
instructions (and the free self-check) into your agent's skills directory:

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
`claude plugin validate .claude-plugin/plugin.json`, test the self-check's
renderer with `python3 -m unittest discover -s tests`, and run
`bash scripts/check-public-text.sh` (the words the shipped files and the
self-check's output must never contain). Changes are listed in
[CHANGELOG.md](CHANGELOG.md).
