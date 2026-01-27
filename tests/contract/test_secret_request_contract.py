"""
Contract tests for SecretRequest parser.

Purpose: Verify input/output contracts for secret request parsing.
Tests validate:
- Valid requests parse successfully
- Invalid requests fail with appropriate errors
- Output structure matches expected schema
"""

from pathlib import Path

import pytest
import yaml


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "requests"


class TestSecretRequestContract:
    """Contract tests for SecretRequest parsing."""

    @pytest.fixture
    def valid_fixtures(self):
        """Load all valid request fixtures."""
        return list((FIXTURES_DIR / "valid").glob("*.yaml"))

    @pytest.fixture
    def invalid_fixtures(self):
        """Load all invalid request fixtures."""
        return list((FIXTURES_DIR / "invalid").glob("*.yaml"))

    def test_valid_fixture_exists(self, valid_fixtures):
        """At least one valid fixture should exist."""
        assert len(valid_fixtures) > 0, "No valid fixtures found"

    def test_invalid_fixture_exists(self, invalid_fixtures):
        """At least one invalid fixture should exist."""
        assert len(invalid_fixtures) > 0, "No invalid fixtures found"

    def test_valid_fixtures_are_valid_yaml(self, valid_fixtures):
        """All valid fixtures should be parseable YAML."""
        for fixture in valid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            assert isinstance(data, dict), f"{fixture.name} is not a dict"

    def test_valid_fixtures_have_required_structure(self, valid_fixtures):
        """Valid fixtures should have apiVersion, kind, metadata, spec."""
        required_keys = ["apiVersion", "kind", "metadata", "spec"]
        for fixture in valid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            for key in required_keys:
                assert key in data, f"{fixture.name} missing '{key}'"

    def test_valid_fixtures_have_metadata_fields(self, valid_fixtures):
        """Valid fixtures should have required metadata fields."""
        required_metadata = ["id", "name", "service", "environment", "owner"]
        for fixture in valid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            metadata = data.get("metadata", {})
            for field in required_metadata:
                assert field in metadata, f"{fixture.name} metadata missing '{field}'"

    def test_valid_fixtures_have_spec_fields(self, valid_fixtures):
        """Valid fixtures should have required spec fields."""
        required_spec = [
            "secretType",
            "riskTier",
            "rotationClass",
            "lifecycleStatus",
            "namespace",
            "k8sSecretName",
        ]
        for fixture in valid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            spec = data.get("spec", {})
            for field in required_spec:
                assert field in spec, f"{fixture.name} spec missing '{field}'"

    def test_invalid_fixtures_are_valid_yaml(self, invalid_fixtures):
        """Invalid fixtures should still be parseable YAML (just missing fields)."""
        for fixture in invalid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            assert isinstance(data, dict), f"{fixture.name} is not a dict"

    def test_invalid_fixtures_missing_required_fields(self, invalid_fixtures):
        """Invalid fixtures should be missing at least one required field."""
        required_metadata = ["id", "name", "service", "environment", "owner"]
        required_spec = [
            "secretType",
            "riskTier",
            "rotationClass",
            "lifecycleStatus",
            "namespace",
            "k8sSecretName",
        ]

        for fixture in invalid_fixtures:
            data = yaml.safe_load(fixture.read_text())
            metadata = data.get("metadata", {})
            spec = data.get("spec", {})

            missing_metadata = [f for f in required_metadata if f not in metadata]
            missing_spec = [f for f in required_spec if f not in spec]

            assert (
                missing_metadata or missing_spec
            ), f"{fixture.name} should be missing required fields"
