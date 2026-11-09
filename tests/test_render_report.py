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


def assert_grey_only(test, page):
    """Neutral grey only: every hex colour has (nearly) equal channels, no named hues."""
    style = page.split("<style>", 1)[1].split("</style>", 1)[0]
    for hexcode in re.findall(r"#([0-9a-fA-F]{6})\b", style):
        r, g, b = (int(hexcode[i:i + 2], 16) for i in (0, 2, 4))
        test.assertLessEqual(max(r, g, b) - min(r, g, b), 12, f"#{hexcode} is not grey")
    for rgb in re.findall(r"rgba?\(([^)]*)\)", style):
        r, g, b = (float(x) for x in rgb.split(",")[:3])
        test.assertLessEqual(max(r, g, b) - min(r, g, b), 12, f"rgb({rgb}) is not grey")
    test.assertNotRegex(style, re.compile(r"\b(red|green|orange|amber|yellow|blue|teal|purple)\b", re.I))


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
            self.assertGreaterEqual(text.count(NOTICE), 2, "header and footer notice")
            self.assertIn("SELF-CHECK", text)
            self.assertIn("https://repoready.ai/self-check?ref=report", text)
            self.assertIn("Self-assessed · L1 · Available · indicative, at most L2", text)
            self.assertIn("test-model-id", text)
            self.assertIn("self-check skill v0.1", text)
            self.assertNotIn("rubric", text)
            self.assertIn("222222222222", text)
            self.assertIn("with uncommitted changes", text)
            self.assertIn("Your coding agent can fix this", text)
            self.assertIn("Your agent can help · needs your answer", text)
            self.assertIn("Authors only", text)
            self.assertNotRegex(text, re.compile("badge", re.I))
        # previous: a1 and b8 fixed, b2 still open, b5 and c2 new
        self.assertIn("Since the last self-check (2026-11-01, commit 111111111111): 2 fixed · 1 still open · 2 new", html)
        self.assertIn("Since the last self-check (2026-11-01, commit 111111111111): 2 fixed · 1 still open · 2 new", md)
        self.assertIn("For 2 of 3 main-text results checked", html)
        # escaping
        self.assertIn("Demo study &lt;with &amp; markup&gt;", html)
        self.assertNotIn("<with & markup>", html)
        self.assertNotIn("{{", html)
        self.assertNotIn("slot:", html)
        # watermark and print stylesheet, no level colours
        self.assertIn('class="watermark"', html)
        self.assertIn("@media print", html)
        assert_grey_only(self, html)

    def test_no_previous_and_missing_model(self):
        html, md, model = self.render("2026-11-01-demo-study.findings.json")
        self.assertIn("First self-check of this project in this folder.", html)
        self.assertIn("model not stated by the agent", html)
        self.assertIn("Self-assessed · L0 · Incomplete", md)
        html2, _, _ = self.render("2026-11-06-demo-study.findings.json", use_previous=False)
        self.assertIn("First self-check", html2)

    def test_code_only_reuse(self):
        html, md, model = self.render("2026-11-06-demo-tool.findings.json")
        self.assertIn("Reuse: 3 of 4", html)
        self.assertIn("Reuse: 3 of 4", md)
        self.assertIn("no level for code alone", md)
        self.assertNotIn("Supplementary results:", md)
        data = load("2026-11-06-demo-tool.findings.json")
        for code in ("R1", "R2", "R3", "R4"):
            data["result"]["reuse"][code]["status"] = "met"
        data["findings"] = [f for f in data["findings"] if f["impact"] != "reuse"]
        p = self.tmp / "2026-11-07-demo-tool.findings.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        html, md, model = self.render(p.name)
        self.assertIn("Reusable", md)
        self.assertIn("1 fixed · 1 still open · 0 new", md)

    def assert_refused(self, data, fragment):
        p = self.tmp / "2026-11-09-bad.findings.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(rr.FindingsError) as ctx:
            rr.render_files(p)
        self.assertIn(fragment, str(ctx.exception))

    def test_refuses_levels_above_l2_and_lenient_levels(self):
        base = load("2026-11-06-demo-study.findings.json")
        d = copy.deepcopy(base)
        d["result"]["level"] = "L3"
        self.assert_refused(d, "never L3 or L4")
        d = copy.deepcopy(base)
        d["result"]["level"] = "L2"
        self.assert_refused(d, "L2 needs every B requirement met")
        d = copy.deepcopy(load("2026-11-01-demo-study.findings.json"))
        d["result"]["level"] = "L1"
        self.assert_refused(d, "means L0")
        d = copy.deepcopy(base)
        d["findings"] = []
        d["requirements"] = [{"code": c, "status": "met"} for c in ("A1", "A2", "A3", "B1", "B2", "B3")]
        d["result"]["level"] = "L2"
        self.assert_refused(d, "B4")

    def test_only_unsettled_inputs_read_not_yet_at_l1(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["result"]["level"] = "L0"
        d["requirements"][1] = {"code": "A2", "status": "not_settled", "note": "A private link."}
        p = self.tmp / "2026-11-11-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        _, md_path, _ = rr.render_files(p)
        md = md_path.read_text(encoding="utf-8")
        self.assertIn("Self-assessed · not yet at L1 · 1 to verify · indicative, at most L2", md)
        d["results"][1]["A1"] = "not_met"
        p.write_text(json.dumps(d), encoding="utf-8")
        _, md_path, _ = rr.render_files(p)
        self.assertIn("Self-assessed · L0 · Incomplete · indicative, at most L2 · 1 not settled", md_path.read_text(encoding="utf-8"))

    def test_l2_allowed_when_everything_is_met(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"] = [f for f in d["findings"] if f["impact"] not in ("blocks_l2", "caps_l1")]
        d["requirements"] = [{"code": c, "status": "met"} for c in
                             ("A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9")] + [
                                {"code": "B10", "status": "not_applicable"}]
        d["result"]["level"] = "L2"
        p = self.tmp / "2026-11-10-demo-study.findings.json"
        p.write_text(json.dumps(d), encoding="utf-8")
        html_path, md_path, model = rr.render_files(p)
        text = md_path.read_text(encoding="utf-8")
        self.assertIn("Self-assessed · L2 · Rerunnable · indicative, at most L2", text)
        self.assertIn(rr.md(rr.INTEGRITY_COMPARED), text)
        self.assertNotIn(rr.md(rr.INTEGRITY_NOT_COMPARED), text)
        self.assertIn(rr.md(rr.DEPOSITS_FROM_LISTS), text)

    def test_l2_needs_the_integrity_comparison(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"] = [f for f in d["findings"] if f["impact"] not in ("blocks_l2", "caps_l1")]
        codes = ("A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B10")
        d["result"]["level"] = "L2"
        for status in (None, "not_checked", "not_settled", "not_applicable", "not_met"):
            with self.subTest(b9=status):
                d["requirements"] = [{"code": c, "status": "met"} for c in codes]
                if status:
                    d["requirements"].append({"code": "B9", "status": status})
                self.assert_refused(d, "L2 needs B9 compared")

    def test_a_cap_cannot_stand_beside_b9_met(self):
        d = load("2026-11-06-demo-study.findings.json")
        d["findings"].append({"id": "b9-threshold", "code": "B9", "impact": "caps_l1", "title": "Stated threshold differs",
                              "evidence": [{"where": "scripts/fig1.py:3"}], "todo": "Align them.", "who": "authors_only"})
        d["requirements"] = [r for r in d["requirements"] if r["code"] != "B9"] + [{"code": "B9", "status": "met"}]
        self.assert_refused(d, "Caps at L1 finding means B9 is not met")

    def test_not_checked_says_whether_integrity_was_compared(self):
        d = load("2026-11-06-demo-study.findings.json")
        cap = {"id": "b9-threshold", "code": "B9", "impact": "caps_l1", "title": "Stated threshold differs",
               "evidence": [{"where": "scripts/fig1.py:3"}], "todo": "Align them.", "who": "authors_only"}
        d["findings"].append(cap)
        d["requirements"] = [r for r in d["requirements"] if r["code"] != "B9"] + [{"code": "B9", "status": "not_met"}]
        for noticed, expected, other in ((True, rr.INTEGRITY_NOT_COMPARED, rr.INTEGRITY_COMPARED),
                                         (False, rr.INTEGRITY_COMPARED, rr.INTEGRITY_NOT_COMPARED)):
            with self.subTest(noticed=noticed):
                cap["noticed_only"] = noticed
                p = self.tmp / "2026-11-13-demo-study.findings.json"
                p.write_text(json.dumps(d), encoding="utf-8")
                _, md_path, _ = rr.render_files(p, use_previous=False)
                text = md_path.read_text(encoding="utf-8")
                self.assertIn(rr.md(expected), text)
                self.assertNotIn(rr.md(other), text)

    def test_code_alone_keeps_the_standard_not_checked_list(self):
        _, md, _ = self.render("2026-11-06-demo-tool.findings.json")
        self.assertIn(rr.md(rr.STANDARD_NOT_CHECKED[0]), md)
        self.assertNotIn(rr.md(rr.DEPOSITS_FROM_LISTS), md)

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
            self.assertIn("self-check skill v0.1", text)
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
        self.assertIn("| Skill | RepoReady self-check v0.1 |", text)  # the renderer's own version

    def test_template_has_every_slot_and_no_colour_scale(self):
        template = (SCRIPT.parent.parent / "assets" / "report-template.html").read_text(encoding="utf-8")
        for slot in ("since_details", "facts", "results", "reuse", "requirements", "findings", "not_checked"):
            self.assertIn(f"<!-- slot:{slot} -->", template)
        self.assertEqual(template.count(NOTICE), 2 + 1)  # header, footer, printed page margin
        self.assertNotRegex(template, re.compile("badge", re.I))
        assert_grey_only(self, template)

    def test_cli(self):
        code = rr.main([str(self.tmp / "2026-11-06-demo-study.findings.json"), "--out-dir", str(self.tmp / "out")])
        self.assertEqual(code, 0)
        self.assertTrue((self.tmp / "out" / "2026-11-06-demo-study.html").exists())
        self.assertTrue((self.tmp / "out" / "2026-11-06-demo-study.md").exists())


if __name__ == "__main__":
    unittest.main()
