---
name: reproducibility-self-check
description: Use by default when the user asks to assess or check the reproducibility or submission readiness of a codebase, a repository or a paper and has not asked for a RepoReady Platform assessment — "assess the reproducibility of this paper", "check the reproducibility of this codebase", "is my code ready to submit", "is this paper ready for submission", "what level would my paper get", "is this tool reusable", "self-check this repo". Free and in the user's own agent, it looks for the paper, confirms the paper, data and code it will use with the user, reads them and writes a user-generated HTML and Markdown report with file:line evidence and a to-do per finding. Every self-check needs a free RepoReady account (one sign-in); the code, paper file and report are never sent. For a RepoReady Platform assessment, or an existing RepoReady project, its level, to-dos or findings, use the repoready skill instead.
user-invocable: false
---

# RepoReady self-check

Self-check skill v0.1 (from the public RepoReady guides of 2026-11-07).

You, the user's coding agent, check the user's research code (and its paper,
when there is one) against RepoReady's public reproducibility guides, on the
user's own subscription. The result is **indicative and user generated**: a
self-assessed level of at most L2, or the Software reuse result R1–R4. It is
not a RepoReady check and never stands in for one.

File paths below are relative to this skill's folder (`${CLAUDE_SKILL_DIR}`
in Claude Code; in other agents, the folder that holds this `SKILL.md`).

## Ground rules

- **Private, with a free account.** Every self-check needs a free RepoReady
  account (Step 1, item 3). Work in the agent. Never upload or send the
  user's code, PDF, report or `findings.json` to RepoReady or anywhere else,
  and add no usage ping, counter or other call of your own. What RepoReady
  receives: for code alone, the sign-in and the one `get_account` call,
  nothing of the work; with a paper, the same plus, when the paper has them,
  its public link and the public repositories it names, for materials
  discovery (`signed-in.md`). With a private PDF and no public link, nothing
  is sent beyond that one call. Make no RepoReady call this skill and
  `signed-in.md` do not name; the optional extras of Step 1, item 7, only
  after the user says yes to them.

  On the user's yes, adding RepoReady's own server and skill (Step 1, items
  3 and 6) is the one install allowed. The only other network reads allowed
  are public pages the check needs:
  the paper (doi.org, the publisher, Europe PMC, bioRxiv/arXiv), public
  repositories (GitHub and the like), package indexes, archive landing
  pages and their public file lists and, for a public repository when no
  paper was given, a web search for its name and URL (Step 1, item 4).
- **Static.** Read files; do not run the project's code, install its
  dependencies or execute its notebooks unless the user says yes to that
  specific step. `git` metadata commands (`log`, `tag`, `rev-parse`,
  `ls-remote`, a read-only `clone`) and listing files are fine.
- **Main-text results.** Every main-text figure and table that shows
  results, however many there are. Supplementary, Extended View, Appendix and source-data figures are not
  checked as results (their files are still read as materials).
- **Evidence.** Every finding cites at least one place you actually read: a
  `file:line` (with a short quote), a paper section, figure legend or page,
  a public URL, or a plain description such as "repository tree" or "GitHub
  releases page". For something missing, cite where you looked. Never
  invent a location. Never quote a secret (an API key, a password, a
  token): name its `file:line` only.
- **Say what is running.** Start your first reply with one line: "Using
  RepoReady: free self-check", so the user knows which check this is.
- **Honest words.** Never write a score, a percentage or a level above L2;
  never call the result official, certified or verified by RepoReady; never
  produce a README badge, badge Markdown or a status image. When in doubt,
  choose the lower level and say what to verify.

## The words to use

| Level | Name |
|---|---|
| L0 | Incomplete |
| L1 | Available |
| L2 | Rerunnable |

- Level line: `Self-assessed · L1 · Available · indicative, at most L2`.
  L3 Re-executed and L4 Reproduced need a run of the code; a self-check
  never awards them.
- Reuse line (code only): `Self-assessed · Reusable · Software reuse, no
  level for code alone` when R1–R4 are all met, else `Self-assessed ·
  Reuse: n of 4 · …`. Analysis code without its paper: `No level · add the
  paper`. The renderer writes these lines; quote them as it prints them. In
  your own text, never claim a level above L2.
