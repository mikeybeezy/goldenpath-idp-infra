"""
Integration test fixtures and configuration.

Per GOV-0017: Integration tests are Tier 3 and run selectively.
Use `pytest --runintegration` to include these tests.
"""

import pytest


def pytest_configure(config):
    """Register integration marker."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires --runintegration to run)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --runintegration is passed."""
    if config.getoption("--runintegration", default=False):
        return

    skip_integration = pytest.mark.skip(
        reason="Integration test: use --runintegration to run"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


def pytest_addoption(parser):
    """Add --runintegration option if not already present."""
    try:
        parser.addoption(
            "--runintegration",
            action="store_true",
            default=False,
            help="Run integration tests",
        )
    except ValueError:
        # Option already exists (defined in main conftest.py)
        pass
