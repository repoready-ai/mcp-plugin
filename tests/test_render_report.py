"""Tests for skills/reproducibility-self-check/scripts/render_report.py (stdlib unittest).

Run from the repository root:  python3 -m unittest discover -s tests -v
"""

import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "reproducibility-self-check" / "scripts" / "render_report.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

spec = importlib.util.spec_from_file_location("render_report", SCRIPT)
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

NOTICE = "Self-check · user generated · not a RepoReady certification"


def assert_report_colours(test, page):
    """Colours for states, severities and accents; no ladder colours; no watermark."""
    test.assertNotIn("watermark", page)
    test.assertNotRegex(page, re.compile(r"indicative", re.I))
    style = page.split("<style>", 1)[1].split("</style>", 1)[0]
    for cls in (".state.met", ".state.not_met", ".state.not_settled", ".sev-critical", ".sev-important", ".sev-recommended"):
        test.assertIn(cls, style)
    # The official ladder colours (L0 orange, L1 blue, L2 green) are never used.
    for hexcode in ("#ea580c", "#175cd3", "#18794e"):
        test.assertNotIn(hexcode, style.lower())
    test.assertNotRegex(style, re.compile(r"\.line\b[^}]*color:\s*var\(--(good|warn|crit|brand)", re.S))


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for f in FIXTURES.glob("*.findings.json"):
            shutil.copy(f, self.tmp / f.name)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def render(self, name, **kw):
        html_path, md_path, model = rr.render_files(self.tmp / name, **kw)
        return html_path.read_text(encoding="utf-8"), md_path.read_text(encoding="utf-8"), model

    def test_paper_report_marks_and_since_last(self):
        html, md, model = self.render("2026-11-06-demo-study.findings.json")
        for text in (html, md):
            self.assertEqual(text.count(NOTICE), int(text is html), "no banner on screen; the printed page margin only")
            self.assertNotIn('class="notice"', text)
            self.assertNotIn("Self-check · 3 to-dos", text)  # the counts are no longer printed on top
            self.assertIn("https://repoready.ai/self-check?ref=report", text)
            self.assertIn("test-model-id", text)
            self.assertIn("RepoReady self-check v0.1", text)
            self.assertNotIn("rubric", text)
            self.assertIn("222222222222", text)
            self.assertIn("uncommitted changes", text)
            self.assertIn(rr.ABOUT_URL, text)
            self.assertNotIn("Not checked</h2>", text)
            self.assertNotIn("## Not checked", text)
            self.assertNotIn("at most L2", text)
            self.assertIn("Your coding agent can fix this", text)
            self.assertIn("Your agent can help · needs your answer", text)
            self.assertIn("Authors only", text)
            self.assertNotRegex(text, re.compile("badge", re.I))
        # previous: a1 and b8 fixed, b2 still open, b5 and c2 new
        self.assertEqual(model["result_line"], "Self-check · 3 to-dos · 2 important · 1 recommended")
        since = "Compared with the last self-check on 2026-11-01 (commit 111111111111): 2 findings fixed, 1 still open and 2 new."
        self.assertIn(since, html)
        self.assertIn(rr.md(since), md)
        tile = html.split('<section class="result"', 1)[1].split("</section>", 1)[0]
        self.assertEqual(tile.count("<p"), 2, "the tile holds the summary and the comparison only")
        self.assertIn("2 of 3 main-text results checked", html)
        # escaping
        self.assertIn("Demo study &lt;with &amp; markup&gt;", html)
        self.assertNotIn("<with & markup>", html)
        self.assertNotIn("{{", html)
        self.assertNotIn("slot:", html)
        # print stylesheet and colours, no watermark, no ladder colours
        self.assertIn("@media print", html)
        self.assertIn('<span class="state met">Met</span>', html)
        self.assertRegex(html, r'<article class="todo-card sev-edge-(critical|important|recommended)">')
        self.assertRegex(html, r'<div class="finding" id="f-')
        self.assertIn('<span class="closed">Show evidence</span><span class="opened">Hide evidence</span>', html)
        # plain to-dos first, the requirements folded under Technical details
        self.assertLess(html.index("<h2>To-dos</h2>"), html.index("<h2>Results checked</h2>"))
        self.assertIn('<details class="panel"><summary>Every requirement and its state</summary>', html)
        self.assertIn("3 to-dos: 1 your coding agent can fix · 1 needs your answer · 1 authors only", html)
        self.assertLess(md.index("## To-dos"), md.index("## Technical details"))
        assert_report_colours(self, html)

    def test_no_previous_and_missing_model(self):
        html, md, model = self.render("2026-11-01-demo-study.findings.json")
        self.assertIn("This is the first self-check of this project in this folder.", html)
        self.assertIn("model not stated by the agent", html)
        self.assertEqual(model["result_line"], "Self-check · 3 to-dos · 1 critical · 2 important")
        html2, _, _ = self.render("2026-11-06-demo-study.findings.json", use_previous=False)
        self.assertIn("first self-check of this project", html2)

    def test_code_only_reuse(self):
        html, md, model = self.render("2026-11-06-demo-tool.findings.json")
        self.assertEqual(model["result_line"], "Self-check · 2 to-dos · 1 important · 1 recommended")
        self.assertIn("### Software reuse, R1–R4", md)
        self.assertIn("<summary>Software reuse, R1–R4</summary>", html)
        self.assertNotRegex(md, r"Reuse: \d of 4|Reusable")
        data = load("2026-11-06-demo-tool.findings.json")
        for code in ("R1", "R2", "R3", "R4"):
            data["result"]["reuse"][code]["status"] = "met"
        data["findings"] = [f for f in data["findings"] if f["severity"] != "important"]
        p = self.tmp / "2026-11-07-demo-tool.findings.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        html, md, model = self.render(p.name)
        self.assertEqual(model["result_line"], "Self-check · 1 to-do · 1 recommended")
        self.assertIn("1 finding fixed, 1 still open and 0 new", md)

    def assert_refused(self, data, fragment):
        p = self.tmp / "2026-11-09-bad.findings.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(rr.FindingsError) as ctx:
            rr.render_files(p)
        self.assertIn(fragment, str(ctx.exception))

    def test_a_self_check_gives_no_level(self):
        base = load("2026-11-06-demo-study.findings.json")
        for level in ("L0", "L1", "L2", "L3"):
            d = copy.deepcopy(base)
            d["result"]["level"] = level
            self.assert_refused(d, "a self-check gives no level")
        d = copy.deepcopy(base)
        d["result"]["next"] = "L2 needs a cited version."
        self.assert_refused(d, "a level (a self-check gives none)")
        html, md, _ = self.render("2026-11-06-demo-study.findings.json")
        for text in (html, md):
            self.assertNotRegex(text.split("</style>")[-1], r"\bL[0-4]\b|Blocks|Rerunnable|Incomplete")

    def test_severity_is_capped_by_the_requirement(self):
        base = load("2026-11-06-demo-study.findings.json")
        d = copy.deepcopy(base)
        d["findings"][1]["severity"] = "critical"  # B5
        self.assert_refused(d, "a B5 finding is at most important")
        d = copy.deepcopy(base)
        d["findings"][2]["severity"] = "important"  # C2
        self.assert_refused(d, "a C2 finding is at most recommended")
        d = copy.deepcopy(base)
        d["findings"][0]["severity"] = "high"
        self.assert_refused(d, "severity: one of critical, important, recommended")
        tool = load("2026-11-06-demo-tool.findings.json")
        tool["findings"].append({"id": "b7-doc", "code": "B7", "severity": "important", "title": "A documented flag is missing",
                                 "evidence": [{"where": "README.md:4"}], "todo": "Fix it.", "who": "agent_can_fix"})
        self.assert_refused(tool, "when the code is checked without its paper")

    def test_open_requirements_need_their_findings(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["requirements"][1] = {"code": "A2", "status": "not_settled", "note": "A private link."}
        self.assert_refused(d, "A2 is open, so it needs a critical finding")
        d["findings"].append({"id": "a2-private", "code": "A2", "severity": "critical", "title": "An input sits behind a private link",
                              "evidence": [{"where": "README.md:9"}], "todo": "Share it publicly.", "who": "authors_only"})
        p = self.tmp / "2026-11-11-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        _, md_path, model = rr.render_files(p)
        md = md_path.read_text(encoding="utf-8")
        self.assertEqual(model["result_line"], "Self-check · 4 to-dos · 1 critical · 2 important · 1 recommended")
        self.assertLess(md.index("*Critical ·"), md.index("*Important ·"))
        self.assertLess(md.index("*Important ·"), md.index("*Recommended ·"))
        self.assertNotIn("### Critical", md)
        tool = load("2026-11-06-demo-tool.findings.json")
        tool["findings"] = [f for f in tool["findings"] if f["code"] != "R3"]
        self.assert_refused(tool, "R3 is open, so it needs an important finding")

    def test_a_contradiction_cannot_stand_beside_b9_met(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"].append({"id": "b9-threshold", "code": "B9", "severity": "important", "title": "Stated threshold differs",
                              "evidence": [{"where": "scripts/fig1.py:3"}], "todo": "Align them.", "who": "authors_only"})
        d["requirements"] = [r for r in d["requirements"] if r["code"] != "B9"] + [{"code": "B9", "status": "met"}]
        self.assert_refused(d, "an important B9 finding (a contradiction) means B9 is not met")

    def test_repository_paper_and_material_are_linked(self):
        html, md, model = self.render("2026-11-06-demo-study.findings.json")
        facts = html.split('<table class="facts">', 1)[1].split("</table>", 1)[0]
        self.assertIn('<a href="https://github.com/example/demo-study">example/demo-study</a>', facts)
        self.assertIn('<a href="https://github.com/example/demo-study/tree/main">main</a>', facts)
        self.assertIn('<a href="https://github.com/example/demo-study/commit/2222222222222222222222222222222222222222">'
                      '<code>commit 222222222222</code></a>', facts)
        self.assertIn('<a href="https://doi.org/10.1234/demo">DOI 10.1234/demo</a>', facts)
        self.assertIn('<a href="https://doi.org/10.5281/zenodo.0000000">', facts)
        self.assertIn("<td>Paper and code</td>", facts)
        self.assertIn("(<https://github.com/example/demo-study/commit/2222222222222222222222222222222222222222>)", md)
        # no Agent, Model, Skill or Date rows: the line under the title says them once
        self.assertNotIn('<th scope="row">Model</th>', facts)
        self.assertIn("Also not checked", facts)  # the agent's own not_checked items

    def test_code_only_modes_read_code_only(self):
        _, md, model = self.render("2026-11-06-demo-tool.findings.json")
        self.assertIn("| Mode | Code only |", md)

    def test_unsafe_links_are_not_linked(self):
        self.assertIsNone(rr.safe_url("javascript:alert(1)"))
        self.assertIsNone(rr.safe_url('https://x.org/" onclick="x'))
        self.assertEqual(rr.safe_url("git@github.com:a/b.git"), "https://github.com/a/b")
        self.assertIsNone(rr.doi_url("not a doi"))
        # a URL with format fields is refused, never formatted
        self.assertIsNone(rr.safe_url("https://github.com/{0.__class__}/x"))
        parts = rr.repo_parts({"url": "https://github.com/a/b", "ref": "v{1}", "commit": "a" * 40})
        self.assertEqual(parts[1], ("chip-link", "v{1}", "https://github.com/a/b/tree/v%7B1%7D"))
        parts = rr.repo_parts({"url": "javascript:alert(1)", "commit": "a" * 40})
        self.assertEqual(parts[0], ("text", "javascript:alert(1)"))
        self.assertNotIn("href", rr.parts_html(parts))

    def test_refuses_banned_words_and_missing_evidence(self):
        base = load("2026-11-06-demo-study.findings.json")
        for text, fragment in (("Add the RepoReady badge to the README", "badge"),
                               ("Certified reproducible", "certification"),
                               ("Reproducibility score 80/100", "score")):
            d = copy.deepcopy(base)
            d["findings"][0]["todo"] = text
            self.assert_refused(d, fragment)
        d = copy.deepcopy(base)
        d["findings"][0]["evidence"] = []
        self.assert_refused(d, "evidence")
        d = copy.deepcopy(base)
        d["findings"][1]["id"] = d["findings"][0]["id"]
        self.assert_refused(d, "used twice")
        d = copy.deepcopy(load("2026-11-06-demo-tool.findings.json"))
        d["findings"] = []
        self.assert_refused(d, "R3 is open")
        # evidence quotes are the user's own text and may contain anything
        d = copy.deepcopy(base)
        d["findings"][0]["evidence"][0]["quote"] = "[![build](https://img.shields.io/x)](y) q.put(item)"
        p = self.tmp / "2026-11-08-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        rr.render_files(p)

    def test_md_code_fence_is_longer_than_any_backtick_run(self):
        for text in ("a``b", "```", "`x`", "x ``` y `", "plain", "a|b", ""):
            span = rr.md_code(text)
            fence = re.match(r"`+", span).group(0)
            longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
            self.assertGreater(len(fence), longest, span)
            self.assertTrue(span.endswith(fence), span)
            inner = span[len(fence):len(span) - len(fence)]
            self.assertNotIn(fence, inner, span)  # the span cannot close early
            if text.startswith("`") or text.endswith("`"):
                self.assertTrue(inner.startswith(" ") and inner.endswith(" "), span)
        self.assertEqual(rr.md_code("a\nb\r# c"), "`a b # c`")
        self.assertIn("\\|", rr.md_code("a|b", in_table=True))

    def test_hostile_inputs_are_refused_or_inert(self):
        base = load("2026-11-06-demo-study.findings.json")
        # A crafted version string is refused, and the report prints the renderer's own version anyway.
        d = copy.deepcopy(base)
        d["skill_version"] = "0.1\n# Official RepoReady certification"
        self.assert_refused(d, "skill_version")
        d = copy.deepcopy(base)
        d["skill_version"] = "<b>0.1</b>"
        self.assert_refused(d, "skill_version")
        d = copy.deepcopy(base)
        d["skill_version"] = "7"  # a plain number is accepted but never printed
        p = self.tmp / "2026-11-08-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        html_path, md_path, _ = rr.render_files(p, use_previous=False)
        for text in (html_path.read_text(encoding="utf-8"), md_path.read_text(encoding="utf-8")):
            self.assertIn("RepoReady self-check v0.1", text)
            self.assertNotIn("v7", text)
        d = copy.deepcopy(base)
        d["date"] = "2026-02-30"
        self.assert_refused(d, "date")
        # A banned word in any printed field is refused: a material, the project name, the agent, not_checked.
        for path, value in ((("project", "materials", 0, "name"), "Certified reproducible dataset"),
                            (("project", "name"), "Demo study badge"),
                            (("agent", "model"), "model-x certified"),
                            (("results", 1, "note"), "![status](https://img.shields.io/x)"),
                            (("not_checked", 0), "Reproducibility score 90/100")):
            d = copy.deepcopy(base)
            target = d
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path):
                p = self.tmp / "2026-11-09-bad.findings.json"
                p.write_text(json.dumps(d), encoding="utf-8")
                with self.assertRaises(rr.FindingsError):
                    rr.render_files(p)
        # Markup, Markdown block starters, line breaks and placeholders in printed text stay inert.
        d = copy.deepcopy(base)
        d["results"][1]["note"] = "<script>alert(1)</script>"
        d["project"]["name"] = "{{summary}} <!-- slot:findings -->"
        d["result"]["summary"] = "# Heading\r\n> quote\u2028- item"
        d["findings"][0]["evidence"][0]["quote"] = "a ``` b"
        d["findings"][1]["title"] = "[link](javascript:alert(1)) & <img src=x onerror=alert(1)>"
        p = self.tmp / "2026-11-12-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        html_path, md_path, _ = rr.render_files(p, use_previous=False)
        page = html_path.read_text(encoding="utf-8")
        text = md_path.read_text(encoding="utf-8")
        self.assertNotIn("<script", page)
        self.assertNotIn("<img", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("{{summary}} &lt;!-- slot:findings --&gt;", page)  # not expanded
        prose = re.sub(r"(`+).*?\1", "", text)  # code spans are inert by construction
        self.assertNotRegex(prose, r"(?<!\\)<(script|img|!--)")  # every < outside code is escaped
        self.assertNotRegex(prose, r"(?<!\\)\[link(?<!\\)\]")
        self.assertIn("\\<script\\>", text)
        self.assertNotRegex(text, re.compile(r"^(#|>|-) ?(Heading|quote|item)", re.M))
        self.assertIn("\\# Heading", text)
        self.assertIn("\\[link\\](javascript:alert(1))", text)
        self.assertIn("````a ``` b````", text)
        self.assertEqual(rr.md("0.1"), "0\\.1")
        self.assertIn("RepoReady self-check v0.1", text)  # the renderer's own version

    def test_template_has_every_slot_and_report_colours(self):
        template = (SCRIPT.parent.parent / "assets" / "report-template.html").read_text(encoding="utf-8")
        for slot in ("facts", "results", "reuse", "requirements", "findings"):
            self.assertIn(f"<!-- slot:{slot} -->", template)
        self.assertEqual(template.count(NOTICE), 1)  # the printed page margin only
        self.assertNotRegex(template, re.compile("badge", re.I))
        assert_report_colours(self, template)

    def _with_todos(self, todos):
        data = load("2026-11-06-demo-study.findings.json")
        data["todos"] = todos
        path = self.tmp / "2026-11-07-demo-study.findings.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_todos_summarise_findings(self):
        path = self._with_todos([
            {"title": "Make the README say how each figure is made", "why": "Readers cannot find the script of a figure.",
             "findings": ["b5-no-result-map", "c2-no-lock"]},
            {"title": "Cite a fixed version of the code", "findings": ["b2-no-cited-version"]},
        ])
        html_path, md_path, model = rr.render_files(path, use_previous=False)
        html = html_path.read_text(encoding="utf-8")
        md = md_path.read_text(encoding="utf-8")
        self.assertEqual(html.count('<article class="todo-card'), 2)
        card = html.split("Make the README say how each figure is made", 1)[1].split("</article>", 1)[0]
        # the highest severity and the most demanding who of its findings
        self.assertIn('<span class="sev sev-important">Important</span>', card.split("</div>", 1)[0] + html.split(
            "Make the README say how each figure is made", 1)[0][-80:])
        self.assertIn('<span class="who who-agent_needs_answer">Your agent can help · needs your answer</span>', card)
        self.assertIn("B5, C2 · 2 findings", card)
        self.assertIn('id="f-b5-no-result-map"', card)
        self.assertIn('id="f-c2-no-lock"', card)
        self.assertIn("- [ ] **Make the README say how each figure is made**", md)
        self.assertIn("(#f-b5-no-result-map)", md)
        self.assertIn('<a id="f-b5-no-result-map"></a>', md)

    def test_todos_must_cover_each_finding_once(self):
        for todos, message in [
            ([{"title": "A", "findings": ["b5-no-result-map", "c2-no-lock"]}], "is in no to-do"),
            ([{"title": "A", "findings": ["b5-no-result-map", "c2-no-lock", "b2-no-cited-version"]},
              {"title": "B", "findings": ["b2-no-cited-version"]}], "belongs to one to-do"),
            ([{"title": "A", "findings": ["b5-no-result-map", "c2-no-lock", "b2-no-cited-version", "nope"]}], "no finding has the id"),
            ([{"title": "Get a certification", "findings": ["b5-no-result-map", "c2-no-lock", "b2-no-cited-version"]}], "certification"),
        ]:
            with self.assertRaises(rr.FindingsError) as ctx:
                rr.render_files(self._with_todos(todos), use_previous=False)
            self.assertIn(message, str(ctx.exception))

    def test_at_submission_findings_are_reminders(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"][0]["at_submission"] = True  # B2
        p = self.tmp / "2026-11-14-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        html_path, md_path, model = rr.render_files(p)
        html, md = html_path.read_text(encoding="utf-8"), md_path.read_text(encoding="utf-8")
        self.assertEqual(model["result_line"], "Self-check · 2 to-dos · 1 important · 1 recommended · 1 when you submit")
        later = html.split('<section class="later"', 1)[1]
        self.assertIn("<h2>When you submit</h2>", later)
        self.assertIn('id="f-b2-no-cited-version"', later)
        self.assertNotIn('sev-important', later)  # no severity chip on a reminder
        self.assertIn('<span class="sev sev-later">At submission</span>', later)
        self.assertNotIn('id="f-b2-no-cited-version"', html.split('<section class="later"', 1)[0])
        self.assertIn("## When you submit", md)
        # against 2026-11-06 (b2, b5, c2 open): b2 is a reminder now, so neither fixed nor open
        self.assertIn("0 findings fixed, 2 still open and 0 new", md)

    def test_at_submission_only_for_b2_and_p2_and_never_mixed(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"][1]["at_submission"] = True  # B5
        self.assert_refused(d, "only B2 and P2 wait for the final version")
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"][0]["at_submission"] = True
        d["todos"] = [{"title": "Fix the README and cite the version", "findings": ["b2-no-cited-version", "b5-no-result-map"]},
                      {"title": "Lock versions", "findings": ["c2-no-lock"]}]
        self.assert_refused(d, "keep findings for when you submit apart")

    def test_same_day_checks_keep_their_order(self):
        base = load("2026-11-06-demo-study.findings.json")
        first = self.tmp / "2026-11-15-demo-study.findings.json"
        later = self.tmp / "2026-11-15-1630-demo-study.findings.json"
        latest = self.tmp / "2026-11-15-1705-demo-study.findings.json"
        for f in (first, later, latest):
            f.write_text(json.dumps(base), encoding="utf-8")
        self.assertEqual(rr.find_previous(later, base), first)
        self.assertEqual(rr.find_previous(latest, base), later)
        self.assertEqual(rr.find_previous(first, base).name, "2026-11-06-demo-study.findings.json")
        other = self.tmp / "2026-11-15-x-demo-study.findings.json"  # another project whose slug ends the same way
        other.write_text(json.dumps(base), encoding="utf-8")
        self.assertEqual(rr.find_previous(later, base), first)

    def test_extra_not_checked_items_join_cleanly(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["not_checked"] = ["The R scripts' plotting themes.", "Supplementary Table S2;"]
        p = self.tmp / "2026-11-16-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        _, md_path, _ = rr.render_files(p, use_previous=False)
        md = md_path.read_text(encoding="utf-8")
        self.assertIn("plotting themes; Supplementary Table S2 |", md)
        self.assertNotIn(".;", md)

    def test_a_repository_without_a_remote_shows_its_name(self):
        parts = rr.repo_parts({"url": None, "name": "leaf-drought", "commit": "a" * 40})
        self.assertEqual(parts[0], ("text", "leaf-drought"))
        self.assertIn("<code>commit aaaaaaaaaaaa</code>", rr.parts_html(parts))

    def test_cli(self):
        code = rr.main([str(self.tmp / "2026-11-06-demo-study.findings.json"), "--out-dir", str(self.tmp / "out")])
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "out" / "2026-11-06-demo-study.html").exists())
        self.assertTrue((self.tmp / "out" / "2026-11-06-demo-study.md").exists())


if __name__ == "__main__":
    unittest.main()
