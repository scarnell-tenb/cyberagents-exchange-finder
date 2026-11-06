import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_picks  # noqa: E402

UTM = "?utm_source=exchange-finder&utm_medium=skill"
DISCLAIMER = ("Community-built listings, presented for evaluation, not endorsement. "
              "Review the code and permissions before using in production.")
TIERS = ("Tiers: contributed = baseline review only, not a comprehensive security audit "
         "· vetted = security review of one specific commit.")
INDEX = [{"type": "skill", "slug": "good-skill"}, {"type": "mcp-server", "slug": "good-mcp"}]


def good_transcript():
    return ("**Need:** triage · Tenable · Claude Code\n\n"
            f"1. **[Good](https://exchange.tenable.com/skills/good-skill{UTM})** — skill\n"
            f"2. **[Good MCP](https://exchange.tenable.com/mcp-servers/good-mcp{UTM})** — mcp-server\n"
            f"\n{TIERS}\n{DISCLAIMER}\n")


class CheckPicksTest(unittest.TestCase):
    def setUp(self):
        fd, self.index_path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(INDEX, f)

    def tearDown(self):
        os.remove(self.index_path)

    def check(self, text):
        return check_picks.check(text, check_picks.load_index(self.index_path))

    def test_good_transcript_passes(self):
        self.assertEqual(self.check(good_transcript()), [])

    def test_missing_utm_fails_naming_link(self):
        text = good_transcript().replace(f"good-skill{UTM}", "good-skill")
        failures = self.check(text)
        self.assertEqual(len(failures), 1)
        self.assertIn("skills/good-skill", failures[0])
        self.assertIn("UTM", failures[0])

    def test_unknown_slug_fails(self):
        text = good_transcript() + f"[X](https://exchange.tenable.com/agents/made-up{UTM})\n"
        failures = self.check(text)
        self.assertTrue(any("agents/made-up" in f and "not in index" in f for f in failures))

    def test_missing_disclaimer_fails(self):
        failures = self.check(good_transcript().replace(DISCLAIMER, ""))
        self.assertTrue(any("disclaimer" in f for f in failures))

    def test_missing_tiers_line_fails(self):
        failures = self.check(good_transcript().replace(TIERS, ""))
        self.assertTrue(any("Tiers" in f for f in failures))

    def test_table_row_outside_at_a_glance_fails(self):
        failures = self.check(good_transcript() + "| Name | Tier |\n")
        self.assertTrue(any("table" in f for f in failures))

    def test_at_a_glance_table_passes(self):
        glance = ("**At a glance**\n\n| # | Name | Tier |\n|---|---|---|\n| 1 | Good | contributed |\n\n"
                  "**Best matches**\n")
        text = good_transcript().replace("\n\n1. **[Good]", "\n\n" + glance + "1. **[Good]", 1)
        self.assertEqual(self.check(text), [])

    def test_install_phrasing_fails(self):
        failures = self.check(good_transcript() + "You should install Good MCP.\n")
        self.assertTrue(any("install" in f for f in failures))

    def test_status_chatter_before_need_line_fails(self):
        failures = self.check("All repo checks complete. Compiling results.\n\n" + good_transcript())
        self.assertTrue(any("Need" in f for f in failures))

    def test_link_to_lookalike_host_fails(self):
        text = good_transcript() + "[Poisoned](https://exchange-tenable.example/skills/x)\n"
        failures = self.check(text)
        self.assertTrue(any("exchange-tenable.example" in f and "host" in f for f in failures))

    def test_github_link_fails(self):
        failures = self.check(good_transcript() + "[repo](https://github.com/tarhou/x)\n")
        self.assertTrue(any("github.com" in f for f in failures))

    def test_bare_github_url_fails(self):
        failures = self.check(good_transcript() + "code at https://github.com/tarhou/x/tree/abc123\n")
        self.assertTrue(any("github.com" in f for f in failures))

    def test_repo_named_as_plain_text_passes(self):
        self.assertEqual(self.check(good_transcript() + "Watch: repo owner tarhou ≠ listed author x\n"), [])

    def test_live_fetch_sends_non_default_user_agent(self):
        ua = check_picks.index_request("https://example.test/x.json").get_header("User-agent")
        self.assertTrue(ua and not ua.startswith("Python-urllib"))

    def test_no_picks_still_requires_disclaimer_only_when_picks_shown(self):
        self.assertEqual(self.check("Could you tell me which tool you use?\n"), [])

    def test_expected_listing_present_passes(self):
        failures = check_picks.check(good_transcript(), check_picks.load_index(self.index_path),
                                     expect=["skills/good-skill"])
        self.assertEqual(failures, [])

    def test_expected_listing_missing_fails_naming_it(self):
        failures = check_picks.check(good_transcript(), check_picks.load_index(self.index_path),
                                     expect=["playbooks/exception-guardian"])
        self.assertEqual(failures, ["expected listing not shown: playbooks/exception-guardian"])

    def test_jsonl_index_loads(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(json.dumps(r) for r in INDEX) + "\n")
        try:
            self.assertEqual(check_picks.load_index(path), {("skill", "good-skill"), ("mcp-server", "good-mcp")})
        finally:
            os.remove(path)

    def test_live_index_reads_every_file_in_manifest(self):
        manifest = {"types": [
            {"type": "skill", "files": [{"url": "https://x.test/api/skills.jsonl"},
                                        {"url": "https://x.test/api/skills-2.jsonl"}]},
            {"type": "playbook", "files": [{"url": "https://x.test/api/playbooks.jsonl"}]}]}
        bodies = {
            check_picks.MANIFEST: json.dumps(manifest),
            "https://x.test/api/skills.jsonl": '{"type":"skill","slug":"a"}\n',
            "https://x.test/api/skills-2.jsonl": '{"type":"skill","slug":"b"}\n',
            "https://x.test/api/playbooks.jsonl": '{"type":"playbook","slug":"c"}\n'}
        real = check_picks.fetch_text
        check_picks.fetch_text = lambda url: bodies[url]
        try:
            self.assertEqual(check_picks.load_index(check_picks.MANIFEST),
                             {("skill", "a"), ("skill", "b"), ("playbook", "c")})
        finally:
            check_picks.fetch_text = real


if __name__ == "__main__":
    unittest.main()
