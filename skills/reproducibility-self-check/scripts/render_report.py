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
the self-check's rules (a level of any kind, a severity higher than its
requirement allows, a finding without evidence or to-do, a status image or
badge Markdown, a score) and says what to fix. It makes no network call.
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
from urllib.parse import quote, urlparse

FORMAT = "repoready-self-check/1"
SKILL_VERSION = "0.1"
NOTICE = "Self-check · user generated · not a RepoReady certification"
OFFICIAL_URL = "https://repoready.ai/self-check?ref=report"
# What a self-check reads and leaves out, explained on the website.
ABOUT_URL = "https://repoready.ai/docs/self-check?ref=report#reads"
NO_MODEL = "model not stated by the agent"


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
    "paper_and_code": "Paper and code",
    "code_only": "Code only",
    "analysis_code_only": "Code only",
}
STATES = {
    "met": "Met",
    "not_met": "Not met",
    "not_settled": "Not settled",
    "not_applicable": "Not applicable",
    "not_checked": "Not checked",
}
# A self-check gives no level: each finding has a severity.
SEVERITIES = {"critical": "Critical", "important": "Important", "recommended": "Recommended"}
SEVERITY_RANK = ["critical", "important", "recommended"]
# Done once the version is final: listed apart, as reminders, until a final check.
AT_SUBMISSION_CODES = ("B2", "P2")


