#!/usr/bin/env python3
"""
---
id: SCRIPT-0060
type: script
owner: platform-team
status: active
maturity: 1
test:
  runner: pytest
  command: "pytest -q tests/unit/test_collect_test_metrics.py"
  evidence: declared
dry_run:
  supported: true
  command_hint: "python3 scripts/collect_test_metrics.py --dry-run"
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
---
Purpose: Normalize test and coverage outputs into a single JSON payload.
"""
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def parse_junit_counts(junit_path: Path) -> Dict[str, int]:
    if not junit_path.exists():
        raise FileNotFoundError(f"JUnit file not found: {junit_path}")
    tree = ET.parse(junit_path)
    root = tree.getroot()
    suites = root.findall(".//testsuite")
    if root.tag == "testsuite":
        suites = [root]
    total = failures = errors = skipped = 0
    for suite in suites:
        total += int(suite.get("tests", 0))
        failures += int(suite.get("failures", 0))
        errors += int(suite.get("errors", 0))
        skipped += int(suite.get("skipped", 0))
    return {"total": total, "failures": failures, "errors": errors, "skipped": skipped}


def parse_coverage_xml(coverage_path: Path) -> Dict[str, float]:
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage XML not found: {coverage_path}")
    tree = ET.parse(coverage_path)
    root = tree.getroot()
    line_rate = float(root.get("line-rate", 0.0)) * 100.0
    branch_rate = float(root.get("branch-rate", 0.0)) * 100.0
    return {"lines": round(line_rate, 2), "branches": round(branch_rate, 2)}


def parse_coverage_summary_json(coverage_path: Path) -> Dict[str, float]:
    if not coverage_path.exists():
        raise FileNotFoundError(f"Coverage summary not found: {coverage_path}")
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    total = data.get("total", {})
    return {
        "lines": float(total.get("lines", {}).get("pct", 0.0)),
        "branches": float(total.get("branches", {}).get("pct", 0.0)),
        "functions": float(total.get("functions", {}).get("pct", 0.0)),
        "statements": float(total.get("statements", {}).get("pct", 0.0)),
    }


def build_framework_entry(
    framework: str,
    junit_counts: Dict[str, int],
    duration_seconds: Optional[float] = None,
    coverage: Optional[Dict[str, float]] = None,
    coverage_threshold: Optional[float] = None,
) -> Dict[str, Any]:
    total = junit_counts.get("total", 0)
    failures = junit_counts.get("failures", 0)
    errors = junit_counts.get("errors", 0)
    skipped = junit_counts.get("skipped", 0)
    passed = max(total - failures - errors - skipped, 0)
    threshold_met = (failures == 0 and errors == 0)
    if coverage_threshold is not None and coverage is not None:
        threshold_met = threshold_met and coverage.get("lines", 0.0) >= coverage_threshold
    return {
        "framework": framework,
        "total": total,
        "passed": passed,
        "failed": failures,
        "skipped": skipped,
        "duration_seconds": duration_seconds,
        "coverage": coverage,
        "threshold_met": bool(threshold_met),
    }


def build_payload(
    repo: str,
    branch: str,
    commit: str,
    ci_run_id: str,
    frameworks: list[Dict[str, Any]],
    last_run: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "repo": repo,
        "branch": branch,
        "commit": commit,
        "ci_run_id": ci_run_id,
        "last_run": last_run or datetime.now(timezone.utc).isoformat(),
        "frameworks": frameworks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect test metrics into a JSON payload.")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--branch", required=True, help="Branch name")
    parser.add_argument("--commit", required=True, help="Commit SHA")
    parser.add_argument("--ci-run-id", required=True, help="CI run ID")
    parser.add_argument("--pytest-junit", help="Path to pytest junit.xml")
    parser.add_argument("--pytest-coverage-xml", help="Path to coverage.xml")
    parser.add_argument("--bats-junit", help="Path to bats junit.xml")
    parser.add_argument("--jest-junit", help="Path to jest junit.xml")
    parser.add_argument("--jest-coverage-json", help="Path to jest coverage-summary.json")
    parser.add_argument("--pytest-threshold", type=float, default=None, help="Line coverage threshold for pytest")
    parser.add_argument("--jest-threshold", type=float, default=None, help="Line coverage threshold for jest")
    parser.add_argument("--output", help="Write JSON payload to file")
    parser.add_argument("--dry-run", action="store_true", help="Print payload to stdout only")
    args = parser.parse_args()

    frameworks = []
    if args.pytest_junit:
        junit_counts = parse_junit_counts(Path(args.pytest_junit))
        coverage = parse_coverage_xml(Path(args.pytest_coverage_xml)) if args.pytest_coverage_xml else None
        frameworks.append(
            build_framework_entry(
                "pytest",
                junit_counts,
                coverage=coverage,
                coverage_threshold=args.pytest_threshold,
            )
        )
    if args.bats_junit:
        junit_counts = parse_junit_counts(Path(args.bats_junit))
        frameworks.append(build_framework_entry("bats", junit_counts))
    if args.jest_junit:
        junit_counts = parse_junit_counts(Path(args.jest_junit))
        coverage = parse_coverage_summary_json(Path(args.jest_coverage_json)) if args.jest_coverage_json else None
        frameworks.append(
            build_framework_entry(
                "jest",
                junit_counts,
                coverage=coverage,
                coverage_threshold=args.jest_threshold,
            )
        )

    payload = build_payload(
        repo=args.repo,
        branch=args.branch,
        commit=args.commit,
        ci_run_id=args.ci_run_id,
        frameworks=frameworks,
    )

    output = json.dumps(payload, indent=2)
    if args.output and not args.dry_run:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
