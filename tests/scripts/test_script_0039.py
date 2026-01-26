"""
Tests for scripts/validate_enums.py (SCRIPT-0039)
Enhanced Enum Consistency Validator

Test Categories:
- YAML loading and parsing
- Dot-path navigation
- Frontmatter parsing
- Value validation against enum lists
- File scanning (YAML and Markdown)
- CLI behavior
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List

import yaml

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validate_enums import (
    load_yaml,
    get_dot,
    find_frontmatter,
    validate_value,
    scan_file,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def valid_enums():
    """Valid enums configuration matching schemas/metadata/enums.yaml structure."""
    return {
        "domains": ["platform-core", "application", "infrastructure"],
        "owners": ["platform-team", "app-team-a", "security-team"],
        "artifact_type": ["adr", "governance", "runbook", "documentation"],
        "lifecycle": ["active", "deprecated", "draft", "archived"],
        "adr_categories": ["security", "infrastructure", "observability"],
        "observability_tier": ["bronze", "silver", "gold"],
        "risk_profile_production_impact": ["low", "medium", "high"],
        "risk_profile_security_risk": ["none", "low", "medium", "high"],
        "risk_profile_coupling_risk": ["low", "medium", "high"],
        "rollback_strategy": ["git-revert", "terraform-destroy", "manual"],
    }


@pytest.fixture
def enums_file(valid_enums, tmp_path):
    """Create a temporary enums file."""
    enums_path = tmp_path / "enums.yaml"
    enums_path.write_text(yaml.safe_dump(valid_enums))
    return enums_path


# ============================================================================
# Test: load_yaml
# ============================================================================

class TestLoadYaml:
    def test_loads_valid_yaml(self, tmp_path):
        """Should load a valid YAML file."""
        path = tmp_path / "test.yaml"
        path.write_text("key: value\nnested:\n  a: 1")
        result = load_yaml(str(path))
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_returns_none_for_invalid_yaml(self, tmp_path, capsys):
        """Should return None and print error for invalid YAML."""
        path = tmp_path / "invalid.yaml"
        path.write_text("key: [\nunbalanced")
        result = load_yaml(str(path))
        assert result is None
        captured = capsys.readouterr()
        assert "Error loading YAML" in captured.out

    def test_returns_none_for_missing_file(self, tmp_path, capsys):
        """Should return None for non-existent file."""
        result = load_yaml(str(tmp_path / "missing.yaml"))
        assert result is None


# ============================================================================
# Test: get_dot
# ============================================================================

class TestGetDot:
    def test_simple_path(self):
        """Should retrieve simple top-level key."""
        d = {"key": "value"}
        assert get_dot(d, "key") == "value"

    def test_nested_path(self):
        """Should retrieve nested value with dot notation."""
        d = {"level1": {"level2": {"level3": "deep"}}}
        assert get_dot(d, "level1.level2.level3") == "deep"

    def test_returns_none_for_missing_key(self):
        """Should return None for missing path."""
        d = {"key": "value"}
        assert get_dot(d, "missing") is None
        assert get_dot(d, "key.nested") is None

    def test_returns_none_for_non_dict(self):
        """Should return None when traversing non-dict."""
        assert get_dot("string", "key") is None
        assert get_dot(None, "key") is None
        assert get_dot(123, "key") is None

    def test_handles_intermediate_missing_key(self):
        """Should return None when intermediate key is missing."""
        d = {"a": {"b": 1}}
        assert get_dot(d, "a.c.d") is None


# ============================================================================
# Test: find_frontmatter
# ============================================================================

class TestFindFrontmatter:
    def test_parses_valid_frontmatter(self):
        """Should parse valid YAML frontmatter."""
        md = """---
id: DOC-001
owner: platform-team
status: active
---

# Document Title

