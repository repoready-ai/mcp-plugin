#!/usr/bin/env python3
"""Render a RepoReady self-check findings.json into an HTML and a Markdown report.

Standard library only (Python 3.8+). Usage:

    python3 render_report.py repoready-self-check/2026-11-06-myrepo.findings.json
        [--previous PATH | --no-previous] [--template PATH] [--out-dir DIR]

It writes <stem>.html and <stem>.md beside the input (or in --out-dir), where
<stem> is the input's name without ".findings.json". The previous self-check
is the newest earlier "*-<slug>.findings.json" in the same folder, unless
--previous or --no-previous says otherwise.

The format is documented in ../references/findings-format.md and
../references/findings.schema.json. The renderer refuses a file that breaks
the self-check's rules (a level above L2, a level that its own findings
contradict, a finding without evidence or to-do, a status image or badge
Markdown, a score) and says what to fix. It makes no network call.
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import sys
from pathlib import Path

FORMAT = "repoready-self-check/1"
SKILL_VERSION = "0.1"
NOTICE = "Self-check · user generated · not a RepoReady certification"
OFFICIAL_URL = "https://repoready.ai/self-check?ref=report"
NO_MODEL = "model not stated by the agent"

LEVEL_NAMES = {"L0": "Incomplete", "L1": "Available", "L2": "Rerunnable"}

# Public requirement names (repoready.ai/docs/checks), by code.
REQUIREMENT_NAMES = {
    "A1": "Code for each result is available",
    "A2": "Input data can be obtained",
    "A3": "Required software can be obtained",
    "B1": "Dependencies and versions are listed",
    "B2": "The exact code version is identified",
    "B3": "Data sources have stable identifiers",
    "B4": "Data preparation steps are documented",
    "B5": "Code is linked to the paper’s results",
    "B6": "Instructions explain how to run the analysis",
    "B7": "Documented commands agree with the code",
    "B8": "Machine assumptions documented",
    "B9": "Outputs correspond to the reported results",
    "B10": "Randomness of key results is controlled",
    "C1": "One command produces the results",
    "C2": "The software environment is pinned",
    "C3": "Input retrieval is automated",
    "C4": "Random seeds and variability are controlled",
    "P1": "Access conditions",
    "P2": "A lasting archive",
    "R1": "Installation",
    "R2": "Documented interface and examples",
    "R3": "Automated tests",
    "R4": "Releases and license",
    "G1": "A tidy repository",
    "G2": "Tests and notebooks",
    "G3": "Paper, data and docs agree",
    "G4": "Hardware, tools and versions",
    "J": "Journal policy",
}
CODE_ORDER = list(REQUIREMENT_NAMES)

MODES = {
    "paper_and_code": "Paper and code: an indicative level",
    "code_only": "Code only: the Software reuse result",
    "analysis_code_only": "Analysis code without its paper",
}
STATES = {
    "met": "Met",
    "not_met": "Not met",
    "not_settled": "Not settled",
    "not_applicable": "Not applicable",
    "not_checked": "Not checked",
}
IMPACTS = {
    "blocks_l1": "Blocks L1",
    "blocks_l2": "Blocks L2",
    "caps_l1": "Caps at L1",
    "blocks_automation": "Blocks Automation",
    "reuse": "Reuse",
    "warning": "Warning",
}
WHO = {
    "agent_can_fix": "Your coding agent can fix this",
    "agent_needs_answer": "Your agent can help · needs your answer",
    "authors_only": "Authors only",
}
GROUPS = [
    ("What L1 needs", ("blocks_l1",)),
    ("What L2 needs", ("blocks_l2", "caps_l1")),
    ("Software reuse", ("reuse",)),
    ("Beside the level", ("blocks_automation", "warning")),
]
STANDARD_NOT_CHECKED = [
    "Integrity: whether the paper's methods, parameters, statistics and numbers agree with the code (anything noticed is marked so).",
    "Deposits and archives: whether cited datasets and archives really hold the files the code reads.",
    "Supplementary results: only main-text figures and tables are checked as results.",
    "Verification by a second model: one agent read everything once.",
    "L3 Re-executed and L4 Reproduced: the code was not run.",
]
# With a paper, the first two lines of the list say what was actually done.
INTEGRITY_NOT_COMPARED = ("Integrity: whether the paper's methods, parameters, statistics and numbers agree with the "
                          "code. They are compared only when a check would otherwise reach L2 (anything noticed is marked so).")
INTEGRITY_COMPARED = ("A second reading of Integrity: one agent compared the paper and the code once, and values that "
                      "exist only when the code runs could not be compared.")
DEPOSITS_FROM_LISTS = ("Deposits and archives: only public file lists were read and matched by file name; "
                       "the files themselves were not opened.")
# Words a self-check report never uses in its own prose (titles, details,
# to-dos, summaries). Evidence quotes are the user's own text and are exempt.
BANNED_PROSE = [
    (re.compile(r"badge", re.I), "a README badge or status image"),
    (re.compile(r"shields\.io", re.I), "a status image"),
    (re.compile(r"!\["), "image Markdown"),
    (re.compile(r"certif(?:ied|icate|ication)", re.I), "a certification claim"),
    (re.compile(r"reproducibility score|\b\d{1,3} ?/ ?100\b|\b\d{1,3}(?:\.\d+)? ?% (?:reproducib|ready|complete)", re.I), "a score or percentage"),
    (re.compile(r"free trial|own (?:api )?key", re.I), "account or pricing words"),
]


VERSION_RE = re.compile(r"\d+(?:\.\d+){0,2}")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
COMMIT_RE = re.compile(r"[0-9a-fA-F]{7,64}")
# Line breaks of every kind a Markdown or HTML reader honours; text fields are one line.
LINE_BREAKS = re.compile(r"[\r\n\v\f\x85\u2028\u2029]+")


class FindingsError(Exception):
    """The findings file breaks the format or the self-check's rules."""


