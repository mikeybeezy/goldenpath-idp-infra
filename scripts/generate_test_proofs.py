#!/usr/bin/env python3
"""
---
id: SCRIPT-0058
type: script
owner: platform-team
status: active
maturity: 1
test:
  runner: pytest
  command: "pytest -q tests/unit/test_generate_test_proofs.py"
  evidence: declared
dry_run:
  supported: true
  command_hint: "python3 scripts/generate_test_proofs.py --dry-run"
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: low
---
Purpose: Generate proof artifacts from pytest junit.xml results
Achievement: Closes the gap between "tests exist" and "tests passed"
Value: Enables evidence='ci' certification for scripts with passing tests
Relates-To: ADR-0146-schema-driven-script-certification, validate_scripts_tested.py
"""

import os
import sys
import json
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))
try:
    from script_metadata import parse_header
except ImportError:
    parse_header = None

SCRIPTS_DIR = Path("scripts")
PROOF_DIR = Path("test-results/proofs")
JUNIT_PATH = Path("test-results/junit.xml")


def extract_script_id(script_path: Path) -> str | None:
    """Extract script ID from metadata header."""
    try:
        content = script_path.read_text(encoding="utf-8")
        if parse_header:
            meta = parse_header(content)
            if meta:
                return meta.get("id")
        # Fallback: simple regex
        import re

        match = re.search(
            r'^id:\s*["\']?([A-Z]+-\d+|[\w_-]+)["\']?\s*$', content, re.MULTILINE
        )
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def map_tests_to_scripts() -> dict[str, str]:
    """
    Build mapping from test file paths to script IDs.
    Convention: test_foo.py tests scripts/foo.py (SCRIPT-XXXX)
    """
    mapping = {}

    if not SCRIPTS_DIR.exists():
        return mapping

    for script_path in SCRIPTS_DIR.glob("*.py"):
        if script_path.name.startswith("_") or script_path.name == "__init__.py":
            continue

        script_id = extract_script_id(script_path)
        if not script_id:
            continue

        # Expected test file: tests/unit/test_<script_name>.py
        script_base = script_path.stem
        test_patterns = [
            f"tests/unit/test_{script_base}.py",
            f"tests/test_{script_base}.py",
            f"test_{script_base}.py",
        ]

        for pattern in test_patterns:
            mapping[pattern] = script_id
            # Also map the class/module path used in junit.xml
            mapping[f"tests.unit.test_{script_base}"] = script_id
            mapping[f"test_{script_base}"] = script_id

    return mapping


def parse_junit_xml(junit_path: Path) -> dict:
    """
    Parse junit.xml and return test results by test file.
    Returns: {test_file: {"passed": int, "failed": int, "errors": int, "skipped": int, "tests": [...]}}
    """
    results = {}

    if not junit_path.exists():
        print(f"⚠️  junit.xml not found at {junit_path}")
        return results

    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()

        # Handle both <testsuites> and <testsuite> as root
        testsuites = root.findall(".//testsuite")
        if root.tag == "testsuite":
            testsuites = [root]

        for suite in testsuites:
            _suite_name = suite.get("name", "unknown")  # noqa: F841

            for testcase in suite.findall("testcase"):
                classname = testcase.get("classname", "")
                name = testcase.get("name", "")
                time_taken = float(testcase.get("time", 0))

                # Determine status
                status = "passed"
                message = None
                if testcase.find("failure") is not None:
                    status = "failed"
                    message = testcase.find("failure").get("message", "")
                elif testcase.find("error") is not None:
                    status = "error"
                    message = testcase.find("error").get("message", "")
                elif testcase.find("skipped") is not None:
                    status = "skipped"
                    message = testcase.find("skipped").get("message", "")

                # Group by classname (test module)
                if classname not in results:
                    results[classname] = {
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                        "skipped": 0,
                        "tests": [],
                    }

                results[classname]["tests"].append(
                    {
                        "name": name,
                        "status": status,
                        "time": time_taken,
                        "message": message,
                    }
                )

                if status == "passed":
                    results[classname]["passed"] += 1
                elif status == "failed":
                    results[classname]["failed"] += 1
                elif status == "error":
                    results[classname]["errors"] += 1
                elif status == "skipped":
                    results[classname]["skipped"] += 1

    except ET.ParseError as e:
        print(f"❌ Failed to parse junit.xml: {e}")

    return results


