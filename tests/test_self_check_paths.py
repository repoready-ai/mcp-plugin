"""The self-check's account rule, as its instructions state it (stdlib unittest).

Every self-check needs a free RepoReady account, code alone included; the
sign-in is read from the tool list before the repository or the paper is
read, and nothing of the user's work is sent.

Run from the repository root:  python3 -m unittest discover -s tests -v
"""

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "reproducibility-self-check" / "SKILL.md"
SIGNED_IN = ROOT / "skills" / "reproducibility-self-check" / "signed-in.md"
EXTRAS = ROOT / "skills" / "reproducibility-self-check" / "signed-in-extras.md"
CONNECT = ROOT / "skills" / "reproducibility-self-check" / "connect.md"
COMMAND = ROOT / "commands" / "self-check.md"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
OFFICIAL_SKILL = ROOT / "skills" / "repoready" / "SKILL.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SCRIPT = ROOT / "skills" / "reproducibility-self-check" / "scripts" / "render_report.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

GATE = "Every self-check needs a free RepoReady account, which takes one sign-in."
RECEIVES = (
    "What RepoReady receives: for code alone, the sign-in and the one `get_account` call, "
    "nothing of the work; with a paper, the same plus, when the paper has them, its public "
    "link and the public repositories it names, for materials discovery"
)
CLIENT_LINES = (
    "claude mcp add --transport http repoready https://api.repoready.ai/api/mcp",
    "codex mcp add repoready --url https://api.repoready.ai/api/mcp",
    "codex mcp login repoready",
    '{ "mcpServers": { "repoready": { "url": "https://api.repoready.ai/api/mcp" } } }',
)
# The texts the rule is read from, and the CHANGELOG entry that announces it.
RULE_TEXTS = (SKILL, SIGNED_IN, EXTRAS, CONNECT, COMMAND, README, OFFICIAL_SKILL, PLUGIN, MARKETPLACE)


def flat(path):
    """The file's text on one line: wrapped sentences and quote marks removed."""
    text = path.read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", re.sub(r"^\s*> ?", "", text, flags=re.M))


def released_entry():
    return flat(CHANGELOG).split("## 2.1.0", 1)[1].split("## 2.0.1", 1)[0]


def without_anonymisation_advice(text):
    """Drop the sentence on anonymising repositories for a double-blind journal:
    a different topic (the platform assessment's shared report), kept."""
    return re.sub(r"[^.]*anonymis[^.]*\.", " ", text)


def step_three(text):
    """Step 1, item 3 of SKILL.md, followed by connect.md, which it sends the agent to when not signed in."""
    return (text.split("**Sign-in, before anything is read.**", 1)[1].split("**Reading the paper**", 1)[0]
            + " " + flat(CONNECT))


class TheGateTest(unittest.TestCase):
    def test_the_gate_is_step_one_item_three_before_anything_is_read(self):
        text = flat(SKILL)
        self.assertIn("3. **Sign-in, before anything is read.**", text)
        self.assertIn(GATE, step_three(text))
        sends = text.index("Read `connect.md` and follow it")
        self.assertLess(text.index("Name it now and read it after item 3"), sends)
        self.assertLess(text.index("Do not open, fetch or extract the paper yet"), sends)
        self.assertLess(sends, text.index("**Reading the paper**"))
        self.assertIn("Read nothing and call nothing else until the user has answered", flat(CONNECT))

    def test_the_gate_applies_to_code_alone_too(self):
        step = step_three(flat(SKILL))
        self.assertIn("Every self-check needs a free RepoReady account, code alone included", step)
        self.assertIn("Do not clone or read the repository, do not open, fetch or extract the paper", step)
        self.assertIn("never produce a report or a to-do", step)
        self.assertNotIn("paper path", step)
        self.assertNotIn("skip this item", step)

    def test_signed_in_is_read_from_the_tool_list(self):
        step = step_three(flat(SKILL))
        self.assertIn("Look at the list; do not call a tool to find out", step)
        self.assertIn("call `get_account` once", step)
        self.assertIn("do not bring up the account or the sign-in again", step)

    def test_a_declined_sign_in_ends_the_self_check(self):
        step = step_three(flat(SKILL))
        self.assertIn("If the user declines, the self-check does not run", step)
        self.assertIn("https://repoready.ai/self-check", step)

    def test_no_offer_to_go_on_without_the_account(self):
        offer = re.compile(
            r"go on (now )?with the code alone|offers? (to go on with )?the code alone|code alone instead"
            r"|Shall I\?|On \"code alone\"|leave the paper out", re.I,
        )
        for path in (SKILL, SIGNED_IN, COMMAND, README):
            self.assertIsNone(offer.search(flat(path)), path.name)
        self.assertIsNone(offer.search(released_entry()), "CHANGELOG 2.1.0")

    def test_every_client_line_is_given_and_matches_the_readme(self):
        skill, readme = flat(CONNECT), flat(README)
        for line in CLIENT_LINES:
            self.assertIn(line, skill)
            self.assertIn(line, readme)

    def test_one_account_call_on_every_self_check(self):
        text = flat(SIGNED_IN)
        self.assertIn("Read this file at Step 1, item 3 of every self-check", text)
        self.assertIn("Call `get_account` once, at the start, before the repository or the paper is read", text)
        self.assertIn("Beyond the sign-in and the one `get_account` call, RepoReady gets only public links", text)
        self.assertIn("With a private PDF and no public link, nothing is sent beyond that call", text)
        self.assertIn("no usage ping, no counter", text)
        self.assertIn("(`request_upload_url` is not used", text)
        self.assertIn("Whenever the paper has a public DOI or link", text)
        self.assertIn("read it only after the user says yes to them", text)
        self.assertIn("Never start a check without telling the user its credits and who pays", flat(EXTRAS))


