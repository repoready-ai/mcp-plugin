# Extras for a signed-in user

Read this file only after the user says yes to one of these extras
(`SKILL.md`, Step 1, item 7). The rules of `signed-in.md` ("What stays the
same") hold here too, and:

- **Nothing paid without a yes.** Never start a check without telling the
  user its credits and who pays and getting their explicit yes to that
  quote. Never open or approve an approval link for them.

## 3. The to-do loop on a platform assessment the user holds

Only for the user's own project (they are its owner) that has a finished
platform assessment: find it with `list_projects` (`repo` = the git remote) or
`identify_source`, then `get_ladder` for its level line (`headline`, as
given). Keep it apart from the self-check: two different results.

1. `list_todos({projectId, status: 'open'})`: the platform assessment's to-dos, goals in
   order (To reach L1, To reach L2, Optional · beside the level), each
   finding's numbered steps and who can do each. `get_issue` with a step's
   `issueIds` gives the `file:line` citations. `counts.markedFixed` is the
   N of "Check N fixes".
2. With the user, one answer per finding. None of them changes the level,
   a badge or a journal's target.
   - **Fixed.** Make the fix as an ordinary edit after the user's yes. The
     user commits and pushes it: a fix check reads the latest pushed commit
     of the repository the project already checks (nothing is uploaded).
     Then `answer_finding({issueId, answer: 'fixed'})`: the finding reads
     "Marked fixed · not checked yet" until a check says "Fixed" or "Still
     open". A Warning cannot be marked (`warning_not_checked`): it blocks
     nothing.
   - **Wrong.** `report_wrong({issueId, pointers})` with where to look
     (`file` with `path` and `line`, `figure`, `manuscript` with a quote or
     section, `accession`, `url`), first without `confirm`: show the user
     the preview ("We'll look at: …", and any place refused with why). Only
     after they agree, the same call with `confirm: true`. It is free; if
     the re-check keeps the finding, a report about it goes to RepoReady
     unless `reportIfUpheld: false`. Follow it with `get_issue`. Refused
     `recheck_repository_scope`: the user reports it in the web app.
   - **Won't change.** `answer_finding({issueId, answer: 'explain',
     reason, …})` with the user's reason: restricted data declared in the
     paper (`restricted_declared`), not applicable to this paper
     (`not_applicable`), done at publication (`at_publication`, with
     `date`), or other (`other`, with `statement` in the user's own words;
     never write it for them). First show them exactly what will be stored
     and that link holders and exports show it as "Authors' response" and
     that it goes to a journal with a revision they send. A receipt code
     the user gives a journal carries the version and its check, never
     these answers; the answers travel only with a revision. Never write a
     receipt code into the report, `findings.json`, a file or a commit.
   - `answer: 'undo'` takes back an unchecked mark, else an explanation
     (`nothing_to_undo` when there is neither).
3. **Check N fixes.** `estimate_run({projectId, intent: 'fixes'})` checks
   every finding marked fixed (`target.issueIds` for only some). Tell the
   user in one message the credits and who pays ("0 credits · billed to
   <payer>"; 0 credits within 3 fix checks per version and 8 starts a
   day) and whether a browser approval follows. Only after their explicit
   yes: `start_run({quoteId, kind: 'fixes'})`. If it answers
   `awaiting_approval`, give them the `approvalUrl`, and after they
   approved call `start_run` again with the same `quoteId`. Poll `get_run`
   after `pollAfterSeconds`; then each finding's `fixMark` (`get_issue`)
   says "Fixed" or "Still open", with what the check saw.
   - `nothing_marked`: no finding is marked fixed yet.
   - `fix_batches_used_up`: the free fix checks of this version are used;
     only Check again is left, which costs credits: price it
     (`intent: 'check_again'`) and ask again, never on your own.
   - `sponsor_refused`: a journal pays for this project's checks; the user
     starts "Check N fixes" in the web app. Only if the refusal offers the
     institute (`ownPayer: 'organization'`) and the user agrees that their
     institute's credits pay instead, estimate again with
     `confirm_own_payer: true` and ask again.
   - `needs_payer`: nobody pays; see 4.

## 4. "Ask my institute"

When nobody pays for the user's platform assessments (`funding.default:
'none'`, or a quote refused `needs_payer`) and the user wants them:

1. `request_institute_access({})` without `consent` is a preview; nothing is
   stored. It says either who gets the request (the admins of the user's
   institution's RepoReady organisation, who see the user's name and email
   and approve or decline; once approved, the institution's credits pay)
   or that RepoReady records the interest and emails the user when the
   institution joins. A request reaches an organisation's admins only from
   the user's verified sign-in address on that organisation's own email
   domain; an unverified address that would reach one is refused
   `email_not_verified` (the user verifies it first). With a public email
   domain, ask the user for their institution's ROR id and pass `rorId`
   (the id or its `https://ror.org/` link; `institutionName` may add the
   name): that only records interest, never a request. The preview may
   instead say `already_open` (a request is still open) or
   `already_member` (an organisation pays already), and `blockedBy` when
   the user belongs to another organisation.
2. Show the user the preview as it reads. Only after they agreed to exactly
   that, the same call with `consent: true`; a confirmation email follows.
3. `institution_unknown` (a public email domain and no `rorId`: ask for
   it), `invalid_ror`, `request_open` (one is open already),
   `too_many_requests`, `recently_declined` (that organisation declined in
   the last 90 days), `in_other_organization`, `already_member`: tell the
   user. They withdraw an open request in the web app (Settings › Billing).

The self-check stays free either way.
