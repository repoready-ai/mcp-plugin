---
description: Make this repository (and its paper text) submission ready with the free self-check, then check it again (needs a free RepoReady account; nothing of yours is uploaded)
argument-hint: "[paper PDF, DOI or link] [repository URL]"
---

Make the current repository submission ready by following the repoready
plugin's **reproducibility-self-check** skill: its `SKILL.md`, Step 1 first
(the sign-in, then the confirmation of paper, code and data), then
`make-ready.md` from Step M1.

- Changes go only to the working copy the user agrees to (a new branch, or
  a new folder when the code is assembled into a clean submission
  repository). Nothing is committed, pushed, tagged, released or archived
  without the user's yes to that step.
- Facts only the authors know (versions used, data sources, parameters,
  the license) are asked, never guessed. Nothing that changes what the code
  computes is changed without the user's answer.
- Every check is the ordinary self-check with its report; the last one runs
  on the tagged version.

Inputs: the current repository, plus $ARGUMENTS when given (a paper PDF, a
DOI or paper link, or another public repository).

End with the to-dos by severity of the first and last check, what changed and where, the
questions still open, the authors' checklist and the report paths.
