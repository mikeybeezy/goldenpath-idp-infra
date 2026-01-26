"""
Golden test fixtures and utilities.

Golden tests assert that generated outputs match known-good snapshots.
These are Tier 2 tests per GOV-0017.

Standard Parser CLI Contract (for golden tests):
    python scripts/<parser>.py \\
        --request <path/to/request.yaml> \\
        --out <output_dir> \\
        --format stable \\
        --dry-run

Where:
    --format stable = deterministic output (sorted keys, no timestamps)
    --dry-run = generate files only, no apply/side-effects
"""

import subprocess
import shutil
import difflib
import pytest
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).resolve().parents[2]  # repo root
FIXTURES_DIR = Path(__file__).parent / "fixtures"
INPUTS_DIR = FIXTURES_DIR / "inputs"
EXPECTED_DIR = FIXTURES_DIR / "expected"
TMP_DIR = ROOT_DIR / ".tmp" / "golden"


@pytest.fixture
def golden_fixtures():
    """Provide access to golden test fixture directories."""
    return {
        "inputs": INPUTS_DIR,
        "expected": EXPECTED_DIR,
        "tmp": TMP_DIR,
        "root": ROOT_DIR,
    }


@pytest.fixture
def load_golden():
    """Factory fixture to load golden files."""

    def _load(filename: str) -> str:
        path = EXPECTED_DIR / filename
        if not path.exists():
            pytest.fail(f"Golden file not found: {path}")
        return path.read_text()

    return _load


@pytest.fixture
def load_input():
    """Factory fixture to load input files."""

    def _load(filename: str) -> str:
        path = INPUTS_DIR / filename
        if not path.exists():
            pytest.fail(f"Input file not found: {path}")
        return path.read_text()

    return _load


@pytest.fixture
def assert_matches_golden(load_golden):
    """
    Assertion helper for golden file comparison.

    Usage:
        def test_output(assert_matches_golden):
            result = generate_something()
            assert_matches_golden(result, "expected-output.md")
    """

    def _assert(actual: str, golden_filename: str):
        expected = load_golden(golden_filename)
        # Normalize trailing whitespace for robust comparison
        actual_normalized = actual.rstrip()
        expected_normalized = expected.rstrip()
        if actual_normalized != expected_normalized:
            # Provide helpful diff information
            diff = difflib.unified_diff(
                expected_normalized.splitlines(keepends=True),
                actual_normalized.splitlines(keepends=True),
                fromfile=f"expected/{golden_filename}",
                tofile="actual",
            )
            diff_str = "".join(diff)
            pytest.fail(
                f"Output differs from golden file '{golden_filename}'.\n\n"
                f"If this change is intentional:\n"
                f"  1. Review the diff below\n"
                f"  2. Get human approval\n"
                f"  3. Update the golden file\n\n"
                f"Diff:\n{diff_str}"
            )

    return _assert


@pytest.fixture
def run_parser():
    """
    Run a parser via CLI using the standard interface.

    Standard Parser CLI Contract:
        python scripts/<parser>.py \\
            --request <path> \\
            --out <dir> \\
            --format stable \\
            --dry-run

    Usage:
        def test_parser(run_parser, golden_fixtures):
            result = run_parser(
                "scripts/secret_request_parser.py",
                golden_fixtures["inputs"] / "SECRET-0001.yaml",
                golden_fixtures["tmp"] / "secret/SECRET-0001"
            )
            assert result.returncode == 0
    """

    def _run(
        parser_script: str,
        request_file: Path,
        out_dir: Path,
        extra_args: List[str] = None,
    ) -> subprocess.CompletedProcess:
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python3",
            str(ROOT_DIR / parser_script),
            "--request",
            str(request_file),
            "--out",
            str(out_dir),
            "--format",
            "stable",
            "--dry-run",
        ]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)

    return _run


@pytest.fixture
def compare_directories():
    """
    Compare two directory trees for golden output testing.

    Usage:
        def test_output(compare_directories, golden_fixtures):
            compare_directories(
                golden_fixtures["expected"] / "secret/SECRET-0001",
                golden_fixtures["tmp"] / "secret/SECRET-0001"
            )
    """

    def _compare(expected_dir: Path, actual_dir: Path) -> None:
        assert expected_dir.exists(), f"Missing golden outputs at {expected_dir}"
        assert actual_dir.exists(), f"Missing generated outputs at {actual_dir}"

        # Compare file sets
        exp_files = sorted(
            [p.relative_to(expected_dir) for p in expected_dir.rglob("*") if p.is_file()]
        )
        act_files = sorted(
            [p.relative_to(actual_dir) for p in actual_dir.rglob("*") if p.is_file()]
        )

        if exp_files != act_files:
            missing = set(exp_files) - set(act_files)
            extra = set(act_files) - set(exp_files)
            msg = "File-set drift detected.\n"
            if missing:
                msg += f"Missing files: {sorted(missing)}\n"
            if extra:
                msg += f"Extra files: {sorted(extra)}\n"
            pytest.fail(msg)

        # Compare contents
        for rel in exp_files:
            exp = expected_dir / rel
            act = actual_dir / rel

            if exp.read_bytes() != act.read_bytes():
                exp_lines = exp.read_text().splitlines(keepends=True)
                act_lines = act.read_text().splitlines(keepends=True)
                diff = difflib.unified_diff(
                    exp_lines, act_lines, fromfile=str(exp), tofile=str(act)
                )
                diff_str = "".join(diff)
                pytest.fail(
                    f"Content drift in {rel}\n\n"
                    f"If this change is intentional:\n"
                    f"  1. Review the diff below\n"
                    f"  2. Get human approval\n"
                    f"  3. Run: cp -r {actual_dir}/* {expected_dir}/\n\n"
                    f"Diff:\n{diff_str}"
                )

    return _compare


@pytest.fixture
def clean_tmp():
    """
    Clean and provide temporary directory for golden test outputs.

    Usage:
        def test_parser(clean_tmp):
            tmp = clean_tmp("secret/SECRET-0001")
            # tmp is now a clean directory at .tmp/golden/secret/SECRET-0001
    """

    def _clean(subdir: str) -> Path:
        tmp_path = TMP_DIR / subdir
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir(parents=True, exist_ok=True)
        return tmp_path

    return _clean
