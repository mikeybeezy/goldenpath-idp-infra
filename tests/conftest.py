"""
Pytest configuration and shared fixtures for GoldenPath IDP infrastructure tests.

This file is automatically loaded by pytest. Fixtures defined here are available
to all test files without explicit import.

Usage:
    pytest tests/                    # Run all tests
    pytest tests/unit/               # Run unit tests only
    pytest tests/ --cov=scripts      # Run with coverage
    pytest tests/ -v                 # Verbose output
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def scripts_dir(project_root: Path) -> Path:
    """Return the scripts directory."""
    return project_root / "scripts"


@pytest.fixture
def docs_dir(project_root: Path) -> Path:
    """Return the docs directory."""
    return project_root / "docs"


@pytest.fixture
def tests_dir(project_root: Path) -> Path:
    """Return the tests directory."""
    return project_root / "tests"


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file that is cleaned up after the test."""
    filepath = temp_dir / "test_file.txt"
    filepath.touch()
    yield filepath


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_yaml_content() -> str:
    """Return sample YAML content for testing."""
    return """---
id: test-document
title: Test Document
type: documentation
owner: platform-team
status: active
domain: platform-core
lifecycle: active
schema_version: 1
relates_to:
  - other-document
---

# Test Document

This is test content.
"""


@pytest.fixture
def sample_frontmatter() -> Dict[str, Any]:
    """Return sample frontmatter as a dictionary."""
    return {
        "id": "test-document",
        "title": "Test Document",
        "type": "documentation",
        "owner": "platform-team",
        "status": "active",
        "domain": "platform-core",
        "lifecycle": "active",
        "schema_version": 1,
        "relates_to": ["other-document"],
    }


@pytest.fixture
def sample_json_content() -> str:
    """Return sample JSON content for testing."""
    return json.dumps(
        {
            "name": "test",
            "version": "1.0.0",
            "data": {"key": "value"},
        },
        indent=2,
    )


@pytest.fixture
def sample_script_metadata() -> Dict[str, Any]:
    """Return sample script metadata."""
    return {
        "id": "SCRIPT-0001",
        "name": "test_script",
        "description": "A test script",
        "owner": "platform-team",
        "maturity": 2,
        "certified": False,
        "test_coverage": 0.0,
    }


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_aws_credentials() -> Generator[None, None, None]:
    """Mock AWS credentials for testing."""
    with patch.dict(
        os.environ,
        {
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_DEFAULT_REGION": "eu-west-2",
        },
    ):
        yield


@pytest.fixture
def mock_github_env() -> Generator[None, None, None]:
    """Mock GitHub Actions environment variables."""
    with patch.dict(
        os.environ,
        {
            "GITHUB_REPOSITORY": "mikeybeezy/goldenpath-idp-infra",
            "GITHUB_SHA": "abc123",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_ACTOR": "test-user",
            "GITHUB_WORKFLOW": "test-workflow",
        },
    ):
        yield


@pytest.fixture
def mock_logger() -> MagicMock:
    """Return a mock logger for testing."""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.debug = MagicMock()
    return logger


# =============================================================================
# File Creation Helpers
# =============================================================================


@pytest.fixture
def create_yaml_file(temp_dir: Path):
    """Factory fixture to create YAML files for testing."""

    def _create(filename: str, content: Dict[str, Any]) -> Path:
        filepath = temp_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(content, f)
        return filepath

    return _create


@pytest.fixture
def create_json_file(temp_dir: Path):
    """Factory fixture to create JSON files for testing."""

    def _create(filename: str, content: Dict[str, Any]) -> Path:
        filepath = temp_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(content, f, indent=2)
        return filepath

    return _create


@pytest.fixture
def create_markdown_file(temp_dir: Path):
    """Factory fixture to create Markdown files with frontmatter."""

    def _create(
        filename: str, frontmatter: Dict[str, Any], body: str = ""
    ) -> Path:
        filepath = temp_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write("---\n")
            yaml.dump(frontmatter, f)
            f.write("---\n\n")
            f.write(body)
        return filepath

    return _create


# =============================================================================
# Pytest Configuration
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
    )
    config.addinivalue_line(
        "markers",
        "requires_aws: marks tests that require AWS credentials",
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on markers and environment."""
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    skip_integration = pytest.mark.skip(
        reason="need --runintegration option to run"
    )
    skip_aws = pytest.mark.skip(reason="AWS credentials not configured")

    for item in items:
        # Skip slow tests unless --runslow is passed
        if "slow" in item.keywords and not config.getoption("--runslow", False):
            item.add_marker(skip_slow)

        # Skip integration tests unless --runintegration is passed
        if "integration" in item.keywords and not config.getoption(
            "--runintegration", False
        ):
            item.add_marker(skip_integration)

        # Skip AWS tests if credentials not available
        if "requires_aws" in item.keywords:
            if not os.environ.get("AWS_ACCESS_KEY_ID"):
                item.add_marker(skip_aws)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="run slow tests",
    )
    parser.addoption(
        "--runintegration",
        action="store_true",
        default=False,
        help="run integration tests",
    )
