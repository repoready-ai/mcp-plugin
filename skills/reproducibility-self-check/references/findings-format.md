# The findings.json of a self-check

Format `repoready-self-check/1` (self-check skill v0.1). The JSON
Schema is `findings.schema.json` beside this file; `scripts/render_report.py`
checks the same rules and turns the file into the HTML and Markdown reports.

Write it to `repoready-self-check/<YYYY-MM-DD>-<slug>.findings.json`. Keep the
file: the next self-check compares with it ("Since the last self-check").

## Fields

| Field | Required | What to write |
|---|---|---|
| `format` | yes | `"repoready-self-check/1"` |
| `skill_version` | yes | `"0.1"` (the skill's version, v0.1 in SKILL.md) |
| `date` | yes | today, `YYYY-MM-DD` |
| `agent.name` | yes | the agent product: `"Claude Code"`, `"Codex"`, `"Cursor"`, … |
| `agent.model` | yes | the exact model id your system states, or `null` (the report then says "model not stated by the agent"); never a guess |
| `mode` | yes | `"paper_and_code"`, `"code_only"` (a method, tool or package: R1–R4) or `"analysis_code_only"` (scripts for one study, checked without its paper) |
| `project.name` | yes | the paper's short title or the repository name |
| `project.slug` | yes | lowercase letters, digits and hyphens; the same on every self-check of this project |
| `project.repositories[]` | yes | `url` (the remote's URL, or `null` when the repository has no remote: then `name`, the folder name), `ref` (the cited tag or branch, if any), `commit` (full SHA from `git rev-parse HEAD`), `uncommitted_changes` (true/false), `role` (e.g. "paper analysis", "method package") |
| `project.paper` | paper mode | `title`, `doi`, `read_from` (e.g. "Europe PMC full text", "PDF from the user") |
| `project.materials[]` | no | the archives, datasets and software the paper cites: `kind`, `name`, `identifier`, `note` (e.g. "cited, not verified") |
| `result.reuse` | code-only mode | `{"R1": {"status": "met", "note": "…"}, "R2": …, "R3": …, "R4": …}`; status `met`, `not_met` or `not_settled` |
| `result.summary` | yes | **one** sentence on top of the report: what is in good shape, then what the to-dos are about (no level). The sentence comparing with the last self-check is the renderer's |
| `results[]` | paper mode | every main-text figure and table that shows results (leave out schematics and tables of reagents or protocols): `label` ("Fig 2", "Table 1"), `title`, `checked` (true for the ones you checked), `A1`/`A2`/`A3` states, `code` (["path:line", …] where the values are computed), `note` (one short line); for one not checked, `reason` |
| `requirements[]` | yes | paper mode: one entry for each of A1–A3 and B1–B10 (B9 is `not_checked` unless you noticed a contradiction or made the comparison of SKILL.md Step 6); code-only modes: `[]`, with R1–R4 in `result.reuse`. Fields: `code`, `status` (`met`, `not_met`, `not_settled`, `not_applicable`, `not_checked`), `note` (one line) |
| `findings[]` | yes | see below; may be empty |
| `todos[]` | no | the plain-language to-dos over the findings; see below. Without it, every finding is its own to-do |
| `not_checked[]` | no | anything else you did not check, beyond the standard list the report always prints |

## A finding

| Field | What to write |
|---|---|
| `id` | short, stable: e.g. `b2-no-cited-version`, `a1-fig3-no-code`. Reuse the previous self-check's `id` when it is the same problem |
| `code` | the requirement code: `A1`–`A3`, `B1`–`B10`, `C1`–`C4`, `P1`, `P2`, `R1`–`R4`, `G1`–`G4`, `J` |
| `severity` | `critical` (A1–A3 open), `important` (B1–B10 open, a contradiction under B9, an open R1–R4) or `recommended` (everything else: C, G, J, P, differences that change no result). With code alone, only R1–R4 may be `important` |
| `title` | what is wrong and where, in one line (at most two names; else a count and the shared place) |
| `detail` | optional: one to three sentences |
| `evidence[]` | at least one: `where` (`path/to/file.py:42`, `README.md:10-14`, `analysis.ipynb cell 12`, "Methods, section Data analysis", a URL, "repository tree") and an optional short `quote` of what is there (one line; escape tabs and newlines as JSON requires). Never quote a secret |
| `results` | optional: the results it affects, e.g. `["Fig 2", "Table 1"]` |
| `todo` | the concrete next step |
| `who` | `agent_can_fix` (Your coding agent can fix this), `agent_needs_answer` (Your agent can help · needs your answer) or `authors_only` (Authors only); when a to-do needs more than one, the most demanding |
| `noticed_only` | optional: `true` for a paper–code contradiction you saw without searching for it |
| `at_submission` | optional: `true` for a B2 or P2 finding outside a final check (SKILL.md, Step 8, item 5). The report lists it under "When you submit", not as a to-do, and leaves it out of the counts and of "Since the last self-check" |

## The to-dos (what the reader sees first)

The report leads with to-dos a researcher understands without the guides;
the findings are the technical details under each one, folded away on
screen and unfolded when printed. Write findings as before (one per problem,
with their requirement code and evidence), then group them:

| Field | What to write |
|---|---|
| `title` | what to do, in plain words and without requirement codes: "Say which script makes each figure", "Pin the package versions you used", "Archive the submitted version and cite its DOI" |
| `why` | optional: one sentence on why it matters for a reader who wants to rerun the work |
| `findings` | the ids of the findings this one step fixes |

- Put findings together when one step fixes them all (a README section that
  answers B5, B6 and B7 at once; one environment file for B1 and C2). Keep
  apart what different people do or what has a different severity.
- Every finding is in exactly one to-do. The to-do's severity is its
  highest finding's, its "who" the most demanding one (Authors only before
  needs your answer before your coding agent can fix).

## Rules the renderer enforces

- No `result.level`, and no level (L0 to L4) in any text you write: a
  self-check gives none.
- A severity no higher than its requirement allows (above).
- A1–A3 not met or not settled needs a `critical` finding under that code.
- An `important` B9 finding (a contradiction) cannot stand beside B9
  recorded as met.
- An open R1–R4 needs an `important` finding with its to-do.
- Every finding has evidence and a to-do; ids are unique.
- With `todos`, every finding is in exactly one to-do and every id exists;
  a to-do holds either findings for when you submit or none of them.
- `at_submission` only on B2 and P2.
- `date` is a real ISO date; `skill_version` is a plain version number
  (the report always prints the renderer's own version);
  a commit is a hex SHA; the slug is lowercase letters, digits and hyphens.
- Every text the report prints is escaped for HTML and Markdown, and placed
  in one pass: markup, Markdown syntax and placeholders in your text stay
  plain text.
- No score, percentage, certification wording, README
  status image or image Markdown in any text you write (titles, details,
  to-dos, summaries, notes, project, agent, paper and material fields,
  result labels, `not_checked`); no account or pricing words. Evidence
  locations and quotes of the user's files are left as they are.

## Example

```json
{
  "format": "repoready-self-check/1",
  "skill_version": "0.1",
  "date": "2026-11-07",
  "agent": {"name": "Claude Code", "model": "<the model id your system states>"},
  "mode": "paper_and_code",
  "project": {
    "name": "Cell filtering study",
    "slug": "cell-filtering",
    "repositories": [{"url": "https://github.com/example/cell-filtering", "ref": "main",
                      "commit": "0123456789abcdef0123456789abcdef01234567", "uncommitted_changes": false,
                      "role": "paper analysis"}],
    "paper": {"title": "Cell filtering at scale", "doi": "10.1234/example", "read_from": "PDF from the user"},
    "materials": [{"kind": "dataset", "name": "Raw counts", "identifier": "10.5281/zenodo.0000000", "note": "cited, not verified"}]
  },
  "result": {
    "summary": "Code, inputs and software were found for every result checked; what is missing is a fixed code version and a map from figures to scripts."
  },
  "results": [
    {"label": "Fig 2", "title": "Filtering thresholds", "checked": true, "A1": "met", "A2": "met", "A3": "met",
     "code": ["analysis/fig2.py:31"]},
    {"label": "Fig 9", "title": "Sensitivity analysis", "checked": false, "reason": "not reached before the run stopped"}
  ],
  "requirements": [
    {"code": "A1", "status": "met", "note": "Every checked result has code that computes it."},
    {"code": "A2", "status": "met", "note": "Inputs in the repository or cited with a DOI."},
    {"code": "A3", "status": "met", "note": "All packages are on PyPI."},
    {"code": "B2", "status": "not_met", "note": "The paper links the repository without a version."}
  ],
  "findings": [
    {"id": "b2-no-cited-version", "code": "B2", "severity": "important",
     "title": "The paper cites the repository without a fixed version",
     "evidence": [{"where": "Paper, Code availability", "quote": "Code is available at github.com/example/cell-filtering"}],
     "results": ["Fig 2"],
     "todo": "Tag the version you submit, archive it with a DOI and cite that version DOI in the paper.",
     "who": "authors_only"}
  ]
}
```
