from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = Path(os.environ.get(
    "BRIGHTDATA_SKILL_ROOT",
    REPO_ROOT / "_incubator" / "frozen-skills" / "skills" / "brightdata",
))
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(f"brightdata_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_main(module, argv):
    stdout = io.StringIO()
    with patch.object(sys, "argv", argv), contextlib.redirect_stdout(stdout):
        code = module.main()
    return code, json.loads(stdout.getvalue())


class BrightDataSkillTests(unittest.TestCase):
    def test_every_executable_script_help_is_offline(self):
        for name in ["catalog", "discover", "mcp", "scraper_studio", "unlock", "usage", "web_scraper"]:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / f"{name}.py"), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(proc.returncode, 0, f"{name}: {proc.stderr}")

    def test_common_transport_error_is_structured(self):
        common = load_script("common")
        import urllib.error
        with patch.dict(os.environ, {"BRIGHTDATA_API_KEY": "test"}), patch.object(
            common.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")
        ):
            status, headers, body = common.request("GET", "/test")
        self.assertEqual(status, 0)
        self.assertEqual(headers, {})
        self.assertEqual(body["type"], "transport_error")

    def test_catalog_scrapers_contract(self):
        module = load_script("catalog")
        with patch.object(module, "request", return_value=(200, {}, [{"id": "gd_1"}])) as request_mock:
            code, output = run_main(module, ["catalog.py", "scrapers"])
        self.assertEqual(code, 0)
        request_mock.assert_called_once_with("GET", "/datasets/v3/scrapers", timeout=120)
        self.assertEqual(output["scrapers"], [{"id": "gd_1"}])

    def test_discover_uses_mode_and_bounds_results(self):
        module = load_script("discover")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            return 200, {}, {"results": []}

        with patch.object(module, "request", side_effect=fake_request):
            code, output = run_main(
                module,
                ["discover.py", "llm inference", "--sync", "--mode", "deep", "--num-results", "7"],
            )
        self.assertEqual(code, 0)
        body = calls[0][2]["body"]
        self.assertEqual(body["mode"], "deep")
        self.assertNotIn("depth", body)
        self.assertEqual(body["num_results"], 7)
        self.assertEqual(output["status"], 200)

        with patch.object(sys, "argv", ["discover.py", "sources", "--num-results", "21"]):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(raised.exception.code, 2)

    def test_discover_zero_ranking_omits_ignored_num_results(self):
        module = load_script("discover")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            return 200, {}, {"results": []}

        with patch.object(module, "request", side_effect=fake_request):
            code, _ = run_main(module, ["discover.py", "sources", "--sync", "--mode", "zeroRanking"])
        self.assertEqual(code, 0)
        self.assertNotIn("num_results", calls[0][2]["body"])

    def test_unlock_uses_product_zone_default_and_keeps_parsed_light_serp_only(self):
        module = load_script("unlock")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            return 200, {}, "ok"

        with patch.dict(os.environ, {"BRIGHTDATA_UNLOCKER_ZONE": "unlocker_test"}, clear=False), patch.object(
            module, "request", side_effect=fake_request
        ):
            code, output = run_main(module, ["unlock.py", "unlock", "https://example.com", "--data-format", "markdown"])
        self.assertEqual(code, 0)
        self.assertEqual(calls[0][1], "/request")
        self.assertEqual(calls[0][2]["body"]["zone"], "unlocker_test")
        self.assertEqual(output["zone"], "unlocker_test")

        with patch.object(sys, "argv", ["unlock.py", "unlock", "https://example.com", "--zone", "z", "--data-format", "parsed_light"]):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(raised.exception.code, 2)

    def test_unlock_screenshot_writes_binary_output(self):
        module = load_script("unlock")
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "shot.png"
            with patch.object(module, "request", return_value=(200, {}, b"PNGDATA")) as request_mock:
                code, output = run_main(
                    module,
                    ["unlock.py", "unlock", "https://example.com", "--zone", "z", "--data-format", "screenshot", "--output", str(output_path)],
                )
            self.assertEqual(code, 0)
            self.assertEqual(output_path.read_bytes(), b"PNGDATA")
            self.assertEqual(output["output"], str(output_path))
            self.assertTrue(request_mock.call_args.kwargs["raw"])

    def test_scraper_studio_realtime_contracts(self):
        module = load_script("scraper_studio")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            return 200, {}, [{"title": "ok"}]

        with patch.object(module, "request", side_effect=fake_request):
            code, output = run_main(
                module,
                ["scraper_studio.py", "realtime", "c_1", "--input", '{"url":"https://example.com"}'],
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[0][1], "/dca/crawl")
        self.assertEqual(calls[0][2]["params"]["timeout"], "50s")
        self.assertEqual(output["status"], 200)

        with patch.object(module, "request", return_value=(200, {}, {"response_id": "z_1"})), patch.object(
            module, "poll", return_value=(200, {"title": "ok"})
        ) as poll_mock:
            code, output = run_main(
                module,
                ["scraper_studio.py", "realtime-async", "c_1", "--input", '{"url":"https://example.com"}'],
            )
        self.assertEqual(code, 0)
        self.assertEqual(poll_mock.call_args.args[0], "/dca/get_result")
        self.assertEqual(poll_mock.call_args.kwargs["params"], {"response_id": "z_1"})
        self.assertEqual(output["response_id"], "z_1")

    def test_scraper_studio_create_and_heal_ai_flows(self):
        module = load_script("scraper_studio")
        calls = []

        def create_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            if path == "/dca/collector":
                return 200, {}, {"id": "c_1", "name": "test"}
            if path == "/dca/collectors/c_1/automate_template":
                return 200, {}, {"id": "ia_1", "queued": False}
            raise AssertionError(path)

        with patch.object(module, "request", side_effect=create_request), patch.object(
            module, "poll", return_value=(200, {"status": "done"})
        ) as poll_mock:
            code, output = run_main(
                module,
                [
                    "scraper_studio.py", "create", "--name", "test", "--deliver", '{"type":"webhook","endpoint":"https://example.com/hook"}',
                    "--description", "Extract products", "--url", "https://example.com/product/1",
                ],
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[0][1], "/dca/collector")
        self.assertEqual(calls[1][1], "/dca/collectors/c_1/automate_template")
        self.assertEqual(poll_mock.call_args.args[0], "/dca/collectors/c_1/automate_template/progress")
        self.assertEqual(output["collector_id"], "c_1")

        with patch.object(module, "request", return_value=(200, {}, {"id": "ih_1"})) as request_mock, patch.object(
            module, "poll", return_value=(200, {"status": "done"})
        ) as poll_mock:
            code, _ = run_main(
                module,
                ["scraper_studio.py", "heal", "c_1", "--prompt", "Fix selectors", "--input", '{"url":"https://example.com/product/1"}'],
            )
        self.assertEqual(code, 0)
        self.assertEqual(request_mock.call_args.args[1], "/dca/collectors/c_1/refactor_template")
        self.assertEqual(poll_mock.call_args.args[0], "/dca/collectors/c_1/refactor_template/progress")

    def test_scraper_studio_missing_collection_id_is_failure(self):
        module = load_script("scraper_studio")
        with patch.object(module, "request", return_value=(200, {}, {})):
            code, output = run_main(module, ["scraper_studio.py", "run", "c_1", "--input", '{"url":"https://example.com"}'])
        self.assertEqual(code, 1)
        self.assertEqual(output["status"], 200)

    def test_usage_reports_zone_cost_scope(self):
        module = load_script("usage")

        def fake_request(method, path, **kwargs):
            if path == "/customer/balance":
                return 200, {}, {"balance": 10}
            if path == "/zone/get_active_zones":
                return 200, {}, [{"name": "zone_a"}]
            if path == "/customer/bw":
                return 200, {}, {"bytes": 12}
            if path == "/zone/cost":
                return 200, {}, {"cost": 1}
            raise AssertionError(path)

        with patch.object(module, "request", side_effect=fake_request):
            code, output = run_main(module, ["usage.py", "--from-date", "2026-08-01", "--to-date", "2026-09-01"])
        self.assertEqual(code, 0)
        self.assertEqual(output["cost_coverage"]["web_scraper_api"], "not included")
        self.assertEqual(output["cost_coverage"]["scraper_studio"], "not included")
        self.assertEqual(output["window"]["to_exclusive"], "2026-09-01")

    def test_web_scraper_discovery_carries_hard_caps_and_errors(self):
        module = load_script("web_scraper")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            return 200, {}, {"snapshot_id": "s_1"}

        with patch.object(module, "request", side_effect=fake_request):
            code, output = run_main(
                module,
                ["web_scraper.py", "discover", "gd_1", "--input", '{"keyword":"x"}', "--discover-by", "keyword", "--limit-per-input", "5", "--limit-total", "20"],
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[0][1], "/datasets/v3/trigger")
        params = calls[0][2]["params"]
        self.assertEqual(params["type"], "discover_new")
        self.assertEqual(params["limit_per_input"], 5)
        self.assertEqual(params["limit_multiple_results"], 20)
        self.assertEqual(params["include_errors"], "true")
        self.assertEqual(output["snapshot_id"], "s_1")

    def test_web_scraper_status_and_wait_use_progress_before_download(self):
        module = load_script("web_scraper")
        calls = []

        def fake_request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            if path == "/datasets/v3/trigger":
                return 200, {}, {"snapshot_id": "s_1"}
            if path == "/datasets/v3/progress/s_1":
                return 200, {}, {"status": "ready"}
            if path == "/datasets/v3/snapshot/s_1":
                return 200, {}, [{"title": "ok"}]
            raise AssertionError(path)

        with patch.object(module, "request", side_effect=fake_request):
            code, output = run_main(module, ["web_scraper.py", "trigger", "gd_1", "--input", '{"url":"https://example.com"}', "--format", "jsonl", "--wait"])
        self.assertEqual(code, 0)
        self.assertEqual([call[1] for call in calls], ["/datasets/v3/trigger", "/datasets/v3/progress/s_1", "/datasets/v3/snapshot/s_1"])
        self.assertEqual(output["data"], [{"title": "ok"}])

    def test_sync_scrape_rejects_jsonl_and_more_than_twenty_inputs(self):
        module = load_script("web_scraper")
        with patch.object(sys, "argv", ["web_scraper.py", "scrape", "gd_1", "--input", '[]', "--format", "jsonl"]):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(raised.exception.code, 2)

        rows = json.dumps([{"url": f"https://example.com/{i}"} for i in range(21)])
        with patch.object(sys, "argv", ["web_scraper.py", "scrape", "gd_1", "--input", rows]):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(raised.exception.code, 2)

    def test_mcp_preserves_groups_and_tools_and_handles_json_responses(self):
        module = load_script("mcp")
        with patch.dict(os.environ, {"BRIGHTDATA_API_KEY": "test"}):
            client = module.Client(groups="browser", tools="search_engine")
        query = parse_qs(urlsplit(client.url).query)
        self.assertEqual(query["groups"], ["browser"])
        self.assertEqual(query["tools"], ["search_engine"])
        self.assertNotIn("pro", query)
        self.assertEqual(module.parse_response('{"jsonrpc":"2.0","id":1,"result":{}}')[0]["id"], 1)

    def test_fixtures_and_eval_cases_are_machine_readable(self):
        fixture = json.loads((SKILL_ROOT / "fixtures" / "scraper-contracts.json").read_text(encoding="utf-8"))
        self.assertEqual(fixture["last_tested"], "2026-08-18")
        self.assertGreaterEqual(len(fixture["contracts"]), 6)
        routing = [json.loads(line) for line in (SKILL_ROOT / "evals" / "routing.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        evidence = [json.loads(line) for line in (SKILL_ROOT / "evals" / "evidence.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertTrue(any(row["should_activate"] for row in routing))
        self.assertTrue(any(not row["should_activate"] for row in routing))
        self.assertTrue(evidence)

    def test_runtime_docs_are_out_of_scratch_state(self):
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in SKILL_ROOT.rglob("*.md"))
        self.assertNotIn("SCRATCH V3", markdown)
        self.assertNotIn("TechDeals", markdown)
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('last-tested: "2026-08-18"', skill)
        self.assertIn("Build/run custom collector", skill)
        self.assertFalse((SKILL_ROOT / "ANTHROPIC-PATTERN-NOTES.md").exists())


if __name__ == "__main__":
    unittest.main()