def max_severity(code, mode):
    """The highest severity a finding under this requirement may have."""
    if mode == "paper_and_code" and code in ("A1", "A2", "A3"):
        return "critical"
    if (mode == "paper_and_code" and code in ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10")) \
            or code in ("R1", "R2", "R3", "R4"):
        return "important"
    return "recommended"


WHO = {
    "agent_can_fix": "Your coding agent can fix this",
    "agent_needs_answer": "Your agent can help · needs your answer",
    "authors_only": "Authors only",
}
# A to-do takes the highest severity and the most demanding "who" of its findings.
WHO_RANK = ["authors_only", "agent_needs_answer", "agent_can_fix"]
WHO_SHORT = {
    "agent_can_fix": ("your coding agent can fix", "your coding agent can fix"),
    "agent_needs_answer": ("needs your answer", "need your answer"),
    "authors_only": ("authors only", "authors only"),
}
# Words a self-check report never uses in its own prose (titles, details,
# to-dos, summaries). Evidence quotes are the user's own text and are exempt.
BANNED_PROSE = [
    (re.compile(r"badge", re.I), "a README badge or status image"),
    (re.compile(r"shields\.io", re.I), "a status image"),
    (re.compile(r"!\["), "image Markdown"),
    (re.compile(r"certif(?:ied|icate|ication)", re.I), "a certification claim"),
    (re.compile(r"reproducibility score|\b\d{1,3} ?/ ?100\b|\b\d{1,3}(?:\.\d+)? ?% (?:reproducib|ready|complete)", re.I), "a score or percentage"),
    (re.compile(r"free trial|own (?:api )?key", re.I), "account or pricing words"),
    (re.compile(r"\bL[0-4]\b|\b(?:Incomplete|Available|Rerunnable) level\b"), "a level (a self-check gives none)"),
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
    if result.get("level") is not None:
        problems.append("result.level: a self-check gives no level; leave it out (each finding has a severity)")
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
        if f.get("severity") not in SEVERITIES:
            problems.append(f"{where}.severity: one of {', '.join(SEVERITIES)}")
        elif f.get("code") in REQUIREMENT_NAMES and mode in MODES:
            top = max_severity(f["code"], mode)
            if SEVERITY_RANK.index(f["severity"]) < SEVERITY_RANK.index(top):
                problems.append(f"{where}.severity: a {f['code']} finding is at most {SEVERITIES[top].lower()}"
                                + ("" if mode == "paper_and_code" else " when the code is checked without its paper"))
        if f.get("who") not in WHO:
            problems.append(f"{where}.who: one of {', '.join(WHO)}")
        if "at_submission" in f:
            if not isinstance(f["at_submission"], bool):
                problems.append(f"{where}.at_submission: true or false")
            elif f["at_submission"] and f.get("code") not in AT_SUBMISSION_CODES:
                problems.append(f"{where}.at_submission: only {' and '.join(AT_SUBMISSION_CODES)} wait for the final "
                                "version; every other finding is a to-do now")
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

    todos = data.get("todos")
    if todos is not None:
        if not isinstance(todos, list):
            problems.append("todos: a list (or leave it out: one to-do per finding)")
            todos = []
        placed = {}
        for i, td in enumerate(todos):
            where = f"todos[{i}]"
            if not isinstance(td, dict):
                problems.append(f"{where}: an object")
                continue
            if not isinstance(td.get("title"), str) or not td["title"].strip():
                problems.append(f"{where}.title: required (what to do, in plain words)")
            _check_prose(td.get("title"), f"{where}.title", problems)
            _check_text(td.get("why"), f"{where}.why", problems)
            ids = td.get("findings")
            if not isinstance(ids, list) or not ids or not all(isinstance(x, str) for x in ids):
                problems.append(f"{where}.findings: the ids of the findings it covers (at least one)")
                continue
            for fid in ids:
                if fid not in seen:
                    problems.append(f"{where}.findings: no finding has the id \"{fid}\"")
                elif fid in placed:
                    problems.append(f"{where}.findings: \"{fid}\" is already in todos[{placed[fid]}]; a finding belongs to one to-do")
                else:
                    placed[fid] = i
        for fid in sorted(seen - set(placed)):
            problems.append(f"todos: finding \"{fid}\" is in no to-do")
        later = {f.get("id") for f in findings if isinstance(f, dict) and f.get("at_submission") is True}
        for i, td in enumerate(todos):
            ids = td.get("findings") if isinstance(td, dict) else None
            if isinstance(ids, list) and 0 < len(later & set(ids)) < len(ids):
                problems.append(f"todos[{i}]: keep findings for when you submit apart from the to-dos of now")

    # Requirements and findings agree (no leniency).
    sev_by_code = {}
    for f in findings:
        if isinstance(f, dict) and f.get("severity") in SEVERITIES:
            sev_by_code.setdefault(f.get("code"), set()).add(f["severity"])
    if mode == "paper_and_code":
        for code in ("A1", "A2", "A3"):
            if req_status.get(code) in ("not_met", "not_settled") and "critical" not in sev_by_code.get(code, set()):
                problems.append(f"findings: {code} is open, so it needs a critical finding with its to-do")
        if req_status.get("B9") == "met" and any(
                isinstance(f, dict) and f.get("code") == "B9" and f.get("severity") == "important" for f in findings):
            problems.append("requirements: an important B9 finding (a contradiction) means B9 is not met")
    if isinstance(reuse, dict):
        for code in ("R1", "R2", "R3", "R4"):
            entry = reuse.get(code)
            if isinstance(entry, dict) and entry.get("status") in ("not_met", "not_settled"):
                if "important" not in sev_by_code.get(code, set()):
                    problems.append(f"findings: {code} is open, so it needs an important finding with its to-do")

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


# <YYYY-MM-DD>-<slug>.findings.json, or <YYYY-MM-DD>-<HHMM>-<slug>.findings.json for a later
# self-check on the same day (the first of a day has no time).
NAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})(?:-(\d{4}))?-(.+)\.findings\.json")


def _name_key(name):
    m = NAME_RE.fullmatch(name)
    return (m.group(1), m.group(2) or "") if m else None


def find_previous(path: Path, data):
    slug = data.get("project", {}).get("slug") or _slug_from_name(path.name)
    own = _name_key(path.name)
    if not slug or own is None:
        return None
    candidates = sorted(
        (p for p in path.parent.glob(f"*-{slug}.findings.json")
         if p.resolve() != path.resolve() and _slug_from_name(p.name) == slug
         and _name_key(p.name) is not None and _name_key(p.name) < own),
        key=lambda p: _name_key(p.name))
    return candidates[-1] if candidates else None


def _slug_from_name(name):
    m = NAME_RE.fullmatch(name)
    return m.group(3) if m else None


def _match_key(f):
    return (f.get("code"), re.sub(r"\s+", " ", str(f.get("title", "")).strip().lower()))


