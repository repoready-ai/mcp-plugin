---
description: Free reproducibility self-check of this repository (needs a free RepoReady account; nothing of yours is uploaded)
argument-hint: "[paper PDF, DOI or link] [repository URL]"
---

Run a free RepoReady self-check by following the repoready plugin's
**reproducibility-self-check** skill (`skills/reproducibility-self-check/SKILL.md`) exactly.

- **Every self-check needs a free RepoReady account**, which takes one
  sign-in: the skill checks that first, before it reads anything, says how
  to connect when the RepoReady tools are not listed, and waits. RepoReady
  gets the sign-in and one `get_account` call, nothing of the work.
- **With a paper** that has public links, the self-check also sends those
  (the paper's DOI or link and the public repositories it names) to find
  its materials. The to-dos of a platform assessment the user already
  holds, and "Ask my institute", only on the user's yes (`signed-in-extras.md`).

It never sends their code, paper file, report or `findings.json`, and never
starts a paid check without their yes to its price and who pays.

Inputs: the current repository, plus $ARGUMENTS when given (a paper PDF, a
DOI or paper link, or another public repository). With no paper given, the
skill looks for one, and it confirms the paper, code and data it will use
before the audit. It gives no level: to-dos, each Critical, Important or Recommended; for code
alone, the Software reuse result R1–R4. It reads statically and runs no code
unless the user says yes.

End with the report paths (`repoready-self-check/<date>-<slug>.html` and
`.md`), the to-dos by severity as the renderer prints them, the to-dos that
matter most, and what a self-check does not cover. A platform assessment, whose
level and share link count, is the repoready skill's flow
(`/repoready:analyze`), paid through an institute or a journal.
