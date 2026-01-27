#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts dir to path to import the script under test
ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.append(str(SCRIPTS_DIR))

import collect_test_metrics


class TestCollectTestMetrics(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.tmp = Path(self.tmpdir.name)

    def _write(self, relpath: str, content: str) -> Path:
        path = self.tmp / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_parse_junit_counts(self):
        junit_xml = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite tests="3" failures="1" errors="0" skipped="1"></testsuite>
"""
        junit_path = self._write("junit.xml", junit_xml)
        counts = collect_test_metrics.parse_junit_counts(junit_path)
        self.assertEqual(counts["total"], 3)
        self.assertEqual(counts["failures"], 1)
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(counts["skipped"], 1)

    def test_parse_coverage_xml(self):
        coverage_xml = """<?xml version="1.0"?>
<coverage line-rate="0.65" branch-rate="0.58"></coverage>
"""
        coverage_path = self._write("coverage.xml", coverage_xml)
        coverage = collect_test_metrics.parse_coverage_xml(coverage_path)
        self.assertAlmostEqual(coverage["lines"], 65.0)
        self.assertAlmostEqual(coverage["branches"], 58.0)

    def test_parse_coverage_summary_json(self):
        coverage_json = {
            "total": {
                "lines": {"pct": 81.2},
                "branches": {"pct": 72.5},
                "functions": {"pct": 68.0},
                "statements": {"pct": 79.0},
            }
        }
        coverage_path = self._write("coverage-summary.json", json.dumps(coverage_json))
        coverage = collect_test_metrics.parse_coverage_summary_json(coverage_path)
        self.assertEqual(coverage["lines"], 81.2)
        self.assertEqual(coverage["branches"], 72.5)
        self.assertEqual(coverage["functions"], 68.0)
        self.assertEqual(coverage["statements"], 79.0)

    def test_build_framework_entry_threshold(self):
        junit_counts = {"total": 5, "failures": 0, "errors": 0, "skipped": 1}
        coverage = {"lines": 62.0}
        entry = collect_test_metrics.build_framework_entry(
            framework="pytest",
            junit_counts=junit_counts,
            duration_seconds=2.5,
            coverage=coverage,
            coverage_threshold=60.0,
        )
        self.assertEqual(entry["passed"], 4)
        self.assertTrue(entry["threshold_met"])

    def test_parse_terraform_test_json(self):
        terraform_json = "\n".join(
            [
                '{"type":"test_run","test_run":{"name":"case_one","status":"pass"}}',
                '{"type":"test_run","test_run":{"name":"case_two","status":"fail"}}',
                '{"type":"test_run","test_run":{"name":"case_three","status":"skip"}}',
            ]
        )
        terraform_path = self._write("terraform-test.jsonl", terraform_json)
        counts = collect_test_metrics.parse_terraform_test_json(terraform_path)
        self.assertEqual(counts["total"], 3)
        self.assertEqual(counts["failures"], 1)
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(counts["skipped"], 1)

    def test_parse_terraform_test_json_direct_summary_minimal(self):
        """Test fallback for minimal summary shape with skip_count."""
        terraform_json = (
            '{"test_count":13,"pass_count":13,"fail_count":0,"skip_count":0}'
        )
        terraform_path = self._write("terraform-test-summary.jsonl", terraform_json)
        counts = collect_test_metrics.parse_terraform_test_json(terraform_path)
        self.assertEqual(counts["total"], 13)
        self.assertEqual(counts["failures"], 0)
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(counts["skipped"], 0)

    def test_parse_terraform_test_json_direct_summary_with_message(self):
        """Test fallback for test_count/pass_count/fail_count shape (no type field)."""
        terraform_json = '{"@level":"info","@message":"Success! 13 passed, 0 failed.","test_count":13,"pass_count":13,"fail_count":0}'
        terraform_path = self._write("terraform-test-summary.jsonl", terraform_json)
        counts = collect_test_metrics.parse_terraform_test_json(terraform_path)
        self.assertEqual(counts["total"], 13)
        self.assertEqual(counts["failures"], 0)
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(counts["skipped"], 0)

    def test_parse_terraform_test_json_direct_summary_with_failures(self):
        """Test fallback with failures."""
        terraform_json = (
            '{"test_count":10,"pass_count":7,"fail_count":2,"skip_count":1}'
        )
        terraform_path = self._write("terraform-test-fail.jsonl", terraform_json)
        counts = collect_test_metrics.parse_terraform_test_json(terraform_path)
        self.assertEqual(counts["total"], 10)
        self.assertEqual(counts["failures"], 2)
        self.assertEqual(counts["errors"], 0)
        self.assertEqual(counts["skipped"], 1)


if __name__ == "__main__":
    unittest.main()
