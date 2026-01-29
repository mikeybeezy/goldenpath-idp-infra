"""
Unit tests for scope filtering.
"""

from scripts.rag.scope import is_allowed_path, filter_paths


def test_allows_docs_tree():
    assert is_allowed_path("docs/10-governance/policies/GOV-0017.md")
    assert is_allowed_path("/Users/test/repo/docs/10-governance/policies/GOV-0017.md")


def test_allows_session_capture():
    assert is_allowed_path("session_capture/2026-01-28-agentic-graph-rag-phase0.md")
    assert is_allowed_path("/Users/test/repo/session_capture/2026-01-28-agentic-graph-rag-phase0.md")


def test_allows_changelog_entries():
    assert is_allowed_path("docs/changelog/entries/2026-01-01-change.md")
    assert is_allowed_path("/Users/test/repo/docs/changelog/entries/2026-01-01-change.md")


def test_allows_platform_health_files():
    assert is_allowed_path("PLATFORM_HEALTH.md")
    assert is_allowed_path("PLATFORM_DASHBOARDS.md")
    assert is_allowed_path("/Users/test/repo/PLATFORM_HEALTH.md")


def test_allows_scripts_index():
    assert is_allowed_path("scripts/index.md")
    assert is_allowed_path("/Users/test/repo/scripts/index.md")


def test_denies_node_modules():
    assert not is_allowed_path("apps/foo/node_modules/bar.js")


def test_denies_terraform_state():
    assert not is_allowed_path("envs/dev/.terraform/state.tfstate")


def test_denies_logs():
    assert not is_allowed_path("logs/2026-01-01.log")


def test_filter_paths_only_returns_allowed():
    paths = [
        "docs/10-governance/policies/GOV-0017.md",
        "logs/2026-01-01.log",
        "PLATFORM_HEALTH.md",
    ]
    allowed = filter_paths(paths)
    assert len(allowed) == 2