- Impact of a finding: **Blocks L1**, **Blocks L2**, **Caps at L1**,
  **Blocks Automation**, **Reuse** (an open R1–R4), **Warning** (blocks no
  level).
- Who can act on a to-do: **Your coding agent can fix this** (an edit inside
  the repository with what is already there), **Your agent can help · needs
  your answer** (the agent can draft it but needs a fact only the authors
  know: a version used, a data source, a parameter, a license choice),
  **Authors only** (only the authors have it or can do it: share code or
  data they hold, deposit data, release weights, tag and archive a version,
  change the paper).
- Requirement states: Met, Not met, Not settled, Not applicable, Not checked.
- Requirement codes and names come from the public guides (`A1 · Code for
  each result is available`, …); use them exactly as
  `references/guide-*.md` print them.
- In your own words (titles, details, to-dos, summaries) the renderer
  refuses the usual word for a README status image (say "status image"),
  image Markdown, scores and certification wording. Quotes of the user's
  files are left as they are.

## References (read before judging)

- `references/levels.md`: the levels, how a level is awarded, what a finding
  blocks, access rules.
- `references/checklist.md`: the public pre-submission checklist.
- `references/guide-materials.md` (A1–A3), `guide-workflow.md` (B1–B8, B10,
  G1, G4), `guide-integrity.md` (B9, G3), `guide-automation.md` (C1–C4, G2),
  `guide-access-and-preservation.md` (P1, P2, J), `guide-software-reuse.md`
  (R1–R4): for each requirement, what counts, what it flags and how to fix.
- `references/findings-format.md`: the `findings.json` you write.

## Step 1 · Inputs and mode

1. **Repository.** The current directory when it is a git repository, or a
   repository the user or the paper names. Name it now and read it after
   item 3. A named repository is cloned read-only, once confirmed (item 6), into a temporary folder
   outside the user's repository, at the version the paper cites when it
   cites one (`ref` is that tag or branch, `null` for a bare commit). Record
   the commit (`git rev-parse HEAD`) and whether the working tree has
   uncommitted changes. Keep tags and history (no `--depth`): B2 and R4
   need them; for a large repository use `git clone --filter=blob:none`
   and a sparse checkout. Prefer `git ls-remote --tags` and the public
   releases page to the GitHub API, which rate-limits calls without a
   token. Code in an archive (Zenodo, figshare): record its version DOI
   instead of a commit, read its file list, and extract only the code and
   documentation when the archive also holds large data; ask before
   downloading anything large.
2. **Paper.** A PDF the user gives, or a DOI or link. When none is given
   and the user did not say "code only", item 4 looks for one. Do not open,
   fetch or extract the paper yet: item 3 comes first.
3. **Sign-in, before anything is read.** Every self-check needs a free
   RepoReady account, code alone included. Every request to RepoReady's
   server needs a sign-in, so the user is signed in when RepoReady's tools
   (`get_account`, `identify_source`, …) are in your tool list, names you
   can only load on demand included. Look at the list; do not call a tool
   to find out.
   - **Listed:** read `signed-in.md`, call `get_account` once (its section
     1), and go on with item 4.
   - **Not listed**, only a sign-in placeholder for the server (a tool such
     as `authenticate`), or `get_account` answered unauthorized: stop. Do
     not clone or read the repository, do not open, fetch or extract the
     paper, and never produce a level or a Reuse result. Tell the user, in
     one message and in these words:

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
4. **Reading the paper** (after item 3). When the user gave no paper and
   did not say "code only", look for one first: the README and docs,
   `CITATION.cff`, the repository's description and any citation or
   publication link. For a public repository, also search the public web
   for its name and URL (Europe PMC, bioRxiv/arXiv, a general search). A
   repository with no remote, or one that cannot be opened without signing
   in, is private: never put its name or anything from its files into a
   search.
   - One paper found, or a clear best match: read its Code and Data
     availability statements and put it in the confirmation of item 6.
   - Several possible: list them and ask which, then go on as for one.
   - None found: say that no paper was found and where you looked, and ask
     whether the user has one (a PDF, DOI or link) or wants the check to
     run on the codebase only. Wait for the answer. Send this and the
     confirmation of item 6 as one message.

   From a DOI, read the open
   full text (publisher page, Europe PMC, the preprint). For a PDF, use
   your file reader or any local text extractor (`pdftotext`, or Python
   `pypdf`, `pypdfium2` or `pdfminer.six`); check equations against a
   rendered page when extraction garbles them. If you cannot read the
   paper's text, ask the user for it.