def compare(previous, current):
    """Return (fixed, still_open, new) lists of findings, matched by id, then by code and title."""
    # Reminders for when you submit are neither open nor fixed: leave them out on both sides,
    # also a finding the earlier check listed as a to-do that is a reminder now.
    later = [f for f in current.get("findings", []) if isinstance(f, dict) and f.get("at_submission") is True]
    later_keys = {f.get("id") for f in later} | {_match_key(f) for f in later}
    prev = [f for f in previous.get("findings", []) if isinstance(f, dict) and f.get("at_submission") is not True
            and f.get("id") not in later_keys and _match_key(f) not in later_keys]
    cur = [f for f in current.get("findings", []) if isinstance(f, dict) and f.get("at_submission") is not True]
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


def safe_url(text):
    """An http(s) URL with no spaces or quotes, else None (never a javascript: or data: link)."""
    text = str(text or "").strip()
    m = re.fullmatch(r"git@([A-Za-z0-9.-]+):(.+?)(?:\.git)?", text)
    if m:
        text = f"https://{m.group(1)}/{m.group(2)}"
    # No braces either: a link is only ever joined by concatenation, never formatted.
    return text if re.fullmatch(r"https?://[^\s<>\"'`\\{}]+", text) else None


def doi_url(text):
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", str(text or "").strip(), flags=re.I)
    return "https://doi.org/" + quote(doi, safe="/:;()._-") if re.fullmatch(r"10\.\d{4,9}/\S+", doi) else None


def repo_parts(repo):
    """The repository as linked parts: its page, the cited ref and the commit on the forge."""
    url = safe_url(repo.get("url"))
    base = re.sub(r"(?:\.git)?/*$", "", url) if url else None
    host = urlparse(base).netloc.lower() if base else ""
    path = urlparse(base).path.strip("/") if base else ""
    if host.endswith("github.com") or host.endswith("codeberg.org"):
        commit_path, tree_path = "/commit/", "/tree/"
    elif "gitlab" in host:
        commit_path, tree_path = "/-/commit/", "/-/tree/"
    elif host.endswith("bitbucket.org"):
        commit_path, tree_path = "/commits/", "/src/"
    else:
        commit_path = tree_path = None
    parts = []
    name = path if commit_path and path.count("/") >= 1 else (repo.get("url") or repo.get("name") or "repository").strip()
    parts.append(("link", name, base) if base else ("text", name))
    ref = (repo.get("ref") or "").strip() if isinstance(repo.get("ref"), str) else ""
    if ref:
        parts.append(("chip-link", ref, base + tree_path + quote(ref, safe="") if tree_path else None))
    commit = str(repo.get("commit") or "").strip()
    if commit:
        parts.append(("code-link", "commit " + commit[:12], base + commit_path + quote(commit, safe="") if commit_path else None))
    else:
        parts.append(("muted", "no commit recorded"))
    if repo.get("uncommitted_changes"):
        parts.append(("warn", "uncommitted changes"))
    if isinstance(repo.get("role"), str) and repo["role"].strip():
        parts.append(("muted", repo["role"].strip()))
    return parts


def parts_html(parts):
    out = []
    for part in parts:
        kind, text = part[0], part[1]
        url = part[2] if len(part) > 2 else None
        if kind == "link" and url:
            out.append(f'<a href="{e(url)}">{e(text)}</a>')
        elif kind == "chip-link":
            inner = f'<a href="{e(url)}">{e(text)}</a>' if url else e(text)
            out.append(f'<span class="ref">{inner}</span>')
        elif kind == "code-link":
            inner = f'<a href="{e(url)}"><code>{e(text)}</code></a>' if url else f"<code>{e(text)}</code>"
            out.append(inner)
        elif kind == "code":
            out.append(f"<code>{e(text)}</code>")
        elif kind == "warn":
            out.append(f'<span class="state not_settled">{e(text)}</span>')
        elif kind == "muted":
            out.append(f'<span class="muted">{e(text)}</span>')
        else:
            out.append(e(text))
    return " · ".join(out)


def parts_md(parts):
    out = []
    for part in parts:
        kind, text = part[0], part[1]
        url = part[2] if len(part) > 2 else None
        if url:
            label = md_code(text, in_table=True) if kind == "code-link" else md(text)
            out.append(f"[{label}](<{url}>)")
        elif kind in ("code-link", "code"):
            out.append(md_code(text, in_table=True))
        elif kind == "warn":
            out.append("**" + md(text) + "**")
        else:
            out.append(md(text))
    return " · ".join(out)


