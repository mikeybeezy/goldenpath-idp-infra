"""
Unit tests for index metadata artifact.
"""

from pathlib import Path

from scripts.rag.index_metadata import build_index_metadata, write_index_metadata


def test_build_index_metadata_sets_fields():
    meta = build_index_metadata(document_count=5, source_sha="abc123")
    assert meta.source_sha == "abc123"
    assert meta.document_count == 5
    assert meta.generated_at


def test_write_index_metadata_writes_json(tmp_path: Path):
    meta = build_index_metadata(document_count=2, source_sha="deadbeef")
    out = tmp_path / "index_metadata.json"
    write_index_metadata(out, meta)
    content = out.read_text()
    assert "deadbeef" in content