5. **Mode**, from the inputs and the answer to item 4:
   - **Paper + code** → an indicative level (Steps 2–6).
   - **Code only, a method, tool or package** meant for others to install
     and use on their own data (a library, a command-line tool, a training
     framework, with usage docs; it may lack a packaging file) → the
     Software reuse result R1–R4 (Step 7). When unsure: a README that tells
     others how to run it on their own inputs (options, a usage section)
     makes it a method; a README that only reproduces one paper's figures
     makes it analysis code.
   - **Code only, analysis code** (scripts or notebooks made for one study's
     results) → `No level · add the paper`: report the Workflow and
     beside-the-level findings of Steps 4–5 as Warnings.
   A repository that is both the paper's analysis and a method package gets
   the level, and its Reuse result beside it when the user asks for it.
6. **Confirm what the audit will use.** Read only what this needs (the
   README and the paper's Code and Data availability statements). Then,
   before the audit, show the user in one short message, and ask them to
   confirm or correct it:
   - **Paper:** its title and DOI or file, and where it came from (given by
     the user, or where you found it).
   - **Codebase:** each repository with its version (tag or commit), and
     whether that is the version the paper cites.
   - **Data:** the deposits, accessions and files the paper's Data
     availability and the README name, or "none named".
   - The mode, that the reading is static, and what leaves their machine:
     to RepoReady the sign-in and the one account call and, with a paper
     that has them, its public link and the public repositories it names.
     Their code, PDF, report and `findings.json` are never sent.
   - **Only when the goal is a final check before submission** (the user
     says so: "final check", "before I submit", "ready to submit") **and
     `funding.default` in the `get_account` answer is `organization`:** one
     more line, saying that their organization pays for RepoReady Platform
     assessments, which compare paper and code for every key result and
     give the level that counts, and asking whether they want that for
     this final check instead; if the `repoready` skill is not among your
     skills, say that a yes also adds it. Never offer it for a check of work in
     progress or when the goal is unclear: the self-check is the one to
     repeat while working, a platform assessment is for the finished
     version. On a yes: if the `repoready` skill is not among your skills,
     run `npx skills add repoready-ai/mcp-plugin --skill repoready` and read
     its `SKILL.md` where the installer put it; then follow the `repoready`
     skill from its price step. Otherwise go on with the self-check.

   For code only, the codebase, the mode and what leaves their machine are
   enough. Wait for the answer; on a correction, redo items 4 and 5 with
   it. Then work. Materials found later (Step 3, discovery) are used and
   named in the report without asking again, unless they change which
   paper or code is audited.
7. **Extras (optional).** The to-dos of a platform assessment the user
   holds and "Ask my institute" (`signed-in.md`, sections 3 and 4). Offer
   them in Step 9, in one or two lines on what they add; never start them
   without the user's explicit yes. On a yes, follow those sections beside
   the self-check. The self-check is complete without them.

## What the account is for

Every self-check needs a free RepoReady account (Step 1, item 3). What
RepoReady receives: for code alone, the sign-in and the one `get_account`
call, nothing of the work; with a paper, the same plus, when the paper has
them, its public link and the public repositories it names, for materials
discovery. RepoReady's free discovery lists the paper's materials
(repositories, deposits with their file lists, supplementary files,
archived links) to settle A2 (`signed-in.md`, section 2). After the user
says yes to them, on either path, the self-check can also work through the
to-dos of a platform assessment the user already holds,
answering each finding (fixed, wrong, or won't change) and starting "Check
N fixes" only after the user agreed to its price and who pays; and, when
nobody pays for the user's platform assessments, "Ask my institute". The user's
code, paper file, report and `findings.json` are never sent, and the report
never shows an account.

## Step 2 · Pick the results (paper + code)

- List the paper's main-text figures and tables. A **result** is one figure
  (all its panels) or one table.
- Skip what computes nothing: schematics, workflow diagrams, photos and
  micrographs shown as images, tables of reagents, parameters or protocols.
  Leave them out of `results[]` entirely. A panel that plots measured or
  computed values is a result panel; so is an image panel with a
  quantification.
- Take every result, in paper order unless the user names the ones that
  matter most. If you have to stop before the end (context or time), list
  every remaining main-text result as not checked, with the reason: the
  level speaks only for the results checked; say so.

## Step 3 · Materials per result (A1–A3): what L1 needs

Read the paper's Code availability, Data availability and Methods, the
README(s), and the repository tree. List the materials the paper and the
code name: repositories (with any cited version), archives, datasets
(accession, DOI or URL), software (packages, tools, models, commercial
programs). If the paper names further public repositories, read them too.

For each result, with `references/guide-materials.md`:

- **A1, code.** Find the code that **computes** the values shown in every
  data panel: search the README and docs for the figure or table name, file
  names, output names, the quantities and tests the legend names. Code on
  any public branch counts (if it is not in the cited version, that is a B2
  finding); code deleted from every branch and left only in the history
  does not (name the commit in the to-do). Met only when public code
  computes the values of every data panel; cite the line where each value
  is computed. Code that only draws values computed elsewhere, computes
  some of the values or a different quantity, or a value from an
  interactive session, is not met; so is a named tool or test without the
  settings needed to redo it. A tool run with its settings stated counts.
  Missing cosmetic plotting code alone is not a gap. When nothing computes
  a result, say where you searched.
  - When shared code computes the shown values from a shared or deposited
    table, A1 is met; how that table was made is B4 (Step 4), not A1.
  - A panel of measured data (an experiment, not a computation) needs its
    data shared (A2) and its statistical test named with the settings
    needed to redo it (the test, sidedness, pairing, correction, n); then
    A1 is met without code.
- **A2, inputs.** Every file that code reads for the result is in the
  repository, produced by shared code, or deposited or cited with an
  identifier or a named source and its access route. Registration,
  controlled access, purchase, reviewer-only data and dated embargoes count,
  with a note. A file shared nowhere, or only "on request", is not met.
  Without code for a result, judge its inputs from what the paper says it
  used.
  - **Deposits.** For each input of a checked result that rests on a
    deposit, read the deposit's public file list (its landing page or
    public record) and look for the file the code reads, by name or by the
    pattern the code builds. Do not download data files.
    - Found: A2 is met for that input; cite the list's URL.
    - Not found, after allowing for a renamed file, another folder or a
      format the code converts: A2 is **Not settled** for that result,
      never Not met. Name the file and the list you read. A list cannot
      show everything a deposit holds.
    - No list you can read (controlled access, reviewer-only, an embargo,
      a page that refuses automated reading, a list too long to read, or a
      file inside an archive the list does not open): the cited deposit
      counts, with a note, and add it to `not_checked`.
  - A public reference resource the code downloads or reads (a genome, an
    ontology, an orthology or gene-set table, a database release) is
    obtainable when you can name where it is served today, even if the
    code's own link has died: A2 is met, and the dead or unversioned link
    is a B3 finding.
- **A3, software.** Every package, tool, model or service the code needs
  can be obtained (package index, model hub, public repository, archive;
  commercial software with vendor and version). An in-house tool, private
  module or unreleased weights are not met.

Any A requirement not met or not settled for a checked result is a **Blocks
L1** finding.
Before you mark one Not settled, look where a third party would: the
paper's references and data statement, the tool's documentation, the
provider's current site, a web archive. Only what still cannot be decided
after that (a private link, an unreadable file, a file missing from a
deposit's list) is Not settled; say what would settle it.

## Step 4 · Workflow basics (B1–B8, B10): what L2 needs

Check these for the code of the checked results, with
`references/guide-workflow.md`, even when L1 is not met (they stay useful
to-dos). Each not met is a **Blocks L2** finding.

- **B1** A dependency file lists every package the result code imports,
  each with a version or range. Compare the imports with the file.
- **B2** The paper cites an immutable version (a tag, release, commit or
  version DOI) that holds the code of every checked result; forks, other
  repositories and models are pinned. Check that a cited tag exists
  (`git tag`, `git ls-remote`) and holds the result code. A bare repository
  URL, a branch or a concept DOI is not met.
- **B3** Each dataset has an accession, DOI, versioned record or release
  URL; no personal or changeable links (cloud drives, unpinned models);
  controlled data say how to apply.
- **B4** Every input that no shared code produces comes with its preparation
  steps: tool, version, parameters, manual curation.
- **B5** A table or entry maps each checked figure and table to the script,
  notebook section or command that produces it.
- **B6** The README, paper or docs cover setup, where inputs go or how they
  are fetched, the run order and every manual step.
- **B7** Every command, file, option, variable, folder and install name the
  docs give matches the repository exactly: check each one. Also flag
  placeholders (`<your-path>`), result notebooks saved with errors, and
  result code that waits for a person (`breakpoint()`, `input()`, `View()`).
- **B8** Result code has no paths from one computer (`/Users/…`, `/home/…`,
  `C:\…`) and no unexplained check for one host or system.
- **B10** Each key result that depends on random draws is seeded (library
  defaults included) or the paper reports its spread across runs.

**B9 · Integrity (paper vs code) is compared only at the edge of L2** (Step
6); it cannot change L0 or L1, so otherwise record B9 as Not checked and do
not search for contradictions. If you happen to see a clear one that changes
a reported key result (a different method, parameter, test or number),
record it as a **Caps at L1** finding with `noticed_only` and set B9 to Not
met; a difference that changes no reported result is a Warning under B9.

## Step 5 · Beside the level (quick)

From the files you already read, add the few findings that never change
the level: C1 one command, C2 a lock file, C3 scripted input retrieval, C4
seeds everywhere (**Blocks Automation**); J a license and a citation file,
G1 committed junk or credentials, G2 notebooks run top to bottom, G4
hardware and run time stated (**Warning**). Do not repeat a B finding as a
C finding. P1 and P2 (access conditions, a lasting archive) may be used
for access and archive notes. Use the guides for the words and the fixes.
These codes appear only as findings: `requirements[]` holds A1–A3 and
B1–B10.

## Step 6 · The indicative level (paper + code)

- **L0 · Incomplete** when an A requirement is not met, or not settled, for
  a checked result. (With only Not settled items, `result.level` is still
  `L0` and the report reads "not yet at L1 · n to verify".)
- **L1 · Available** when A1–A3 are met for every checked result.
- **L2 · Rerunnable** only when L1 holds, **every** B requirement of Step 4
  is met for every checked result, with evidence for each, B9 is Met from
  the comparison below, and no Caps at L1 finding exists. Anything not met
  or not settled keeps it at L1.
- Strengths never offset a gap. Never above L2. The renderer writes the
  level line as in "The words to use" and adds "For n of m main-text
  results checked".

**The Integrity comparison.** Only when everything else for L2 holds (A1–A3
and every B of Step 4 met for every checked result, no Caps at L1 finding),
compare the paper and the code before writing L2, with
`references/guide-integrity.md`. For every checked result, read its Methods
passage, its legend and the values it reports beside the code that computes
them: method, parameters, statistics (test, sidedness, correction, interval,
n), data processing and exclusions, splits, reported values and quantities.

- A contradiction needs both sides: a quote of the paper and the `file:line`
  of the code. When it changes a reported result, it is a **Caps at L1**
  finding (without `noticed_only`), B9 is Not met and the level is L1.
- A difference that changes no reported result is a Warning under B9.
- A value that exists only once the code runs, and that no saved output or
  deposit shows, cannot be compared: it is no contradiction; add it to
  `not_checked`.
- Every checked result compared and no contradiction: B9 is Met, with the
  note "Compared once by one agent".
- A checked result you could not compare at all: B9 is Not settled and the
  level is L1; say what would settle it.

## Step 7 · Software reuse R1–R4 (code only)

With `references/guide-software-reuse.md`. Each requirement is Met or Not
met (Not settled counts as not met and says what to verify); an open one is
a **Reuse** finding with its to-do. Steps 2–6 do not apply: write
`results: []` and `requirements: []`, and put R1–R4 in `result.reuse`.

- **R1 Installation**: a packaging file declares the package and its
  dependencies (`pyproject.toml`, `setup.py`/`setup.cfg`, an R
  `DESCRIPTION`, a conda recipe, `Project.toml`, `package.json`,
  `Cargo.toml`, …) **and** the README says how to install it.
- **R2 Documented interface and examples**: met unless one of the guide's
  core flags holds: the README and docs show no usage example; a library's
  public functions (what others import) have no reference documentation
  (most lack docstrings and no API docs exist); scripts run from the command
  line read their arguments without a parser that prints help. For a tool
  used only through its scripts, the interface is the command line: an
  argument parser with help and the commands the README documents; the
  docstrings of its internal functions do not decide R2. An example that
  would fail, an undocumented configuration key or a missing example file
  is a Warning under R2 (or B7), not a reason to open R2.
- **R3 Automated tests**: tests of the package exist **and** continuous
  integration runs them on changes.
- **R4 Releases and license**: a numbered version others can get, on a
  package index (PyPI, CRAN, Bioconductor, conda-forge, npm, …) or archived
  with a DOI or in Software Heritage, **and** an open license for the code.
  When you can read public pages, confirm the index entry or the archive
  (an index's JSON API, such as `https://pypi.org/pypi/<name>/json`, is
  fine); an index name that belongs to another project does not count.
  Otherwise rely on a documented install from the index and say "not
  confirmed online".

The guide flags more than these core items (fixed parameters, uninformative
errors, a missing changelog or citation file, …): report them as Warnings
under their R code; they do not open the requirement. Other problems you
notice (documented names that do not match the repository, unseeded
training, committed junk) are findings with impact `warning` under B7, C4,
G1 and the like; they never change the Reuse result. The result line is
`Reusable` (4 of 4) or `Reuse: n of 4`.

## Step 8 · Write findings.json and the report

1. Folder: `repoready-self-check/` in the current directory (the
   repository root when the user works inside the repository). The report
   files are the user's; do not commit them or edit `.gitignore` unless they
   ask.
2. Name: `<YYYY-MM-DD>-<slug>.findings.json`, the slug from the repository
   (or paper) name in lowercase letters, digits and hyphens.
3. **Since the last self-check.** If the folder holds an earlier
   `*-<slug>.findings.json`, read the newest one first. Give a finding that
   is still there its previous `id`; give a new problem a new `id`. Leave
   fixed problems out. The renderer counts fixed, still open and new.
4. **Agent and model.** `agent.name` is the product you run in (Claude
   Code, Codex, Cursor, …). `agent.model` is the exact model id your system
   tells you; if it does not tell you, write `null` and the report says
   "model not stated by the agent". Never guess a model.
5. Write the file as `references/findings-format.md` specifies (the schema
   is `references/findings.schema.json`), then render it:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/render_report.py" repoready-self-check/<date>-<slug>.findings.json
   ```

   It writes `<date>-<slug>.html` and `<date>-<slug>.md` beside the JSON,
   and refuses a file that breaks the rules above (fix what it names and run
   it again). Without Python, fill `assets/report-template.html` yourself as
   its comments describe, and write the Markdown in the same order.

## Step 9 · Tell the user

In a short message: the level line (or the Reuse line) exactly as the
report has it, the three to five to-dos that matter most with who can do
them, the report paths, "open the HTML in a browser and print it to save a
PDF", and what was not checked (Integrity, deposit and archive
verification beyond public file lists, supplementary results, a second
model's verification, L3/L4; Integrity counts as not checked unless the
check reached the comparison in Step 6).
Platform assessments, whose levels and share links count, come through
institutes and journals: https://repoready.ai/self-check?ref=report.
Offer to fix the "Your coding agent can fix this" items, as ordinary edits
after the user's yes. Say what discovery added, if it ran, and offer the
extras of Step 1, item 7: the to-dos of a platform assessment the user
holds and, when nobody pays for their platform assessments, "Ask my
institute" (`signed-in.md`, sections 3 and 4).