def _code_key(f):
    return CODE_ORDER.index(f["code"]) if f.get("code") in CODE_ORDER else 99


def build_todo_groups(data, findings):
    """The plain-language to-dos, each over the technical findings it covers, grouped by severity.

    Without a "todos" list every finding is its own to-do: its to-do text is the title.
    """
    by_id = {f.get("id"): f for f in findings}
    raw = data.get("todos")
    todos = []
    if isinstance(raw, list) and raw:
        for td in raw:
            items = [by_id[x] for x in td["findings"] if x in by_id]
            todos.append({"title": td["title"].strip(), "why": (td.get("why") or "").strip(), "findings": items})
    else:
        for f in findings:
            todos.append({"title": f["todo"].strip(), "why": f["title"].strip(), "findings": [f]})
    for td in todos:
        td["findings"].sort(key=_code_key)
        td["severity"] = min((f["severity"] for f in td["findings"]), key=SEVERITY_RANK.index)
        td["who"] = min((f["who"] for f in td["findings"]), key=WHO_RANK.index)
        codes, results = [], []
        for f in td["findings"]:
            if f["code"] not in codes:
                codes.append(f["code"])
            for r in f.get("results") or []:
                if r not in results:
                    results.append(r)
        order = [r.get("label") for r in data.get("results", []) if isinstance(r, dict)]
        results.sort(key=lambda r: order.index(r) if r in order else len(order))
        td["codes"], td["results"] = codes, results
        td["noticed_only"] = all(f.get("noticed_only") for f in td["findings"])
    later = [td for td in todos if all(f.get("at_submission") is True for f in td["findings"])]
    todos = [td for td in todos if td not in later]
    later.sort(key=lambda td: _code_key(td["findings"][0]))
    groups = []
    for sev in SEVERITY_RANK:
        items = [td for td in todos if td["severity"] == sev]
        if items:
            # Steps your agent can take first, then answers, then the authors'.
            items.sort(key=lambda td: (-WHO_RANK.index(td["who"]), _code_key(td["findings"][0])))
            groups.append((sev, items))
    return groups, later


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
    reuse = result.get("reuse") if isinstance(result.get("reuse"), dict) else None
    if mode == "paper_and_code":
        total = len(results)
        scope_line = (f"{len(checked)} of {total} main-text results checked, read statically in your own agent"
                      if total else "Read statically in your own agent")
    elif mode == "code_only":
        scope_line = "The code on its own, as a tool others install and use, read statically in your own agent"
    else:
        scope_line = ("Analysis code without its paper; run the self-check again with the paper "
                      "(a PDF or DOI) to check the code behind each result")

    since_line = "This is the first self-check of this project in this folder."
    if previous is not None:
        fixed, still, new = compare(previous, data)
        prev_date = previous.get("date", "")
        prev_commit = ""
        prev_repos = previous.get("project", {}).get("repositories") or []
        if prev_repos and isinstance(prev_repos[0], dict):
            prev_commit = _short_commit(prev_repos[0])
        when = (f"on {prev_date}" if prev_date else "") + (f" (commit {prev_commit})" if prev_commit else "")
        since_line = (f"Compared with the last self-check {when}".rstrip() + ": "
                      f"{len(fixed)} finding{'' if len(fixed) == 1 else 's'} fixed, "
                      f"{len(still)} still open and {len(new)} new.")

    facts = [("Date", [("text", data["date"])]),
             ("Written by", [("text", agent["name"].strip()), ("muted" if model_text == NO_MODEL else "code", model_text)]),
             ("Skill", [("link", f"RepoReady self-check v{SKILL_VERSION}", ABOUT_URL)]),
             ("Mode", [("text", MODES[mode])]),
             ("Scope", [("text", scope_line)])]
    for repo in project.get("repositories") or []:
        if isinstance(repo, dict):
            facts.append(("Repository", repo_parts(repo)))
    paper = project.get("paper")
    if isinstance(paper, dict):
        parts = []
        if paper.get("title"):
            parts.append(("text", paper["title"].strip()))
        if paper.get("doi"):
            url = doi_url(paper["doi"])
            parts.append(("link", "DOI " + paper["doi"].strip(), url) if url else ("text", "DOI " + paper["doi"].strip()))
        if paper.get("read_from"):
            parts.append(("muted", paper["read_from"].strip()))
        facts.append(("Paper", parts))
    for m in project.get("materials") or []:
        if isinstance(m, dict) and (m.get("name") or m.get("identifier")):
            parts = [("text", x.strip()) for x in (m.get("kind"), m.get("name")) if isinstance(x, str) and x.strip()]
            ident = (m.get("identifier") or "").strip()
            if ident:
                url = doi_url(ident) or safe_url(ident)
                parts.append(("link", ident, url) if url else ("text", ident))
            if isinstance(m.get("note"), str) and m["note"].strip():
                parts.append(("muted", m["note"].strip()))
            facts.append(("Material", parts))
    extra = [x.strip().rstrip(".;").strip() for x in data.get("not_checked", []) if isinstance(x, str) and x.strip()]
    if extra:
        facts.append(("Also not checked", [("text", "; ".join(extra))]))

    groups, later = build_todo_groups(data, findings)
    todo_total = sum(len(items) for _, items in groups)
    if todo_total:
        result_line = f"Self-check · {todo_total} to-do{'s' if todo_total != 1 else ''} · " + " · ".join(
            f"{len(items)} {SEVERITIES[sev].lower()}" for sev, items in groups)
    else:
        result_line = "Self-check · nothing to do for what was checked"
    if later:
        result_line += f" · {len(later)} when you submit"
    severity_counts = [(sev, len(items)) for sev, items in groups]
    by_who = {}
    for _, items in groups:
        for td in items:
            by_who[td["who"]] = by_who.get(td["who"], 0) + 1
    todo_line = ""
    if todo_total:
        parts = [f"{by_who[w]} {WHO_SHORT[w][by_who[w] != 1]}" for w in reversed(WHO_RANK) if by_who.get(w)]
        todo_line = f"{todo_total} to-do{'s' if todo_total != 1 else ''}: " + " · ".join(parts)

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
        "since_line": since_line,
        "facts": facts,
        "checked": checked,
        "unchecked": unchecked,
        "reuse": reuse,
        "requirements": requirements,
        "groups": groups,
        "later": later,
        "todo_line": todo_line,
        "severity_counts": severity_counts,
        "mode": mode,
        "previous_name": previous_name,
    }


