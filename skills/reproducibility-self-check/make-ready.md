# Make it submission ready

Read this file when the user asks you to **make** their code or paper ready,
not only to check it: "make this codebase submission ready", "prepare my
code for the paper", "clean this repository up for publication", "make this
reproducible", "fix what the self-check found". A request to check or assess ("is
my code ready to submit?") is the self-check alone (`SKILL.md`).

The flow: set up, map the code to the paper's results, assemble a clean
submission repository first when the code is a mess, check, fix, check
again, and freeze the submitted version last. Every check is the ordinary
self-check of `SKILL.md`, Steps 2–8, with its report.

## Ground rules (beside those of `SKILL.md`)

- **The sign-in, the privacy promise, the evidence and the honest words of
  `SKILL.md` all hold.** Running the project's code still needs the user's
  yes to that specific step.
- **Edit only a working copy the user agreed to** (Step M1): a new branch
  in their repository, or a new folder for an assembled repository. Never
  edit their current branch without a yes. Never commit, push, tag, create
  a release, archive or publish without a yes to that step. Never delete
  the original code: it stays in the history or in its own folder.
- **Never invent a fact.** The versions used, data sources and accessions,
  parameters, seeds, the license, authors and DOIs come from the files, the
  paper or the user. When they cannot be read from evidence, ask (Step M4).
  A placeholder such as `<your-path>` is not a fix.
- **Do not change what the code computes.** Moving and renaming files,
  relative paths, a configuration for where data lives, documentation, a
  run script that calls the existing code, a dependency file with the
  versions that were used: fine. A changed parameter, filter, test, seed or
  package version that could change a reported value needs the user's
  answer of what the paper used, and you say that the result should be
  rerun to confirm it.
- **No fix only for the check.** Never write a README line the code does not
  bear out, a test that tests nothing, a seed in a comment only, or a file
  that only names a requirement. A to-do is fixed when a reader could now
  rerun the work, not when a check would pass.
- **The paper.** Edit the manuscript only when the user gives its source
  (LaTeX, Overleaf, Word) and says yes. Otherwise draft the text (Code and
  Data availability statements, the results-to-code table) in
  `repoready-self-check/<date>-<slug>.paper-text.md` for the authors.

## Step M1 · Set up

Follow `SKILL.md`, Step 1, items 1–6, as written. The confirmation of item 6
adds, in the same message:

- **The goal:** a submission-ready repository (and paper text), checked,
  fixed and checked again.
- **Where changes go:** a new branch (suggest `submission-ready`) or, when
  Step M2 finds the code needs assembling, a new folder beside it.
- **What may be edited:** code and documentation; the paper source only if
  given.
- **Whether you may run code**, and which: none by default; a yes lets you
  run one result's code to confirm an assembled repository still runs.
- **Supplementary results:** whether their code belongs in the submission
  (journals usually expect it). The self-check still checks main-text
  results only.

## Step M2 · Map the results and decide the shape

Do the reading the check needs anyway (`SKILL.md`, Steps 2 and 3): for every
result, the code that computes it, the inputs it reads and how it is run.
Then decide:

- **Tidy:** each result has one clear producer, and most of the code serves
  the results or is a documented tool. Go to Step M3.
- **Needs assembling:** several near-identical copies or versions of a
  script (`fig2_v3_final.py`, `old/`, `copy of …`), more than one candidate
  producer for a result, much of the code used by no result, notebooks
  whose saved outputs disagree, data paths scattered across files, no way
  to tell where to start. Go to Step M2a first.

Tell the user which shape you see, in two or three lines with examples from
the repository, and that they can choose the other. Checking a messy
repository first would bury the to-dos that matter under findings about
code that will not be submitted.

### Step M2a · Assemble the submission repository