class TheScopeTest(unittest.TestCase):
    def test_no_paper_given_means_search_then_ask(self):
        step = flat(SKILL).split("**Reading the paper**", 1)[1].split("**Mode**", 1)[0]
        self.assertIn('did not say "code only", look for one first', step)
        self.assertIn("never put its name or anything from its files into a search", step)
        self.assertIn("say that no paper was found and where you looked", step)
        self.assertIn("wants the check to run on the codebase only. Wait for the answer", step)
        self.assertLess(step.index("look for one first"), step.index("From a DOI, read the open full text"))

    def test_a_partial_install_is_finished_only_on_a_yes(self):
        step = step_three(flat(SKILL))
        self.assertIn("Say yes and I will add it for you", step)
        self.assertIn("**On the user's yes, finish the install yourself:**", step)
        self.assertIn("npx skills add repoready-ai/mcp-plugin --skill repoready", step)
        self.assertIn("Change nothing else", step)
        self.assertIn("Without a yes, run nothing", step)
        self.assertIn("you cannot restart the agent or finish the browser sign-in", step)

    def test_the_install_gives_both_skills(self):
        section = flat(README).split("## Free self-check", 1)[1].split("## How a check goes", 1)[0]
        self.assertIn("the plugin brings both skills and the server", section)
        self.assertIn("--skill reproducibility-self-check npx skills add repoready-ai/mcp-plugin --skill repoready", section)

    def test_the_platform_is_offered_only_for_a_final_check_an_organization_pays_for(self):
        step = flat(SKILL).split("**Confirm what the audit will use.**", 1)[1].split("## What the account is for", 1)[0]
        offer = step.split("**Only when the goal is a final check before submission**", 1)[1].split("For code only", 1)[0]
        self.assertIn("`funding.default` in the `get_account` answer is `organization`", offer)
        self.assertIn("Never offer it for a check of work in progress or when the goal is unclear", offer)
        self.assertIn("follow the `repoready` skill from its price step", offer)
        self.assertLess(offer.index("is not among your skills"), offer.index("from its price step"))

    def test_the_audit_waits_for_one_confirmation_of_paper_code_and_data(self):
        text = flat(SKILL)
        step = text.split("**Confirm what the audit will use.**", 1)[1].split("## What the account is for", 1)[0]
        for part in ("**Paper:**", "**Codebase:**", "**Data:**", "Wait for the answer", "are never sent"):
            self.assertIn(part, step)
        self.assertLess(text.index("**Mode**"), text.index("**Confirm what the audit will use.**"))
        self.assertLess(text.index("**Confirm what the audit will use.**"), text.index("## Step 2"))
        self.assertIn("after the user has confirmed the paper", flat(SIGNED_IN))

    def test_the_skill_starts_on_reproducibility_or_submission_readiness(self):
        description = SKILL.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("reproducibility or submission readiness of a codebase, a repository or a paper", description)

    def test_integrity_is_compared_only_when_nothing_else_is_open(self):
        text = flat(SKILL)
        self.assertIn("compared only when nothing else is open", text)
        comparison = text.split("## Step 6 · The Integrity comparison", 1)[1].split("## Step 7", 1)[0]
        self.assertIn("Only when nothing else is open", comparison)
        self.assertIn("a quote of the paper and the `file:line` of the code", comparison)

    def test_a_file_missing_from_a_deposit_list_is_never_not_met(self):
        step = flat(SKILL).split("**Deposits.**", 1)[1].split("**A3, software.**", 1)[0]
        self.assertIn("**Not settled** for that result, never Not met", step)
        self.assertIn("Do not download data files", step)


