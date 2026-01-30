"""
Unit tests for index build flow.
"""

from pathlib import Path
from unittest.mock import patch

from scripts.rag.index_build import build_index
from scripts.rag.loader import GovernanceDocument


def test_build_index_writes_metadata(tmp_path: Path):
    doc = GovernanceDocument(
        content="# Title", metadata={"id": "DOC-1"}, source_path=""
    )

    with (
        patch("scripts.rag.index_build.collect_markdown_paths") as mock_collect,
        patch("scripts.rag.index_build.load_documents") as mock_load,
        patch("scripts.rag.index_build.GovernanceIndex") as mock_index,
        patch("scripts.rag.index_build.ingest_documents") as mock_ingest,
        patch("scripts.rag.index_build.write_index_metadata") as mock_write,
    ):
        mock_collect.return_value = [tmp_path / "docs/test.md"]
        mock_load.return_value = ([doc], [])
        mock_index.return_value.add.return_value = 1

        build_index(root=tmp_path, metadata_path=tmp_path / "meta.json")

        assert mock_write.called


def test_collect_and_build_index_respects_scope(tmp_path: Path):
    """
    Integration-style test: ensure absolute paths are filtered by scope
    and index build runs end-to-end on allowed docs.
    """
    docs_dir = tmp_path / "docs" / "10-governance" / "policies"
    logs_dir = tmp_path / "logs"
    docs_dir.mkdir(parents=True)
    logs_dir.mkdir(parents=True)

    allowed_path = docs_dir / "GOV-0001.md"
    denied_path = logs_dir / "ignored.md"

    allowed_path.write_text(
        "---\n"
        "id: GOV-0001\n"
        "title: Test Policy\n"
        "type: governance\n"
        "---\n\n"
        "# GOV-0001\n\n"
        "## Purpose\n\n"
        "Test content.\n"
    )
    denied_path.write_text("# Ignored")

    from scripts.rag import index_build

    # Use real collection of paths, but replace indexer to avoid heavy deps
    class FakeIndex:
        def add(self, chunks):
            return len(chunks)

    with (
        patch.object(index_build, "GovernanceIndex", return_value=FakeIndex()),
        patch.object(index_build, "_graph_client_from_env", return_value=None),
    ):
        count = index_build.build_index(
            root=tmp_path, metadata_path=tmp_path / "reports/index_metadata.json"
        )

    assert count >= 1
    assert (tmp_path / "reports/index_metadata.json").exists()


def test_build_index_writes_error_report(tmp_path: Path):
    from scripts.rag import index_build

    error_path = tmp_path / "bad.md"
    error_path.write_text("# bad")
    error_entry = {"path": str(error_path), "error": "boom"}

    class FakeIndex:
        def add(self, chunks):
            return len(chunks)

    with (
        patch.object(index_build, "collect_markdown_paths", return_value=[error_path]),
        patch.object(index_build, "load_documents", return_value=([], [error_entry])),
        patch.object(index_build, "GovernanceIndex", return_value=FakeIndex()),
        patch.object(index_build, "_graph_client_from_env", return_value=None),
        patch.object(index_build, "write_index_metadata"),
    ):
        index_build.build_index(root=tmp_path)

    report_path = tmp_path / "reports/index_errors.json"
    assert report_path.exists()