1. **Choose each result's code by evidence.** The candidate whose
   parameters, tests and processing match the paper's Methods and legend;
   whose output names the figure uses; whose saved outputs show the
   paper's values; the README's or the authors' notes; the history around
   the submission date. Never choose by file name or date alone. When two
   candidates stay possible, show the user the difference (a few lines of
   each, with `file:line`) and ask.
2. **Build a clean tree** in the agreed folder or branch: the chosen
   producers and everything they need (imported modules, sourced files,
   called scripts, the configuration they read), the README, the
   dependency files, the license and citation files. Keep each file's
   content; the only changes are moves, renames, relative paths and one
   configuration for data locations.
3. **Record the assembly** in
   `repoready-self-check/<date>-<slug>.assembly.md`: for every file in the
   new tree, where it came from (path and commit); every file left out,
   with the reason (used by no result, a superseded copy, a scratch
   notebook); every choice you asked about and the answer. The authors use
   it to add back what they want and to answer reviewers.
4. **Confirm it still runs**, only with the yes of Step M1: run the cheapest
   result's code in the new tree. Without a yes, say that the assembly was
   not run and add it to `not_checked`.
5. When the assembled tree becomes its own repository, the paper must cite
   it: that is an Authors only to-do (the paper's Code availability).

Then go to Step M3 on the assembled tree.

## Step M3 · The first check

Run `SKILL.md`, Steps 2–8, on the working copy (the assembled tree, if
Step M2a ran). This report is the starting point. Write `todos` in
`findings.json` (`references/findings-format.md`): plain steps, each over
the findings it fixes. Show the user the to-dos grouped by who can act.

## Step M4 · Fix

Work through the open to-dos, smallest change first:

- **Your coding agent can fix this:** make the change, then reread the
  place the finding cites to see that it is fixed.
- **Your agent can help · needs your answer:** ask every question in one
  message, numbered, each with what it unblocks and, where the files
  suggest an answer, that suggestion marked as a guess and its evidence
  ("`requirements.txt` was last changed in March 2024: was numpy 1.26 the
  version used?"). Apply the answers. A question left unanswered keeps its
  to-do open.
- **Authors only:** prepare what can be prepared and do not do the rest:
  draft the availability statements, list the files a deposit must hold,
  write the release description, give the commands to tag and archive.
  These become the authors' checklist.
- **Leave the freeze for last** (Step M6): tagging, archiving and citing the
  version DOI, and anything that names the final version, change with every
  commit. The checks before the freeze list them under "When you submit";
  the last check, on the tagged version, is a final check and counts them
  as to-dos.

## Step M5 · Check again

Run `SKILL.md`, Steps 2–8, again on the changed working copy, from a fresh
reading. When you can start a subagent with a clean context, give it the
check: the inputs and this skill's `SKILL.md`, not your notes about the
fixes, so it reads what is there rather than what you meant to do.
Otherwise reread the files instead of relying on what you remember editing.
The report shows "Since the last self-check: n fixed · n still open · n
new".

Repeat Steps M4 and M5 while the new check finds something your coding
agent can fix, at most twice more. Then stop, even if to-dos remain: say
which and why.

## Step M6 · Freeze the submitted version

When nothing your coding agent can fix is left, guide the authors, with a
yes for each step you take for them:

1. Commit the working copy (a message that says what was prepared).
2. Tag the version to submit; push it and create the release (the user,
   or you on their yes).
3. Archive that release with a version DOI (for GitHub, the Zenodo
   integration; or Software Heritage) and put the DOI in the paper's Code
   availability statement.
4. Run a last self-check on the tagged version: that report goes with the
   submission.
5. When the user's organization pays for RepoReady Platform assessments,
   offer one for this final version (`SKILL.md`, Step 1, item 6, the final
   check rule).

## Step M7 · Tell the user

In one short message: the to-dos by severity of the first and of the last check (as the renderer prints them);
what was changed and where (the branch or folder, the files); what the
assembly left out (with the path of the assembly note); the questions still
open; the authors' checklist; the report paths and the paper text file.
Say plainly what was not committed, pushed or run.