# --------------------------------------------------------------------------
# HTML


def e(text):
    return html.escape(str(text), quote=True)


def _state(status):
    if not status:
        return "—"
    css = f"state {status}" if status in STATES else "state"
    return f'<span class="{css}">{e(STATES.get(status, status))}</span>'


def _where_html(where):
    return f"<code>{e(where)}</code>"


def _finding_html(f):
    """One technical finding inside a to-do's evidence panel: what was seen, where, and the change it suggests."""
    evidence = []
    for ev in f["evidence"]:
        quote = f'<span class="quote">{e(ev["quote"])}</span>' if ev.get("quote") else ""
        evidence.append(f"<li>{_where_html(ev['where'])}{quote}</li>")
    detail = f'<p class="f-detail">{e(f["detail"])}</p>' if f.get("detail") else ""
    extra = []
    if f.get("results"):
        extra.append(", ".join(str(x) for x in f["results"]))
    if f.get("noticed_only"):
        extra.append("noticed, not searched for")
    extra_html = f' <span class="muted">· {e(" · ".join(extra))}</span>' if extra else ""
    return (f'<div class="finding" id="f-{e(f["id"])}">'
            f'<p class="f-title"><span class="tag">{e(f["code"])}</span>{e(f["title"])}{extra_html}</p>{detail}'
            f'<ul class="ev">{"".join(evidence)}</ul>'
            f'<p class="f-fix"><span class="f-label">Suggested change</span> {e(f["todo"])}</p></div>')


def _sev_chip(sev):
    return f'<span class="sev sev-{e(sev)}">{e(SEVERITIES[sev])}</span>'


