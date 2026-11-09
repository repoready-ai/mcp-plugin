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
| `mode` | yes | `"paper_and_code"`, `"code_only"` (a method, tool or package: R1–R4) or `"analysis_code_only"` (no level, add the paper) |
| `project.name` | yes | the paper's short title or the repository name |
| `project.slug` | yes | lowercase letters, digits and hyphens; the same on every self-check of this project |
| `project.repositories[]` | yes | `url`, `ref` (the cited tag or branch, if any), `commit` (full SHA from `git rev-parse HEAD`), `uncommitted_changes` (true/false), `role` (e.g. "paper analysis", "method package") |
| `project.paper` | paper mode | `title`, `doi`, `read_from` (e.g. "Europe PMC full text", "PDF from the user") |
| `project.materials[]` | no | the archives, datasets and software the paper cites: `kind`, `name`, `identifier`, `note` (e.g. "cited, not verified") |
| `result.level` | paper mode | `"L0"`, `"L1"` or `"L2"`; `null` in the code-only modes. Never L3 or L4 |
| `result.reuse` | code-only mode | `{"R1": {"status": "met", "note": "…"}, "R2": …, "R3": …, "R4": …}`; status `met`, `not_met` or `not_settled` |
| `result.summary` | yes | two sentences: what holds the level (or the Reuse result) and the most important to-do |
| `result.next` | no | one sentence: what the next level (or the next R) needs |
| `results[]` | paper mode | every main-text figure and table that shows results (leave out schematics and tables of reagents or protocols): `label` ("Fig 2", "Table 1"), `title`, `checked` (true for the ones you checked), `A1`/`A2`/`A3` states, `code` (["path:line", …] where the values are computed), `note` (one short line); for one not checked, `reason` |
| `requirements[]` | yes | paper mode: one entry for each of A1–A3 and B1–B10 (B9 is `not_checked` unless you noticed a contradiction or made the comparison of SKILL.md Step 6); code-only modes: `[]`, with R1–R4 in `result.reuse`. Fields: `code`, `status` (`met`, `not_met`, `not_settled`, `not_applicable`, `not_checked`), `note` (one line) |
| `findings[]` | yes | see below; may be empty |
| `not_checked[]` | no | anything else you did not check, beyond the standard list the report always prints |

## A finding

| Field | What to write |
|---|---|
| `id` | short, stable: e.g. `b2-no-cited-version`, `a1-fig3-no-code`. Reuse the previous self-check's `id` when it is the same problem |
| `code` | the requirement code: `A1`–`A3`, `B1`–`B10`, `C1`–`C4`, `P1`, `P2`, `R1`–`R4`, `G1`–`G4`, `J` |
| `impact` | `blocks_l1`, `blocks_l2`, `caps_l1`, `blocks_automation`, `reuse` (an open R1–R4) or `warning` |
| `title` | what is wrong and where, in one line (at most two names; else a count and the shared place) |
| `detail` | optional: one to three sentences |
| `evidence[]` | at least one: `where` (`path/to/file.py:42`, `README.md:10-14`, `analysis.ipynb cell 12`, "Methods, section Data analysis", a URL, "repository tree") and an optional short `quote` of what is there (one line; escape tabs and newlines as JSON requires). Never quote a secret |
| `results` | optional: the results it affects, e.g. `["Fig 2", "Table 1"]` |
| `todo` | the concrete next step |
| `who` | `agent_can_fix` (Your coding agent can fix this), `agent_needs_answer` (Your agent can help · needs your answer) or `authors_only` (Authors only); when a to-do needs more than one, the most demanding |
| `noticed_only` | optional: `true` for a paper–code contradiction you saw without searching for it |

## Rules the renderer enforces

- A `blocks_l1` finding, or A1–A3 not met or not settled, means `L0`.
- `L2` needs A1–A3 and B1–B8, B10 each recorded as met (or not applicable),
  B9 recorded as met from the comparison, and no `blocks_l2` or `caps_l1`
  finding.
- A `caps_l1` finding cannot stand beside B9 recorded as met.
- An open R1–R4 needs a `reuse` finding with its to-do.
- Every finding has evidence and a to-do; ids are unique.
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
    "level": "L1",
    "summary": "Code, inputs and software were found for the results checked. A rerun still needs a fixed code version and a map from figures to scripts.",
    "next": "L2 needs a cited version of the code and a results table in the README."
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
    {"id": "b2-no-cited-version", "code": "B2", "impact": "blocks_l2",
     "title": "The paper cites the repository without a fixed version",
     "evidence": [{"where": "Paper, Code availability", "quote": "Code is available at github.com/example/cell-filtering"}],
     "results": ["Fig 2"],
     "todo": "Tag the version you submit, archive it with a DOI and cite that version DOI in the paper.",
     "who": "authors_only"}
  ]
}
```
