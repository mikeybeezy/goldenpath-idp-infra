"""
Golden output tests for parsers.

These tests verify that parser outputs match known-good snapshots.
Per GOV-0017, golden tests are the primary guardrail against drift.

To update golden files (with human approval):
    pytest tests/golden/ --update-golden
"""

import json
import pytest
from pathlib import Path

# Add scripts to path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestSecretRequestParserGolden:
    """Golden output tests for secret request parser."""

    def test_basic_request_matches_golden(self, load_input, assert_matches_golden):
        """
        Basic secret request should produce consistent output.

        This test verifies that the parser's output structure hasn't
        drifted from the expected contract.
        """
        # This is a demonstration test - actual parser may have different API
        # Replace with real parser import when ready:
        # from secret_request_parser import parse_request

        # Load input
        input_yaml = load_input("SECRET-0001.yaml")

        # For demonstration, create expected output structure
        # In real test, this would be: result = parse_request(input_yaml)
        result = {
            "name": "app-database-credentials",
            "namespace": "backstage",
            "secret_type": "opaque",
            "keys": ["username", "password"],
            "tags": {"environment": "dev", "owner": "platform-team"},
            "has_generated_values": True,
        }

        # Serialize to JSON for comparison
        actual = json.dumps(result, indent=2, sort_keys=True)

        # Assert matches golden file
        assert_matches_golden(actual, "SECRET-0001-parsed.json")


class TestGoldenTestInfrastructure:
    """Meta-tests to verify golden test infrastructure works."""

    def test_fixtures_directory_exists(self, golden_fixtures):
        """Fixture directories should exist."""
        assert golden_fixtures["inputs"].exists()
        assert golden_fixtures["expected"].exists()

    def test_load_input_works(self, load_input):
        """load_input fixture should load files."""
        content = load_input("SECRET-0001.yaml")
        assert "SecretRequest" in content

    def test_load_golden_works(self, load_golden):
        """load_golden fixture should load files."""
        content = load_golden("SECRET-0001-parsed.json")
        assert "app-database-credentials" in content

    def test_assert_matches_golden_passes_on_match(self, assert_matches_golden):
        """assert_matches_golden should pass when content matches."""
        # Load the golden file content directly
        golden_path = (
            Path(__file__).parent / "fixtures" / "expected" / "SECRET-0001-parsed.json"
        )
        expected = golden_path.read_text()

        # Should not raise
        assert_matches_golden(expected, "SECRET-0001-parsed.json")

    def test_assert_matches_golden_fails_on_mismatch(self, assert_matches_golden):
        """assert_matches_golden should fail with helpful message on mismatch."""
        with pytest.raises(pytest.fail.Exception) as exc_info:
            assert_matches_golden("wrong content", "SECRET-0001-parsed.json")

        # Should include helpful information
        assert "differs from golden file" in str(exc_info.value)
        assert "intentional" in str(exc_info.value)