class ThePromisesTest(unittest.TestCase):
    def test_no_text_says_the_self_check_needs_no_account_or_works_offline(self):
        stale = re.compile(
            r"no account|needs no server|without an account|offline|anonymous"
            r"|no telemetry|nothing leaves their machine|say nothing about accounts",
            re.I,
        )
        for path in RULE_TEXTS:
            self.assertIsNone(stale.search(without_anonymisation_advice(flat(path))), path.name)
        self.assertIsNone(stale.search(without_anonymisation_advice(released_entry())), "CHANGELOG 2.1.0")

    def test_the_rule_is_stated_everywhere_users_read(self):
        rule = re.compile(r"(Every|every|The|the) self-check needs a free RepoReady account")
        for path in (SKILL, COMMAND, README):
            text = flat(path)
            self.assertRegex(text, rule, path.name)
            self.assertIn("get_account", text, path.name)
        self.assertRegex(released_entry(), rule, "CHANGELOG 2.1.0")
        for path in (PLUGIN, MARKETPLACE):
            self.assertIn("free self-check", flat(path), path.name)
            self.assertIn("with a free account", flat(path), path.name)

    def test_what_repoready_receives_is_stated_exactly(self):
        text = flat(SKILL)
        self.assertEqual(text.count(RECEIVES), 1, "once, in the ground rules")
        ground_rules = text.split("## The words to use", 1)[0]
        self.assertIn(RECEIVES, ground_rules)
        self.assertIn("code, PDF, report or `findings.json`", ground_rules)
        self.assertIn("add no usage ping, counter or other call", ground_rules)
        for path in (COMMAND, README):
            self.assertIn("one `get_account` call, nothing of the work", flat(path), path.name)
        self.assertIn("one `get_account` call, nothing of the work", released_entry(), "CHANGELOG 2.1.0")

    def test_install_order_is_plugin_first(self):
        section = flat(README).split("## Free self-check", 1)[1].split("## How a check goes", 1)[0]
        self.assertLess(section.index("/plugin install repoready@repoready"), section.index("npx skills add"))
        self.assertLess(section.index("npx skills add"), section.index("codex mcp add repoready"))
        self.assertIn("every self-check needs the free account", section)


class TheReportTest(unittest.TestCase):
    def test_the_report_shows_no_account(self):
        spec = importlib.util.spec_from_file_location("render_report_paths", SCRIPT)
        rr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rr)
        tmp = Path(tempfile.mkdtemp())
        try:
            for fixture in FIXTURES.glob("*.findings.json"):
                shutil.copy(fixture, tmp / fixture.name)
                html_path, md_path, _ = rr.render_files(tmp / fixture.name, use_previous=False)
                for out in (html_path, md_path):
                    text = out.read_text(encoding="utf-8").lower()
                    self.assertNotIn("get_account", text, out.name)
                    self.assertNotIn("sign-in", text, out.name)
                    self.assertNotIn("signed in", text, out.name)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()


class NoLevelTest(unittest.TestCase):
    def test_the_self_check_never_gives_a_level(self):
        text = flat(SKILL)
        self.assertIn("A self-check gives no level and no score", text)
        for word in ("Level line", "Blocks L1", "Blocks L2", "Caps at L1", "Rerunnable", "result.level"):
            self.assertNotIn(word, text)
        for sev in ("**Critical**", "**Important**", "**Recommended**"):
            self.assertIn(sev, text)


class SelfCheckIsLocalTest(unittest.TestCase):
    def test_versions_read_locally_are_the_agents_to_pin(self):
        text = flat(SKILL)
        self.assertIn("listing the packages installed in the project's environment", text)
        b1 = text.split("- **B1**", 1)[1].split("- **B2**", 1)[0]
        self.assertIn("the to-do is **Your coding agent can fix this**", b1)
        self.assertIn("check that this is the environment the results were made in", b1)
        b10 = text.split("- **B10**", 1)[1].split("**B9", 1)[0]
        self.assertIn("a new seed would change the reported values", b10)

    def test_the_final_version_waits_for_submission(self):
        text = flat(SKILL)
        self.assertIn("mark their findings `\"at_submission\": true`", text)
        self.assertIn("Zenodo can reserve the DOI before the release exists", text)
        self.assertIn("In a final check they are ordinary to-dos", text)


class CodeDefectsTest(unittest.TestCase):
    def test_defects_seen_while_reading_are_reported_and_agreement_is_never_assumed(self):
        text = flat(SKILL)
        self.assertIn("you read the code that computes each result for A1 anyway", text)
        self.assertIn("a resampling that is not one, a correction step left out", text)
        self.assertIn("Never tell the user that the code matches the paper's Methods unless Step 6 compared them", text)

    def test_less_data_than_the_paper_describes_is_one_a2_finding(self):
        text = flat(SKILL)
        self.assertIn("**Less data than the paper describes.**", text)
        self.assertIn("A2 is **Not met** for those results (Critical)", text)
        self.assertIn("Record it once, under A2, not again under B9", text)

    def test_same_day_reports_get_the_time(self):
        self.assertIn("`<YYYY-MM-DD>-<HHMM>-<slug>`", flat(SKILL))


class CodeOnlyReadsTheComputationTest(unittest.TestCase):
    def test_code_only_checks_read_what_the_tool_computes(self):
        step7 = flat(SKILL).split("## Step 7", 1)[1].split("## Step 8", 1)[0]
        self.assertIn("**What the tool computes.**", step7)
        self.assertIn("**Important** when the tool gives wrong numbers without an error", step7)
        self.assertIn("it never changes R1–R4", step7)