# --------------------------------------------------------------------------
# Loading and validation


def _req(obj, key, kind, where):
    if not isinstance(obj, dict) or key not in obj:
        raise FindingsError(f"{where}: missing '{key}'")
    value = obj[key]
    if kind is not None and not isinstance(value, kind):
        raise FindingsError(f"{where}.{key}: expected {getattr(kind, '__name__', kind)}")
    return value


def _text(value, where, required=True):
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise FindingsError(f"{where}: expected non-empty text")
    return value.strip()


def _check_prose(value, where, problems):
    if not isinstance(value, str):
        return
    for pattern, what in BANNED_PROSE:
        if pattern.search(value):
            problems.append(f"{where}: remove {what} (\"{pattern.search(value).group(0)}\")")


def _check_text(value, where, problems):
    """Optional free text the report prints: text or null, and the prose policy."""
    if value is None:
        return
    if not isinstance(value, str):
        problems.append(f"{where}: text")
        return
    _check_prose(value, where, problems)


def _valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise FindingsError(f"{path}: not valid JSON ({exc})") from exc
    validate(data)
    return data


def validate(data):
    """Raise FindingsError listing every problem found."""
    if not isinstance(data, dict):
        raise FindingsError("findings.json must be a JSON object")
    problems = []
    if data.get("format") != FORMAT:
        problems.append(f"format: must be \"{FORMAT}\"")
    mode = data.get("mode")
    if mode not in MODES:
        problems.append(f"mode: one of {', '.join(MODES)}")
    if not _valid_date(data.get("date")):
        problems.append("date: an ISO date, YYYY-MM-DD")
    value = data.get("skill_version")
    if value is not None and not (isinstance(value, str) and VERSION_RE.fullmatch(value)):
        problems.append(f"skill_version: a version number such as \"{SKILL_VERSION}\" (the report prints the renderer's own)")
    agent = data.get("agent")
    if not isinstance(agent, dict) or not isinstance(agent.get("name"), str) or not agent["name"].strip():
        problems.append("agent.name: the agent product, e.g. \"Claude Code\"")
    else:
        _check_prose(agent["name"], "agent.name", problems)
        if agent.get("model") is not None and not isinstance(agent.get("model"), str):
            problems.append("agent.model: the model id as text, or null")
        _check_prose(agent.get("model"), "agent.model", problems)
    project = data.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str) or not project["name"].strip():
        problems.append("project.name: required")
    else:
        _check_prose(project["name"], "project.name", problems)
        slug = project.get("slug")
        if slug is not None and not (isinstance(slug, str) and SLUG_RE.fullmatch(slug)):
            problems.append("project.slug: lowercase letters, digits and hyphens")
        repos = project.get("repositories", [])
        if not isinstance(repos, list):
            problems.append("project.repositories: a list")
            repos = []
        for i, repo in enumerate(repos):
            if not isinstance(repo, dict):
                problems.append(f"project.repositories[{i}]: an object")
                continue
            commit = repo.get("commit")
            if commit not in (None, "") and not (isinstance(commit, str) and COMMIT_RE.fullmatch(commit)):
                problems.append(f"project.repositories[{i}].commit: a commit SHA, or null")
            for key in ("url", "name", "ref", "role"):
                _check_text(repo.get(key), f"project.repositories[{i}].{key}", problems)
        paper = project.get("paper")
        if mode == "paper_and_code" and not isinstance(paper, dict):
            problems.append("project.paper: required in paper_and_code mode")
        if isinstance(paper, dict):
            for key in ("title", "doi", "read_from"):
                _check_text(paper.get(key), f"project.paper.{key}", problems)
        materials = project.get("materials", [])
        if not isinstance(materials, list):
            problems.append("project.materials: a list")
            materials = []
        for i, m in enumerate(materials):
            if not isinstance(m, dict):
                problems.append(f"project.materials[{i}]: an object")
                continue
            for key in ("kind", "name", "identifier", "note"):
                _check_text(m.get(key), f"project.materials[{i}].{key}", problems)

    result = data.get("result")
    if not isinstance(result, dict):
        problems.append("result: required")
        result = {}
    level = result.get("level")
    if level not in (None, "L0", "L1", "L2"):
        problems.append("result.level: a self-check gives L0, L1 or L2 (never L3 or L4), or null")
    if mode == "paper_and_code" and level is None:
        problems.append("result.level: required in paper_and_code mode")
    if mode != "paper_and_code" and level is not None:
        problems.append("result.level: only a paper with its code gets a level; use null")
    for key in ("summary", "next"):
        if key in result and not isinstance(result[key], str):
            problems.append(f"result.{key}: text")
        _check_prose(result.get(key), f"result.{key}", problems)

    reuse = result.get("reuse")
    if mode == "code_only":
        if not isinstance(reuse, dict) or any(code not in reuse for code in ("R1", "R2", "R3", "R4")):
            problems.append("result.reuse: R1, R2, R3 and R4 are required in code_only mode")
    if isinstance(reuse, dict):
        for code in ("R1", "R2", "R3", "R4"):
            entry = reuse.get(code)
            if entry is None:
                continue
            if not isinstance(entry, dict) or entry.get("status") not in ("met", "not_met", "not_settled"):
                problems.append(f"result.reuse.{code}.status: met, not_met or not_settled")
            else:
                _check_prose(entry.get("note"), f"result.reuse.{code}.note", problems)

    results = data.get("results", [])
    if not isinstance(results, list):
        problems.append("results: a list")
        results = []
    for i, r in enumerate(results):
        if not isinstance(r, dict) or not isinstance(r.get("label"), str) or not r["label"].strip():
            problems.append(f"results[{i}].label: required")
            continue
        for key in ("label", "title", "note", "reason"):
            _check_text(r.get(key), f"results[{i}].{key}", problems)
        code = r.get("code", [])
        if not isinstance(code, list) or not all(isinstance(c, str) for c in code):
            problems.append(f"results[{i}].code: a list of \"path:line\" text")
        for key in ("A1", "A2", "A3"):
            if key in r and r[key] not in STATES:
                problems.append(f"results[{i}].{key}: one of {', '.join(STATES)}")

    requirements = data.get("requirements", [])
    if not isinstance(requirements, list):
        problems.append("requirements: a list")
        requirements = []
    req_status = {}
    for i, r in enumerate(requirements):
        if not isinstance(r, dict) or r.get("code") not in REQUIREMENT_NAMES:
            problems.append(f"requirements[{i}].code: one of {', '.join(CODE_ORDER)}")
            continue
        if r.get("status") not in STATES:
            problems.append(f"requirements[{i}].status: one of {', '.join(STATES)}")
            continue
        req_status[r["code"]] = r["status"]
        _check_prose(r.get("note"), f"requirements[{i}].note", problems)

    findings = data.get("findings", [])
    if not isinstance(findings, list):
        problems.append("findings: a list")
        findings = []
    seen = set()
    impacts = set()
    for i, f in enumerate(findings):
        where = f"findings[{i}]"
        if not isinstance(f, dict):
            problems.append(f"{where}: an object")
            continue
        fid = f.get("id")
        if not isinstance(fid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", fid):
            problems.append(f"{where}.id: letters, digits, '.', '_' or '-' (keep it across self-checks)")
        elif fid in seen:
            problems.append(f"{where}.id: \"{fid}\" is used twice")
        else:
            seen.add(fid)
        if f.get("code") not in REQUIREMENT_NAMES:
            problems.append(f"{where}.code: one of {', '.join(CODE_ORDER)}")
        if f.get("impact") not in IMPACTS:
            problems.append(f"{where}.impact: one of {', '.join(IMPACTS)}")
        else:
            impacts.add(f["impact"])
        if f.get("who") not in WHO:
            problems.append(f"{where}.who: one of {', '.join(WHO)}")
        for key in ("title", "todo"):
            if not isinstance(f.get(key), str) or not f[key].strip():
                problems.append(f"{where}.{key}: required")
            _check_prose(f.get(key), f"{where}.{key}", problems)
        _check_prose(f.get("detail"), f"{where}.detail", problems)
        affected = f.get("results", [])
        if not isinstance(affected, list) or not all(isinstance(x, str) for x in affected):
            problems.append(f"{where}.results: a list of result labels")
        else:
            for j, label in enumerate(affected):
                _check_prose(label, f"{where}.results[{j}]", problems)
        evidence = f.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{where}.evidence: at least one place you read (file:line, a paper section or a URL)")
        else:
            for j, ev in enumerate(evidence):
                if not isinstance(ev, dict) or not isinstance(ev.get("where"), str) or not ev["where"].strip():
                    problems.append(f"{where}.evidence[{j}].where: required")
                elif ev.get("quote") is not None and not isinstance(ev.get("quote"), str):
                    problems.append(f"{where}.evidence[{j}].quote: text")

    # The level must follow from the findings and requirements (no leniency).
    if mode == "paper_and_code" and level in ("L0", "L1", "L2"):
        a_open = [c for c in ("A1", "A2", "A3") if req_status.get(c) in ("not_met", "not_settled")]
        b_open = [c for c in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B10")
                  if req_status.get(c) in ("not_met", "not_settled")]
        if level != "L0" and ("blocks_l1" in impacts or a_open):
            problems.append("result.level: a Blocks L1 finding or an open A requirement means L0")
        if "caps_l1" in impacts and req_status.get("B9") == "met":
            problems.append("requirements: a Caps at L1 finding means B9 is not met")
        if level == "L2":
            if req_status.get("B9") != "met":
                problems.append("result.level: L2 needs B9 compared for every checked result and recorded as met")
            if impacts & {"blocks_l2", "caps_l1"} or b_open:
                problems.append("result.level: L2 needs every B requirement met and no Blocks L2 or Caps at L1 finding")
            missing = [c for c in ("A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B10")
                       if req_status.get(c) not in ("met", "not_applicable")]
            if missing:
                problems.append("result.level: L2 needs A1-A3 and B1-B8, B10 each recorded as met (or not applicable): "
                                + ", ".join(missing))
    if isinstance(reuse, dict):
        for code in ("R1", "R2", "R3", "R4"):
            entry = reuse.get(code)
            if isinstance(entry, dict) and entry.get("status") in ("not_met", "not_settled"):
                if not any(isinstance(f, dict) and f.get("code") == code and f.get("impact") == "reuse" for f in findings):
                    problems.append(f"findings: {code} is open, so it needs a Reuse finding with its to-do")

    extra = data.get("not_checked", [])
    if not isinstance(extra, list) or not all(isinstance(x, str) for x in extra):
        problems.append("not_checked: a list of text")
    else:
        for i, item in enumerate(extra):
            _check_prose(item, f"not_checked[{i}]", problems)
    if problems:
        raise FindingsError("findings.json breaks the self-check format:\n  - " + "\n  - ".join(problems))


# --------------------------------------------------------------------------
# Since the last self-check


def find_previous(path: Path, data):
    slug = data.get("project", {}).get("slug") or _slug_from_name(path.name)
    if not slug:
        return None
    candidates = sorted(
        p for p in path.parent.glob(f"*-{slug}.findings.json")
        if p.resolve() != path.resolve() and p.name < path.name
    )
    return candidates[-1] if candidates else None


def _slug_from_name(name):
    m = re.fullmatch(r"\d{4}-\d{2}-\d{2}-(.+)\.findings\.json", name)
    return m.group(1) if m else None


def _match_key(f):
    return (f.get("code"), re.sub(r"\s+", " ", str(f.get("title", "")).strip().lower()))


def compare(previous, current):
    """Return (fixed, still_open, new) lists of findings, matched by id, then by code and title."""
    prev = [f for f in previous.get("findings", []) if isinstance(f, dict)]
    cur = [f for f in current.get("findings", []) if isinstance(f, dict)]
    prev_ids = {f.get("id") for f in prev}
    cur_ids = {f.get("id") for f in cur}
    matched_prev, matched_cur = set(), set()
    for f in cur:
        if f.get("id") in prev_ids:
            matched_cur.add(id(f))
    for f in prev:
        if f.get("id") in cur_ids:
            matched_prev.add(id(f))
    prev_by_key = {}
    for f in prev:
        if id(f) not in matched_prev:
            prev_by_key.setdefault(_match_key(f), []).append(f)
    for f in cur:
        if id(f) in matched_cur:
            continue
        pool = prev_by_key.get(_match_key(f))
        if pool:
            matched_prev.add(id(pool.pop(0)))
            matched_cur.add(id(f))
    fixed = [f for f in prev if id(f) not in matched_prev]
    still = [f for f in cur if id(f) in matched_cur]
    new = [f for f in cur if id(f) not in matched_cur]
    return fixed, still, new


# --------------------------------------------------------------------------
# Building the report model (shared by HTML and Markdown)


def _short_commit(repo):
    commit = str(repo.get("commit") or "").strip()
    return commit[:12] if commit else ""


def build(data, previous=None, previous_name=None):
    agent = data["agent"]
    model = agent.get("model")
    model_text = model.strip() if isinstance(model, str) and model.strip() else NO_MODEL
    project = data["project"]
    result = data.get("result", {})
    mode = data["mode"]
    results = [r for r in data.get("results", []) if isinstance(r, dict)]
    checked = [r for r in results if r.get("checked", True)]
    unchecked = [r for r in results if not r.get("checked", True)]
    findings = [f for f in data.get("findings", []) if isinstance(f, dict)]
    requirements = sorted(
        (r for r in data.get("requirements", []) if isinstance(r, dict)),
        key=lambda r: CODE_ORDER.index(r["code"]) if r.get("code") in CODE_ORDER else 99,
    )
    if isinstance(result.get("reuse"), dict):
        # R1-R4 have their own table; do not print them twice.
        requirements = [r for r in requirements if r.get("code") not in ("R1", "R2", "R3", "R4")]
    level_codes = ("A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10")
    unsettled = sum(1 for r in requirements if r.get("code") in level_codes and r.get("status") == "not_settled")
    a_not_met = any(r.get("code") in ("A1", "A2", "A3") and r.get("status") == "not_met" for r in requirements) or any(
        r.get(k) == "not_met" for r in checked for k in ("A1", "A2", "A3"))
    a_unsettled = sum(1 for r in requirements if r.get("code") in ("A1", "A2", "A3") and r.get("status") == "not_settled")

    reuse = result.get("reuse") if isinstance(result.get("reuse"), dict) else None
    reuse_line = ""
    if reuse:
        met = sum(1 for c in ("R1", "R2", "R3", "R4") if (reuse.get(c) or {}).get("status") == "met")
        reuse_line = "Reusable" if met == 4 else f"Reuse: {met} of 4"

    if mode == "paper_and_code":
        level = result["level"]
        if level == "L0" and not a_not_met and a_unsettled:
            # Nothing is confirmed missing: L0 would overstate it.
            result_line = f"Self-assessed · not yet at L1 · {a_unsettled} to verify · indicative, at most L2"
        else:
            result_line = f"Self-assessed · {level} · {LEVEL_NAMES[level]} · indicative, at most L2"
            # Only what holds this level back: A items for L0, B items for L1.
            held = a_unsettled if level == "L0" else (unsettled - a_unsettled if level == "L1" else 0)
            if held:
                result_line += f" · {held} not settled"
        total = len(results)
        scope_line = (f"For {len(checked)} of {total} main-text results checked, read statically in your own agent."
                      if total else "Read statically in your own agent.")
        if reuse_line:
            scope_line += f" Software reuse beside the level: {reuse_line}."
    elif mode == "code_only":
        result_line = f"Self-assessed · {reuse_line} · Software reuse, no level for code alone"
        scope_line = "Code checked on its own gets no level; its answer is the Software reuse result R1–R4."
    else:
        result_line = "No level · add the paper"
        scope_line = "Analysis code without its paper gets no level. Run the self-check again with the paper (a PDF or DOI)."

    since_line = "First self-check of this project in this folder."
    since_fixed = []
    if previous is not None:
        fixed, still, new = compare(previous, data)
        prev_date = previous.get("date", "")
        prev_commit = ""
        prev_repos = previous.get("project", {}).get("repositories") or []
        if prev_repos and isinstance(prev_repos[0], dict):
            prev_commit = _short_commit(prev_repos[0])
        when = prev_date + (f", commit {prev_commit}" if prev_commit else "")
        since_line = (f"Since the last self-check ({when}): {len(fixed)} fixed · "
                      f"{len(still)} still open · {len(new)} new")
        since_fixed = [f"{f.get('code', '')} · {f.get('title', '')}" for f in fixed]

    repos = project.get("repositories") or []
    commit_bits = []
    for repo in repos:
        if not isinstance(repo, dict):
            continue
        bit = repo.get("url") or repo.get("name") or "repository"
        if repo.get("ref"):
            bit += f" ({repo['ref']})"
        if _short_commit(repo):
            bit += f" at commit {_short_commit(repo)}"
        if repo.get("uncommitted_changes"):
            bit += ", with uncommitted changes"
        commit_bits.append(bit)
    commit_text = "; ".join(commit_bits) if commit_bits else "no commit recorded"

    facts = [("Agent", agent["name"].strip()), ("Model", model_text),
             ("Skill", f"RepoReady self-check v{SKILL_VERSION}"),
             ("Date", data["date"]), ("Mode", MODES[mode])]
    for repo_text in commit_bits:
        facts.append(("Repository", repo_text))
    paper = project.get("paper")
    if isinstance(paper, dict):
        bits = [paper.get("title") or "", ("DOI " + paper["doi"]) if paper.get("doi") else "", paper.get("read_from") or ""]
        facts.append(("Paper", " · ".join(b for b in bits if b)))
    for m in project.get("materials") or []:
        if isinstance(m, dict) and (m.get("name") or m.get("identifier")):
            bits = [m.get("kind") or "", m.get("name") or "", m.get("identifier") or "", m.get("note") or ""]
            facts.append(("Material", " · ".join(b for b in bits if b)))

    groups = []
    for title, impacts in GROUPS:
        items = [f for f in findings if f.get("impact") in impacts]
        if items:
            items.sort(key=lambda f: (CODE_ORDER.index(f["code"]) if f.get("code") in CODE_ORDER else 99))
            groups.append((title, items))

    not_checked = list(STANDARD_NOT_CHECKED)
    if mode == "paper_and_code":
        b9 = next((r.get("status") for r in requirements if r.get("code") == "B9"), None)
        compared = b9 in ("met", "not_settled") or (b9 == "not_met" and any(
            f.get("impact") == "caps_l1" and not f.get("noticed_only") for f in findings))
        not_checked[:2] = [INTEGRITY_COMPARED if compared else INTEGRITY_NOT_COMPARED, DEPOSITS_FROM_LISTS]
    else:
        not_checked = [x for x in not_checked if not x.startswith("Supplementary results")]
    not_checked += [x for x in data.get("not_checked", []) if isinstance(x, str) and x.strip()]

    return {
        "project_name": project["name"].strip(),
        "date": data["date"],
        "agent_name": agent["name"].strip(),
        "model_text": model_text,
        # The renderer is part of the skill: its own version, never the file's text.
        "skill_version": SKILL_VERSION,
        "result_line": result_line,
        "scope_line": scope_line,
        "summary": (result.get("summary") or "").strip(),
        "next_line": (result.get("next") or "").strip(),
        "since_line": since_line,
        "since_fixed": since_fixed,
        "facts": facts,
        "checked": checked,
        "unchecked": unchecked,
        "reuse": reuse,
        "requirements": requirements,
        "groups": groups,
        "not_checked": not_checked,
        "commit_text": commit_text,
        "mode": mode,
        "previous_name": previous_name,
    }


# --------------------------------------------------------------------------
# HTML


def e(text):
    return html.escape(str(text), quote=True)


def _state(status):
    return f'<span class="state">{e(STATES.get(status, status or "—"))}</span>' if status else "—"


def _where_html(where):
    return f"<code>{e(where)}</code>"


def render_html(model, template):
    slots = {}
    slots["since_details"] = (
        '<p class="muted">Fixed: ' + e("; ".join(model["since_fixed"])) + "</p>" if model["since_fixed"] else "")
    slots["facts"] = "\n      ".join(
        f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in model["facts"])

    if model["mode"] == "paper_and_code" and (model["checked"] or model["unchecked"]):
        rows = []
        for r in model["checked"]:
            label = r["label"] + (f" · {r['title']}" if r.get("title") else "")
            where = ", ".join(_where_html(c) for c in (r.get("code") or []) if isinstance(c, str)) or "—"
            note = f'<br><span class="muted">{e(r["note"])}</span>' if r.get("note") else ""
            rows.append(f"<tr><td>{e(label)}{note}</td><td>{_state(r.get('A1'))}</td>"
                        f"<td>{_state(r.get('A2'))}</td><td>{_state(r.get('A3'))}</td><td>{where}</td></tr>")
        part = ['<h2>Results checked</h2>']
        if rows:
            part.append('<div class="scroll"><table class="results"><thead><tr><th>Result</th><th>Code</th><th>Inputs</th>'
                        '<th>Software</th><th>Where</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
        if model["unchecked"]:
            items = "; ".join(r["label"] + (f" ({r['reason']})" if r.get("reason") else "") for r in model["unchecked"])
            part.append(f'<p class="muted">Not checked: {e(items)}</p>')
        slots["results"] = "\n  ".join(part)
    else:
        slots["results"] = ""

    if model["reuse"]:
        rows = []
        for code in ("R1", "R2", "R3", "R4"):
            entry = model["reuse"].get(code) or {}
            rows.append(f'<tr><td><span class="tag">{code}</span>{e(REQUIREMENT_NAMES[code])}</td>'
                        f"<td>{_state(entry.get('status'))}</td><td>{e(entry.get('note') or '')}</td></tr>")
        slots["reuse"] = ('<h2>Software reuse</h2>\n  <div class="scroll"><table><thead><tr><th>Requirement</th>'
                          '<th>State</th><th>Note</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    else:
        slots["reuse"] = ""

    if model["requirements"]:
        rows = [f'<tr><td><span class="tag">{e(r["code"])}</span>{e(REQUIREMENT_NAMES[r["code"]])}</td>'
                f"<td>{_state(r.get('status'))}</td><td>{e(r.get('note') or '')}</td></tr>"
                for r in model["requirements"]]
        slots["requirements"] = ('<h2>Requirements</h2>\n  <div class="scroll"><table><thead><tr><th>Requirement</th>'
                                 '<th>State</th><th>Note</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    else:
        slots["requirements"] = ""

    if model["groups"]:
        parts = []
        for title, items in model["groups"]:
            parts.append(f"<h3>{e(title)}</h3>")
            for f in items:
                meta = [IMPACTS[f["impact"]], WHO[f["who"]]]
                if f.get("results"):
                    meta.append(", ".join(str(x) for x in f["results"]))
                if f.get("noticed_only"):
                    meta.append("noticed, not searched for")
                evidence = []
                for ev in f["evidence"]:
                    quote = f'<span class="quote">{e(ev["quote"])}</span>' if ev.get("quote") else ""
                    evidence.append(f"<li>{_where_html(ev['where'])}{quote}</li>")
                detail = f"<p>{e(f['detail'])}</p>" if f.get("detail") else ""
                parts.append(
                    f'<article class="finding" id="f-{e(f["id"])}">'
                    f'<h4><span class="tag">{e(f["code"])}</span>{e(f["title"])}</h4>'
                    f'<p class="meta">{e(" · ".join(meta))}</p>{detail}'
                    f'<ul>{"".join(evidence)}</ul>'
                    f'<p class="todo"><strong>To-do:</strong> {e(f["todo"])}</p></article>')
        slots["findings"] = "\n  ".join(parts)
    else:
        slots["findings"] = "<p>No findings were recorded for the results checked.</p>"

    slots["not_checked"] = "\n    ".join(f"<li>{e(x)}</li>" for x in model["not_checked"])

    # Drop the hand-filling notes from the template, then fill it in one pass,
    # so inserted text is never scanned for placeholders again. Every scalar is
    # HTML-escaped; slots hold markup built above from escaped text only.
    template = re.sub(r"<!--\s*\n\s*RepoReady self-check report template.*?-->\n", "", template, count=1, flags=re.S)
    template = re.sub(r"<!--\s*\n\s*Example markup for the slots.*?-->\n", "", template, count=1, flags=re.S)
    scalars = ("project_name", "date", "agent_name", "model_text", "skill_version",
               "result_line", "scope_line", "summary", "next_line", "since_line", "commit_text")
    missing = []

    def fill(match):
        name = match.group(1) or match.group(2)
        if match.group(1) is not None and name in scalars:
            return e(model[name])
        if match.group(2) is not None and name in slots:
            return slots[name]
        missing.append(match.group(0))
        return match.group(0)

    out = re.sub(r"\{\{([a-z_]+)\}\}|<!-- slot:([a-z_]+) -->", fill, template)
    if missing:
        raise FindingsError("template: unknown placeholders " + ", ".join(sorted(set(missing))))
    return out


# --------------------------------------------------------------------------
# Markdown


def _one_line(text):
    return LINE_BREAKS.sub(" ", str(text))


# A line that starts with one of these would open a heading, list, quote,
# thematic break, setext underline, table or fenced block.
BLOCK_START = re.compile(r"^(\s*)(?:([#>+=~-])|(\d+)([.)]))")


def md(text):
    """Escape text for one Markdown line or table cell: inline-safe and inert."""
    text = _one_line(text).strip()
    text = text.replace("\\", "\\\\").replace("|", "\\|")
    text = re.sub(r"([*_`<>\[\]!&])", r"\\\1", text)
    # Escape the punctuation itself (a backslash before a digit would print).
    return BLOCK_START.sub(
        lambda m: m.group(1) + ("\\" + m.group(2) if m.group(2) else m.group(3) + "\\" + m.group(4)), text)


def md_code(text, in_table=False):
    """A CommonMark code span: a fence one backtick longer than the longest run inside."""
    text = _one_line(text)
    if in_table:
        text = text.replace("|", "\\|")
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if text.startswith(("`", " ")) or text.endswith(("`", " ")) or not text else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def render_markdown(model):
    L = []
    L.append(f"> **SELF-CHECK** · {NOTICE}")
    L.append("")
    L.append(f"# {md(model['project_name'])}")
    L.append("")
    L.append(f"Reproducibility self-check of {md(model['date'])} · written by {md(model['agent_name'])} "
             f"({md(model['model_text'])}) with the RepoReady self-check skill {md('v' + model['skill_version'])}")
    L.append("")
    L.append(f"**{md(model['result_line'])}**")
    L.append("")
    L.append(md(model["scope_line"]))
    if model["summary"]:
        L += ["", md(model["summary"])]
    if model["next_line"]:
        L += ["", md(model["next_line"])]
    L += ["", f"**{md(model['since_line'])}**"]
    if model["since_fixed"]:
        L += ["", "Fixed: " + md("; ".join(model["since_fixed"]))]
    L += ["", "## About this self-check", "", "| | |", "|---|---|"]
    L += [f"| {md(k)} | {md(v)} |" for k, v in model["facts"]]

    if model["mode"] == "paper_and_code" and (model["checked"] or model["unchecked"]):
        L += ["", "## Results checked", ""]
        if model["checked"]:
            L += ["| Result | Code | Inputs | Software | Where |", "|---|---|---|---|---|"]
            for r in model["checked"]:
                label = r["label"] + (f" · {r['title']}" if r.get("title") else "")
                if r.get("note"):
                    label += f" ({r['note']})"
                where = ", ".join(md_code(c, in_table=True) for c in (r.get("code") or []) if isinstance(c, str)) or "—"
                L.append(f"| {md(label)} | {STATES.get(r.get('A1'), '—')} | {STATES.get(r.get('A2'), '—')} | "
                         f"{STATES.get(r.get('A3'), '—')} | {where} |")
        if model["unchecked"]:
            items = "; ".join(r["label"] + (f" ({r['reason']})" if r.get("reason") else "") for r in model["unchecked"])
            L += ["", "Not checked: " + md(items)]

    if model["reuse"]:
        L += ["", "## Software reuse", "", "| Requirement | State | Note |", "|---|---|---|"]
        for code in ("R1", "R2", "R3", "R4"):
            entry = model["reuse"].get(code) or {}
            L.append(f"| {code} · {md(REQUIREMENT_NAMES[code])} | {STATES.get(entry.get('status'), '—')} | "
                     f"{md(entry.get('note') or '')} |")

    if model["requirements"]:
        L += ["", "## Requirements", "", "| Requirement | State | Note |", "|---|---|---|"]
        for r in model["requirements"]:
            L.append(f"| {r['code']} · {md(REQUIREMENT_NAMES[r['code']])} | {STATES.get(r.get('status'), '—')} | "
                     f"{md(r.get('note') or '')} |")

    L += ["", "## To-dos"]
    if not model["groups"]:
        L += ["", "No findings were recorded for the results checked."]
    for title, items in model["groups"]:
        L += ["", f"### {title}"]
        for f in items:
            meta = [IMPACTS[f["impact"]], WHO[f["who"]]]
            if f.get("results"):
                meta.append(", ".join(str(x) for x in f["results"]))
            if f.get("noticed_only"):
                meta.append("noticed, not searched for")
            L += ["", f"#### {f['code']} · {md(f['title'])}", "", "*" + md(" · ".join(meta)) + "*"]
            if f.get("detail"):
                L += ["", md(f["detail"])]
            L.append("")
            for ev in f["evidence"]:
                line = f"- {md_code(ev['where'])}"
                if ev.get("quote"):
                    line += f": {md_code(ev['quote'])}"
                L.append(line)
            L += ["", f"**To-do:** {md(f['todo'])}"]

    L += ["", "## Not checked", "", "A self-check reads the code and the paper once, in your own agent. It does not cover:", ""]
    L += [f"- {md(x)}" for x in model["not_checked"]]
    L += ["", "---", "", f"> **SELF-CHECK** · {NOTICE}", ">",
          f"> Written by {md(model['agent_name'])} ({md(model['model_text'])}) with the RepoReady self-check skill "
          f"{md('v' + model['skill_version'])} (from RepoReady's public guides) on {md(model['date'])}, "
          f"at {md(model['commit_text'])}. The level is self-assessed and indicative, at most L2. Nothing was sent to RepoReady.",
          ">",
          f"> RepoReady Platform assessments, whose levels and share links count, come through institutes and journals: {OFFICIAL_URL}",
          ""]
    return "\n".join(L)


# --------------------------------------------------------------------------
# CLI


def output_stem(path: Path):
    name = path.name
    return name[: -len(".findings.json")] if name.endswith(".findings.json") else path.stem


def render_files(path, previous_path=None, use_previous=True, template_path=None, out_dir=None):
    path = Path(path)
    data = load(path)
    previous = None
    previous_name = None
    if use_previous:
        prev_path = Path(previous_path) if previous_path else find_previous(path, data)
        if prev_path is not None:
            try:
                with open(prev_path, encoding="utf-8") as fh:
                    previous = json.load(fh)
                previous_name = prev_path.name
            except (OSError, json.JSONDecodeError) as exc:
                print(f"note: could not read the previous self-check {prev_path} ({exc}); skipped", file=sys.stderr)
    template_path = Path(template_path) if template_path else Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
    template = template_path.read_text(encoding="utf-8")
    model = build(data, previous, previous_name)
    out_dir = Path(out_dir) if out_dir else path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = output_stem(path)
    html_path = out_dir / f"{stem}.html"
    md_path = out_dir / f"{stem}.md"
    html_path.write_text(render_html(model, template), encoding="utf-8")
    md_path.write_text(render_markdown(model), encoding="utf-8")
    return html_path, md_path, model


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render a RepoReady self-check findings.json into HTML and Markdown.")
    parser.add_argument("findings", help="path to <date>-<slug>.findings.json")
    parser.add_argument("--previous", help="the previous self-check's findings.json (default: the newest earlier one beside it)")
    parser.add_argument("--no-previous", action="store_true", help="do not compare with a previous self-check")
    parser.add_argument("--template", help="report template (default: ../assets/report-template.html)")
    parser.add_argument("--out-dir", help="where to write the reports (default: beside the findings)")
    args = parser.parse_args(argv)
    try:
        html_path, md_path, model = render_files(args.findings, args.previous, not args.no_previous,
                                                 args.template, args.out_dir)
    except FindingsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(model["result_line"])
    print(model["since_line"])
    print(f"wrote {html_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
