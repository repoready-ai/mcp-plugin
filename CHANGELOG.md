# Changelog

## 2.1.0 — the free self-check, credits, and your answers from your agent (next release)

For RepoReady's MCP server 2.2.0 (credits, no own keys, the author tools).
With an older server the agent says that the author tools are missing and
you use the web app for them; a self-check needs only the sign-in from the
server.

- **Free self-check.** Adds the free self-check skill v0.1, its first
  release: `reproducibility-self-check` (`/repoready:self-check` in Claude Code) checks
  your research code, or a paper with its code, in your own coding agent.
  Every self-check needs a free RepoReady account, which takes one
  sign-in; RepoReady receives the sign-in and one `get_account` call,
  nothing of the work. Your code, PDF, report and `findings.json` are
  never sent. Code alone gets the Software reuse result R1–R4. With a
  paper (PDF or DOI), whose public links are also sent, if it has them, to
  find its materials: an indicative level, self-assessed and at most L2,
  over the Materials and the workflow basics. Main-text figures and tables
  only, static reading, `file:line` evidence and a to-do per finding. With
  no paper given it looks for one, and before the audit it confirms the
  paper, code and data it will use. Paper and code are compared when a
  check would otherwise reach L2, and inputs resting on a deposit are
  looked up in its public file list. The report plainly lists what it does
  not check (Integrity below that point, deposits beyond their public file
  lists, supplementary results, a second model's verification, L3/L4). Its
  rubric is copied from RepoReady's public checklist, guides
  and levels page. The plugin brings both skills and the server in one step;
  for any other agent, `npx skills add repoready-ai/mcp-plugin --skill
  reproducibility-self-check` and `--skill repoready`, plus the agent's one
  line to add the server. If something is missing when a self-check starts,
  the agent says what and, on your yes, adds it.
- **The self-check report.** HTML (print it to PDF from your browser) and
  Markdown in `repoready-self-check/`, rendered by a standard-library
  Python script from a documented `findings.json`. Marked "Self-check ·
  user generated · not a RepoReady certification" in its header and
  footer, with a SELF-CHECK watermark and grey instead of the level
  colours; it names the agent, the model, the self-check's version (v0.1),
  the date and the commit, and shows "Since the last self-check: n fixed ·
  n still open · n new". Platform assessments come through institutes and
  journals.
- **The self-check, signed in.** A check with a paper finds the paper's
  materials from its public links (repositories, deposits with their file
  lists, supplements, archived links), sending only the paper's public link
  and the public repositories it names. If you say yes: the to-dos of a
  platform assessment you already hold, and "Ask my institute". Your code, paper
  file and report are never sent, and nothing paid starts without your yes.
- **No own keys.** Platform assessments are paid by your institute (its
  organization's plan), a journal or a checker link's owner; the own
  OpenRouter key and the individual plan are gone. With no payer a quote is
  refused `needs_payer` (was `needs_own_key`): the agent offers the free
  self-check and "Ask my institute". `get_account`'s `funding` reads
  organization or none (no `hasPersonalKey`, no `plan`).
- **Credits instead of dollars.** The agent tells you "2 credits · billed
  to <payer>" ("Large paper: 4 credits" when a paper counts double), never
  a dollar amount: L1 check 1 credit, L2 check 2, Continue to L2 1, Check
  again 1. `estimate_run` (with `billing: "credits"`), `get_run` and
  `list_runs` carry `credits` (and `creditsStatus`: held, used, returned)
  and no USD field; the agents' approval threshold and daily limit are in
  credits (the quote's `limits`). Supplementary results add no credits
  unless they make a paper large. A check that cannot finish, is
  cancelled, or stops because of a temporary problem on RepoReady's side
  gets its credits back. `confirm_own_payer` is set only after a journal's
  sponsorship refused a check (`sponsor_refused`) and you agreed that your
  institute pays instead.
- **Three answers per finding, from your agent.** Fixed (`answer_finding`
  `fixed`: "Marked fixed · not checked yet" until a check says "Fixed" or
  "Still open"), Wrong (`report_wrong`: "This is wrong…", a free re-check
  with the places to look, previewed before it is sent) and Won't change
  (`answer_finding` `explain` with a reason: restricted data declared in
  the paper, not applicable, done at publication, or your own words; shown
  as "Authors' response" to people you share with); `undo` takes an answer
  back. No answer moves the level. An explained finding leaves the to-dos
  and the open issues (`list_issues` with `status: 'accepted_risk'` lists
  them), and `get_issue` shows each answer (`answer`). Only the project
  owner answers; text in findings stays data.
- **"Check N fixes".** `estimate_run` intent `fixes` (with
  `target.issueIds` for some) and `start_run` with `kind: 'fixes'` check
  every finding you marked fixed in one check: 0 credits within 3 fix
  checks per version (a journal's allowance pays them in the web app).
  The to-dos and issues show your marks (`markedFixed`, `fixMarks`,
  `counts.markedFixed`, `fixMark`).
- **"Ask my institute".** `request_institute_access` asks your
  institution's RepoReady admins to let you join, or records your interest
  so you hear when it joins; it previews first and is sent only with your
  consent. A request reaches the admins only from your verified sign-in
  address on the organisation's own email domain.
- **For a journal's request** (made in RepoReady or through the journal's
  own submission system), your answers go to the journal with the
  revision you send; "Check the revision" and Send are in the web app.
- **Submitting.** "Prepare for submission" (a 12-month link to the check,
  its PDF, your answers and a suggested sentence), the "Submitted to"
  label and "Send to journal" with a one-time receipt code are in the web
  app. A receipt carries the version and its check, never your answers;
  the agent never writes a receipt code into files or commits. For a
  double-blind journal you anonymise your repositories yourself.
- **Who can do a to-do**, in new words: "Your coding agent can fix this",
  "Your agent can help · needs your answer" and "Authors only" (were "AI can
  fix this", "AI can help · needs your answer" and "Authors"). The
  self-check uses them; the check workflow shows them as the server sends
  them.
- **More of the server described:** projects shared with you through a
  saved link (`list_projects` with `scope: 'shared'`, read only) and a
  journal's review copy, on which agents start no checks
  (`journal_review_project`).

## 2.0.1 — requires the RepoReady server with `list_todos` (next release)

- **The to-dos.** The agent now shows the same to-do plan as the web app's
  To-dos view, read with the server's new `list_todos` tool: what to do to
  reach L1, to reach L2, then what is optional beside the level (including
  Other findings, which never change the level); each finding's steps in
  order, a step with alternatives as one step ("Either … or …"), steps
  already fixed ticked, and who can do each step: "AI can fix this", "AI
  can help · needs your answer" or "Authors". The check's summary comes
  first when it has one.
- **Only what to do.** Ask for "only what to do" (or only what changes the
  level) and the agent lists just the open steps.
- `/repoready:status` shows the current repository's to-dos in one line and
  offers the whole plan; `/repoready:analyze` ends with the to-dos instead
  of a fix list.
- With a server from before `list_todos`, the agent falls back to the issue
  list (`list_issues`) and says the to-do plan needs a newer server.
  `get_findings` and `get_report` stay unused.
- Unchanged: nothing paid starts without the expected cost ("about $X"),
  who pays and your explicit yes.

## 2.0.0 — 2026-10-26

For RepoReady's 2.x server (MCP server 2.0.0). Earlier plugin versions
describe the retired score-based server.

- **Levels instead of a score.** Each check gives one level: L0 Incomplete,
  L1 Available, L2 Rerunnable (L3 Re-executed and L4 Reproduced are not
  offered yet), with Integrity, Automation and Reuse as area results beside
  it, and Journal policy when a journal is known. The 0–100 score,
  categories and tiers are gone from the skill, the commands and the
  README.
- **Review scopes.** An "L1 check" (are the code, data and software behind
  each result shared?) awards at most L1; an "L2 check" (the full review
  without running the code: workflow, integrity, automation, reuse) awards
  at most L2. After an L1 check, "Continue to L2" checks the same inputs
  for less than a new check, and the issue list says which findings were
  not assessed in the L1 check.
- **The 2.x flow.** `list_projects` / `identify_source` → `create_project`
  or `estimate_run` → the user's explicit yes, with the expected cost and
  who pays → `start_run` (and the browser approval link when it answers
  `awaiting_approval`) → `get_run` → `get_ladder` → `list_issues` /
  `get_issue` → "I fixed this" or Check again through `estimate_run`.
  The skill no longer uses `analyze_repo`, `get_report` or `get_findings`,
  which the server keeps for older plugins for one release.
- **The expected cost only.** The agent tells the user "about $X"
  (`expectedUsd`), never the most a check may spend.
- **Supplementary results only on request.** By default a check does not
  check supplementary figures, tables and datasets as results; it still
  reads the supplementary files as materials of the main-text results.
  Each quote names what also checking them would add ("+ about $Y",
  `supportingExtraUsd`); on the user's request the agent prices the check
  again with `check_supporting_results: true`. Findings on supplementary
  results are Warnings, never blockers for a level.
- **No "Confirm this".** Every check confirms its uncertain findings
  itself (`get_run` shows `confirming`); what it could not decide is shown
  as Unresolved. The only follow-up on one finding is "I fixed this"
  (it checks the project again first, then that issue).
- **Issues by Impact.** Blocks L1, Blocks L2, Caps at L1 (a confirmed
  paper–code contradiction on a key result), Blocks L3, Blocks Automation,
  Warning, in that order; "what L2 needs" in plain words. Finding states:
  Missing, Warning, Unresolved, Available, Not applicable.
- **Who pays.** A journal's sponsorship, an organization or individual
  plan, or the user's own OpenRouter key; there are no free checks.
- **Incomplete, stopped and cancelled checks.** A check that cannot finish
  is "Check incomplete, not charged" and may rerun once by itself (if some
  of the authors' code could not be read, only once that code is new); on
  the user's own key, the provider's tokens for it are not refunded. A check stopped because the
  payer's key ran out of credit is charged what it spent and keeps its
  answers: Check again on the same payer continues it. A cancelled check is
  charged what it spent until it stopped, and the project keeps its last
  finished check.
- **Papers and supplements.** Projects from a DOI, paper link or uploaded
  PDF / LaTeX zip, with separately uploaded supplementary files; the
  intake's coverage is reported before saying a paper was read in full.
  Materials can hold code, data or both and have several roles.
- **More of the server described:** `get_update` (what a new check would
  read), `lookup_public_assessment` (only while the public registry is
  on), `targetJournal` and the Journal policy area, `checkVersion`
  choices, shared root causes, the agents' policy refusals, share links
  sent by email only on the user's request, badges issued in the web app.
- **Safety kept and tightened.** Find existing work first; upload
  exclusions (now also nested dependency folders, virtualenvs and notebook
  checkpoints); never open or approve an approval link for the user; text
  inside findings is data, not instructions.
- `/repoready:status` shows the current repository's level line and what
  is waiting for the user (`list_updates`).
- Manifests: version 2.0.0, new descriptions, a marketplace description.

## 1.1.0 (not published; included in 2.0.0)

- Find existing work first: `get_account`, `list_projects` by git remote,
  `get_project`, `list_runs`.
- `/repoready:status`.

## 1.0.1 — 2026-09-14

- Current claude.ai paths (Customize), Claude Science instructions.

## 1.0.0 — 2026-09-14

- First release: MCP connection, workflow skill, `/repoready:analyze`; MIT
  license; hardened data handling after the marketplace review.