def render_html(model, template):
    slots = {}
    slots["facts"] = "\n      ".join(
        f'<tr><th scope="row">{e(k)}</th><td>{parts_html(v)}</td></tr>' for k, v in model["facts"])

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

    tech = []
    if model["reuse"]:
        rows = []
        for code in ("R1", "R2", "R3", "R4"):
            entry = model["reuse"].get(code) or {}
            rows.append(f'<tr><td><span class="tag">{code}</span>{e(REQUIREMENT_NAMES[code])}</td>'
                        f"<td>{_state(entry.get('status'))}</td><td>{e(entry.get('note') or '')}</td></tr>")
        tech.append('<details class="panel"><summary>Software reuse, R1–R4</summary><div class="scroll"><table><thead><tr>'
                    '<th>Requirement</th><th>State</th><th>Note</th></tr></thead><tbody>' + "".join(rows)
                    + "</tbody></table></div></details>")
    if model["requirements"]:
        rows = [f'<tr><td><span class="tag">{e(r["code"])}</span>{e(REQUIREMENT_NAMES[r["code"]])}</td>'
                f"<td>{_state(r.get('status'))}</td><td>{e(r.get('note') or '')}</td></tr>"
                for r in model["requirements"]]
        tech.append('<details class="panel"><summary>Every requirement and its state</summary><div class="scroll"><table>'
                    '<thead><tr><th>Requirement</th><th>State</th><th>Note</th></tr></thead><tbody>' + "".join(rows)
                    + "</tbody></table></div></details>")
    slots["reuse"] = ""
    slots["requirements"] = ("<h2>Technical details</h2>\n  " + "\n  ".join(tech)) if tech else ""

    if model["groups"] or model["later"]:
        parts = []
        if model["todo_line"]:
            parts.append(f'<p class="muted">{e(model["todo_line"])}</p>')
        for sev, items in model["groups"]:
            for td in items:
                meta = [f'<span class="who who-{e(td["who"])}">{e(WHO[td["who"]])}</span>']
                if td["results"]:
                    meta.append(f'<span class="muted">{e(", ".join(str(x) for x in td["results"]))}</span>')
                if td["noticed_only"]:
                    meta.append('<span class="muted">noticed, not searched for</span>')
                why = f'<p class="why">{e(td["why"])}</p>' if td["why"] else ""
                n = len(td["findings"])
                codes = ", ".join(td["codes"])
                details = "".join(_finding_html(f) for f in td["findings"])
                parts.append(
                    f'<article class="todo-card sev-edge-{e(sev)}">'
                    f'<div class="todo-head">{_sev_chip(sev)}<h4>{e(td["title"])}</h4></div>'
                    f'{why}<p class="meta">{" ".join(meta)}</p>'
                    f'<details class="evidence"><summary>'
                    f'<span class="closed">Show evidence</span><span class="opened">Hide evidence</span>'
                    f'<span class="count">{e(codes)} · {n} finding{"s" if n != 1 else ""}</span></summary>'
                    f'<div class="evidence-body">{details}</div></details></article>')
        if not model["groups"]:
            parts.append("<p>Nothing to do now for what was checked.</p>")
        if model["later"]:
            parts.append('<section class="later" aria-label="When you submit"><h2>When you submit</h2>'
                         '<p class="muted">Do these once the version you submit is final: every commit before then '
                         'changes it. A final self-check counts them as to-dos.</p>')
            for td in model["later"]:
                n = len(td["findings"])
                why = f'<p class="why">{e(td["why"])}</p>' if td["why"] else ""
                details = "".join(_finding_html(f) for f in td["findings"])
                parts.append(
                    f'<article class="todo-card later-card"><div class="todo-head"><span class="sev sev-later">At submission</span>'
                    f'<h4>{e(td["title"])}</h4></div>{why}'
                    f'<details class="evidence"><summary>'
                    f'<span class="closed">Show evidence</span><span class="opened">Hide evidence</span>'
                    f'<span class="count">{e(", ".join(td["codes"]))} · {n} finding{"s" if n != 1 else ""}</span></summary>'
                    f'<div class="evidence-body">{details}</div></details></article>')
            parts.append("</section>")
        slots["findings"] = "\n  ".join(parts)
    else:
        slots["findings"] = "<p>No findings were recorded for what was checked.</p>"

    # Drop the hand-filling notes from the template, then fill it in one pass,
    # so inserted text is never scanned for placeholders again. Every scalar is
    # HTML-escaped; slots hold markup built above from escaped text only.
    template = re.sub(r"<!--\s*\n\s*RepoReady self-check report template.*?-->\n", "", template, count=1, flags=re.S)
    template = re.sub(r"<!--\s*\n\s*Example markup for the slots.*?-->\n", "", template, count=1, flags=re.S)
    scalars = ("project_name", "date", "agent_name", "model_text", "skill_version",
               "summary", "since_line")
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