Content here.
"""
        fm = find_frontmatter(md)
        assert fm is not None
        assert fm["id"] == "DOC-001"
        assert fm["owner"] == "platform-team"

    def test_returns_none_for_no_frontmatter(self):
        """Should return None when no frontmatter present."""
        md = "# Just a title\n\nNo frontmatter here."
        assert find_frontmatter(md) is None

    def test_returns_none_for_missing_closing_delimiter(self):
        """Should return None when closing --- is missing."""
        md = """---
id: incomplete
No closing delimiter
"""
        # The function searches up to 2000 lines
        assert find_frontmatter(md) is None

    def test_handles_empty_frontmatter(self):
        """Should return empty dict for empty frontmatter."""
        md = """---
---

Content
"""
        fm = find_frontmatter(md)
        assert fm == {}

    def test_marks_parse_error(self):
        """Should mark parse errors in frontmatter."""
        md = """---
invalid: [unbalanced
---

Content
"""
        fm = find_frontmatter(md)
        assert fm is not None
        assert fm.get("__parse_error__") == True


# ============================================================================
# Test: validate_value
# ============================================================================

class TestValidateValue:
    def test_valid_value_no_error(self):
        """Should not add error for valid value."""
        errors = []
        validate_value("test.yaml", "field", "valid", ["valid", "also-valid"], errors)
        assert len(errors) == 0

    def test_invalid_value_adds_error(self):
        """Should add error for invalid value."""
        errors = []
        validate_value("test.yaml", "field", "invalid", ["valid", "also-valid"], errors)
        assert len(errors) == 1
        assert "invalid" in errors[0]
        assert "not in enum" in errors[0]

    def test_none_value_skipped(self):
        """Should skip validation for None value."""
        errors = []
        validate_value("test.yaml", "field", None, ["valid"], errors)
        assert len(errors) == 0

    def test_empty_allowed_list_skipped(self):
        """Should skip validation when allowed list is empty."""
        errors = []
        validate_value("test.yaml", "field", "anything", [], errors)
        assert len(errors) == 0

    def test_list_value_validation(self):
        """Should validate each item in a list value."""
        errors = []
        validate_value("test.yaml", "field", ["valid", "invalid"], ["valid"], errors)
        assert len(errors) == 1
        assert "[1]='invalid'" in errors[0]

    def test_all_list_items_valid(self):
        """Should pass when all list items are valid."""
        errors = []
        validate_value("test.yaml", "field", ["a", "b"], ["a", "b", "c"], errors)
        assert len(errors) == 0


# ============================================================================
# Test: scan_file (YAML)
# ============================================================================

class TestScanFileYaml:
    def test_scans_valid_yaml(self, tmp_path, valid_enums):
        """Should scan YAML file without errors for valid values."""
        yaml_content = {
            "owner": "platform-team",
            "domain": "platform-core",
            "reliability": {"observability_tier": "gold"},
        }
        path = tmp_path / "valid.yaml"
        path.write_text(yaml.safe_dump(yaml_content))

        checks = [
            ("yaml", "owner", valid_enums["owners"]),
            ("yaml", "domain", valid_enums["domains"]),
            ("yaml", "reliability.observability_tier", valid_enums["observability_tier"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0

    def test_detects_invalid_yaml_values(self, tmp_path, valid_enums):
        """Should detect invalid enum values in YAML."""
        yaml_content = {
            "owner": "unknown-team",  # Invalid
            "domain": "platform-core",
        }
        path = tmp_path / "invalid.yaml"
        path.write_text(yaml.safe_dump(yaml_content))

        checks = [
            ("yaml", "owner", valid_enums["owners"]),
            ("yaml", "domain", valid_enums["domains"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 1
        assert "unknown-team" in errors[0]

    def test_handles_multi_document_yaml(self, tmp_path, valid_enums):
        """Should handle multi-document YAML files."""
        yaml_content = """---
owner: platform-team
domain: platform-core
---
owner: app-team-a
domain: application
"""
        path = tmp_path / "multi.yaml"
        path.write_text(yaml_content)

        checks = [
            ("yaml", "owner", valid_enums["owners"]),
            ("yaml", "domain", valid_enums["domains"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0


# ============================================================================
# Test: scan_file (Markdown frontmatter)
# ============================================================================

class TestScanFileMarkdown:
    def test_scans_valid_markdown(self, tmp_path, valid_enums):
        """Should scan markdown frontmatter without errors for valid values."""
        md_content = """---
owner: platform-team
domain: platform-core
status: active
risk_profile:
  production_impact: low
  security_risk: none
---

# Document

Content here.
"""
        path = tmp_path / "valid.md"
        path.write_text(md_content)

        checks = [
            ("mdfm", "owner", valid_enums["owners"]),
            ("mdfm", "domain", valid_enums["domains"]),
            ("mdfm", "status", valid_enums["lifecycle"]),
            ("mdfm", "risk_profile.production_impact", valid_enums["risk_profile_production_impact"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0

    def test_detects_invalid_markdown_frontmatter(self, tmp_path, valid_enums):
        """Should detect invalid values in markdown frontmatter."""
        md_content = """---
owner: invalid-team
domain: platform-core
status: unknown-status
---

# Document
"""
        path = tmp_path / "invalid.md"
        path.write_text(md_content)

        checks = [
            ("mdfm", "owner", valid_enums["owners"]),
            ("mdfm", "status", valid_enums["lifecycle"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 2

    def test_skips_markdown_without_frontmatter(self, tmp_path, valid_enums):
        """Should skip markdown files without frontmatter."""
        md_content = "# Just a Title\n\nNo frontmatter here."
        path = tmp_path / "no-fm.md"
        path.write_text(md_content)

        checks = [("mdfm", "owner", valid_enums["owners"])]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0

    def test_reports_invalid_frontmatter(self, tmp_path, valid_enums):
        """Should report invalid YAML in frontmatter."""
        md_content = """---
invalid: [unbalanced
---

# Document
"""
        path = tmp_path / "bad-fm.md"
        path.write_text(md_content)

        checks = [("mdfm", "owner", valid_enums["owners"])]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 1
        assert "invalid YAML frontmatter" in errors[0]


# ============================================================================
# Test: Nested field validation
# ============================================================================

class TestNestedFieldValidation:
    def test_validates_nested_risk_profile(self, tmp_path, valid_enums):
        """Should validate nested risk_profile fields."""
        yaml_content = {
            "risk_profile": {
                "production_impact": "high",
                "security_risk": "medium",
                "coupling_risk": "low",
            }
        }
        path = tmp_path / "risk.yaml"
        path.write_text(yaml.safe_dump(yaml_content))

        checks = [
            ("yaml", "risk_profile.production_impact", valid_enums["risk_profile_production_impact"]),
            ("yaml", "risk_profile.security_risk", valid_enums["risk_profile_security_risk"]),
            ("yaml", "risk_profile.coupling_risk", valid_enums["risk_profile_coupling_risk"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0

    def test_validates_nested_reliability(self, tmp_path, valid_enums):
        """Should validate nested reliability fields."""
        yaml_content = {
            "reliability": {
                "observability_tier": "gold",
                "rollback_strategy": "git-revert",
            }
        }
        path = tmp_path / "reliability.yaml"
        path.write_text(yaml.safe_dump(yaml_content))

        checks = [
            ("yaml", "reliability.observability_tier", valid_enums["observability_tier"]),
            ("yaml", "reliability.rollback_strategy", valid_enums["rollback_strategy"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 0

    def test_detects_invalid_nested_value(self, tmp_path, valid_enums):
        """Should detect invalid nested values."""
        yaml_content = {
            "risk_profile": {
                "production_impact": "critical",  # Invalid - should be high/medium/low
            }
        }
        path = tmp_path / "invalid-nested.yaml"
        path.write_text(yaml.safe_dump(yaml_content))

        checks = [
            ("yaml", "risk_profile.production_impact", valid_enums["risk_profile_production_impact"]),
        ]
        errors = []

        scan_file(str(path), valid_enums, checks, errors)
        assert len(errors) == 1
        assert "critical" in errors[0]