def normalize_classname(classname: str) -> str:
    """
    Normalize junit.xml classname to module path.

    junit.xml uses format: tests.unit.test_foo.TestFooClass
    We need just: tests.unit.test_foo

    Heuristic: If last component starts with uppercase, it's a class name.
    """
    parts = classname.split(".")
    if not parts:
        return classname

    # Check if last part looks like a class name (starts with uppercase)
    if parts[-1] and parts[-1][0].isupper():
        return ".".join(parts[:-1])

    return classname


def generate_proof(
    script_id: str, test_results: dict, commit_sha: str, run_id: str
) -> dict:
    """Generate a proof artifact for a script."""
    total_tests = len(test_results.get("tests", []))
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    errors = test_results.get("errors", 0)

    return {
        "schema_version": "1.0",
        "script_id": script_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit_sha": commit_sha,
        "ci_run_id": run_id,
        "test_summary": {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": test_results.get("skipped", 0),
            "pass_rate": round(passed / total_tests * 100, 2) if total_tests > 0 else 0,
        },
        "verdict": "PASS" if (failed == 0 and errors == 0 and passed > 0) else "FAIL",
        "tests": test_results.get("tests", []),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate test proof artifacts from junit.xml"
    )
    parser.add_argument(
        "--junit-path",
        type=Path,
        default=JUNIT_PATH,
        help="Path to junit.xml file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROOF_DIR,
        help="Directory for proof artifacts",
    )
    parser.add_argument(
        "--commit-sha",
        default=os.environ.get("GITHUB_SHA", "unknown"),
        help="Git commit SHA",
    )
    parser.add_argument(
        "--run-id",
        default=os.environ.get("GITHUB_RUN_ID", "local"),
        help="CI run ID",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing",
    )
    args = parser.parse_args()

    print(f"🔍 Generating test proofs from {args.junit_path}")

    # Build test -> script mapping
    test_to_script = map_tests_to_scripts()
    print(f"📋 Found {len(test_to_script)} test-to-script mappings")

    if args.dry_run:
        print("\n[DRY-RUN] Test mappings:")
        for test, script_id in sorted(set((v, k) for k, v in test_to_script.items())):
            print(f"  {test} -> {script_id}")
        return

    # Parse junit.xml
    test_results = parse_junit_xml(args.junit_path)
    if not test_results:
        print("⚠️  No test results found")
        return

    print(f"📊 Parsed {len(test_results)} test modules from junit.xml")

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate proofs for each matched script
    proofs_generated = 0
    proofs_passed = 0

    for test_module, results in test_results.items():
        # Normalize classname (strip class suffix like TestFooClass)
        normalized_module = normalize_classname(test_module)

        # Try to match test module to script
        script_id = None
        for pattern, sid in test_to_script.items():
            if pattern in normalized_module or normalized_module in pattern:
                script_id = sid
                break

        if not script_id:
            print(
                f"⚠️  No script mapping for test module: {test_module} (normalized: {normalized_module})"
            )
            continue

        # Generate proof
        proof = generate_proof(script_id, results, args.commit_sha, args.run_id)
        proof_path = args.output_dir / f"proof-{script_id}.json"

        with open(proof_path, "w") as f:
            json.dump(proof, f, indent=2)

        verdict = proof["verdict"]
        emoji = "✅" if verdict == "PASS" else "❌"
        print(
            f"{emoji} {script_id}: {verdict} ({results['passed']}/{len(results['tests'])} passed) -> {proof_path}"
        )

        proofs_generated += 1
        if verdict == "PASS":
            proofs_passed += 1

    # Summary
    print(f"\n📦 Generated {proofs_generated} proof artifacts")
    print(f"   ✅ Passed: {proofs_passed}")
    print(f"   ❌ Failed: {proofs_generated - proofs_passed}")

    if proofs_generated == 0:
        print("\n⚠️  No proofs generated. Check test-to-script mappings.")
        sys.exit(1)


if __name__ == "__main__":
    main()