def _md_anchor(f):
    return "f-" + re.sub(r"[^a-z0-9-]+", "-", str(f["id"]).lower()).strip("-")


def render_markdown(model):
    L = []
    L.append(f"[**RepoReady**]({OFFICIAL_URL}) · [How the self-check works]({ABOUT_URL})")
    L.append("")
    L.append(f"# {md(model['project_name'])}")
    L.append("")
    if model["summary"]:
        L += [f"**{md(model['summary'])}**", ""]
    L += [md(model["since_line"])]
    L += ["", "## To-dos"]
    if not model["groups"]:
        L += ["", "Nothing to do now for what was checked."]
    elif model["todo_line"]:
        L += ["", md(model["todo_line"])]
    for sev, items in model["groups"]:
        for td in items:
            meta = [SEVERITIES[sev], WHO[td["who"]]]
            if td["results"]:
                meta.append(", ".join(str(x) for x in td["results"]))
            if td["noticed_only"]:
                meta.append("noticed, not searched for")
            L += ["", f"- [ ] **{md(td['title'])}**  ", "  *" + md(" · ".join(meta)) + "*"]
            if td["why"]:
                L += ["  " + md(td["why"])]
            L += ["  Evidence: " + ", ".join(f"[{f['code']} · {md(f['title'])}](#{_md_anchor(f)})" for f in td["findings"])]
    if model["later"]:
        L += ["", "## When you submit", "",
              "*Do these once the version you submit is final: every commit before then changes it. "
              "A final self-check counts them as to-dos.*"]
        for td in model["later"]:
            L += ["", f"- [ ] **{md(td['title'])}**  "]
            if td["why"]:
                L += ["  " + md(td["why"])]
            L += ["  Evidence: " + ", ".join(f"[{f['code']} · {md(f['title'])}](#{_md_anchor(f)})" for f in td["findings"])]

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

    L += ["", "## About this self-check", "", "| | |", "|---|---|"]
    L += [f"| {md(k)} | {parts_md(v)} |" for k, v in model["facts"]]

    if model["requirements"] or model["reuse"] or model["groups"] or model["later"]:
        L += ["", "## Technical details"]
    if model["reuse"]:
        L += ["", "### Software reuse, R1–R4", "", "| Requirement | State | Note |", "|---|---|---|"]
        for code in ("R1", "R2", "R3", "R4"):
            entry = model["reuse"].get(code) or {}
            L.append(f"| {code} · {md(REQUIREMENT_NAMES[code])} | {STATES.get(entry.get('status'), '—')} | "
                     f"{md(entry.get('note') or '')} |")
    if model["requirements"]:
        L += ["", "### Every requirement and its state", "",
              "| Requirement | State | Note |", "|---|---|---|"]
        for r in model["requirements"]:
            L.append(f"| {r['code']} · {md(REQUIREMENT_NAMES[r['code']])} | {STATES.get(r.get('status'), '—')} | "
                     f"{md(r.get('note') or '')} |")

    if model["groups"] or model["later"]:
        L += ["", "### The evidence behind the to-dos"]
        for td_list in [items for _, items in model["groups"]] + [model["later"]]:
            for td in td_list:
                for f in td["findings"]:
                    meta = [WHO[f["who"]]]
                    if f.get("results"):
                        meta.append(", ".join(str(x) for x in f["results"]))
                    if f.get("noticed_only"):
                        meta.append("noticed, not searched for")
                    L += ["", f'<a id="{_md_anchor(f)}"></a>', "",
                          f"#### {f['code']} · {md(f['title'])}", "", "*" + md(" · ".join(meta)) + "*"]
                    if f.get("detail"):
                        L += ["", md(f["detail"])]
                    L.append("")
                    for ev in f["evidence"]:
                        line = f"- {md_code(ev['where'])}"
                        if ev.get("quote"):
                            line += f": {md_code(ev['quote'])}"
                        L.append(line)
                    L += ["", f"Suggested change: {md(f['todo'])}"]

    L.append("")
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
