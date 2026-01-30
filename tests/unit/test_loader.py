"""
Unit tests for RAG document loader.

Tests the loader module's ability to:
- Load governance documents from the filesystem
- Extract YAML frontmatter as metadata
- Separate content from frontmatter
- Handle edge cases (missing frontmatter, empty content)

Per GOV-0017: "Nothing that generates infrastructure, parses config, or emits
scaffolds may change without tests."

References:
- GOV-0017: TDD and Determinism Policy
- ADR-0184: RAG Markdown Header Chunking Strategy
"""

import pytest
from pathlib import Path

# Import will fail until loader.py is implemented (RED phase)
from scripts.rag.loader import (
    load_governance_document,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_doc_path(tmp_path: Path) -> Path:
    """Create a sample governance document for testing."""
    content = """---
id: GOV-0017-tdd-and-determinism
title: TDD and Determinism Policy
type: governance
owner: platform-team
status: active
relates_to:
  - ADR-0182-tdd-philosophy
  - GOV-0016-testing-stack-matrix
---

# GOV-0017: TDD and Determinism Policy

## Purpose

This policy defines the testing and determinism requirements.

## Core Principle

> "Nothing that generates infrastructure, parses config, or emits scaffolds may change without tests."
"""
    doc_path = tmp_path / "GOV-0017-tdd-and-determinism.md"
    doc_path.write_text(content)
    return doc_path


@pytest.fixture
def doc_without_frontmatter(tmp_path: Path) -> Path:
    """Create a document without YAML frontmatter."""
    content = """# Simple Document

This document has no frontmatter.

## Section

Content here.
"""
    doc_path = tmp_path / "no-frontmatter.md"
    doc_path.write_text(content)
    return doc_path


@pytest.fixture
def empty_doc(tmp_path: Path) -> Path:
    """Create an empty document."""
    doc_path = tmp_path / "empty.md"
    doc_path.write_text("")
    return doc_path


# ---------------------------------------------------------------------------
# Tests: Frontmatter Extraction
# ---------------------------------------------------------------------------


class TestExtractFrontmatter:
    """Tests for frontmatter extraction from markdown content."""

    def test_extracts_id_from_frontmatter(self, sample_doc_path: Path):
        """Loader must extract id field from YAML frontmatter."""
        doc = load_governance_document(sample_doc_path)
        assert doc.metadata["id"] == "GOV-0017-tdd-and-determinism"

    def test_extracts_title_from_frontmatter(self, sample_doc_path: Path):
        """Loader must extract title field from YAML frontmatter."""
        doc = load_governance_document(sample_doc_path)
        assert doc.metadata["title"] == "TDD and Determinism Policy"

    def test_extracts_type_from_frontmatter(self, sample_doc_path: Path):
        """Loader must extract type field from YAML frontmatter."""
        doc = load_governance_document(sample_doc_path)
        assert doc.metadata["type"] == "governance"

    def test_extracts_relates_to_as_list(self, sample_doc_path: Path):
        """Loader must extract relates_to as a list of references."""
        doc = load_governance_document(sample_doc_path)
        assert "relates_to" in doc.metadata
        assert isinstance(doc.metadata["relates_to"], list)
        assert "ADR-0182-tdd-philosophy" in doc.metadata["relates_to"]

    def test_includes_file_path_in_metadata(self, sample_doc_path: Path):
        """Loader must include the source file path in metadata."""
        doc = load_governance_document(sample_doc_path)
        assert "file_path" in doc.metadata
        assert doc.metadata["file_path"] == str(sample_doc_path)


# ---------------------------------------------------------------------------
# Tests: Content Separation
# ---------------------------------------------------------------------------


class TestContentSeparation:
    """Tests for separating content from frontmatter."""

    def test_content_does_not_include_frontmatter_delimiters(
        self, sample_doc_path: Path
    ):
        """Content should not start with YAML frontmatter delimiters."""
        doc = load_governance_document(sample_doc_path)
        assert not doc.content.strip().startswith("---")

    def test_content_includes_document_title(self, sample_doc_path: Path):
        """Content should include the H1 document title."""
        doc = load_governance_document(sample_doc_path)
        assert "# GOV-0017: TDD and Determinism Policy" in doc.content

    def test_content_includes_sections(self, sample_doc_path: Path):
        """Content should include all H2 sections."""
        doc = load_governance_document(sample_doc_path)
        assert "## Purpose" in doc.content
        assert "## Core Principle" in doc.content

    def test_content_preserves_markdown_formatting(self, sample_doc_path: Path):
        """Content should preserve markdown formatting (blockquotes, etc)."""
        doc = load_governance_document(sample_doc_path)
        assert '> "Nothing that generates' in doc.content


# ---------------------------------------------------------------------------
# Tests: Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_handles_missing_frontmatter(self, doc_without_frontmatter: Path):
        """Loader should handle documents without frontmatter gracefully."""
        doc = load_governance_document(doc_without_frontmatter)
        # Should return empty metadata dict (not None, not error)
        assert doc.metadata == {} or doc.metadata.get("file_path") == str(
            doc_without_frontmatter
        )
        assert "# Simple Document" in doc.content

    def test_handles_empty_document(self, empty_doc: Path):
        """Loader should handle empty documents gracefully."""
        doc = load_governance_document(empty_doc)
        assert doc.content == ""
        assert doc.metadata.get("file_path") == str(empty_doc)

    def test_raises_for_nonexistent_file(self, tmp_path: Path):
        """Loader should raise FileNotFoundError for missing files."""
        nonexistent = tmp_path / "does-not-exist.md"
        with pytest.raises(FileNotFoundError):
            load_governance_document(nonexistent)


# ---------------------------------------------------------------------------
# Tests: GovernanceDocument Dataclass
# ---------------------------------------------------------------------------


class TestGovernanceDocument:
    """Tests for the GovernanceDocument data structure."""

    def test_has_content_attribute(self, sample_doc_path: Path):
        """GovernanceDocument must have a content attribute."""
        doc = load_governance_document(sample_doc_path)
        assert hasattr(doc, "content")
        assert isinstance(doc.content, str)

    def test_has_metadata_attribute(self, sample_doc_path: Path):
        """GovernanceDocument must have a metadata attribute."""
        doc = load_governance_document(sample_doc_path)
        assert hasattr(doc, "metadata")
        assert isinstance(doc.metadata, dict)

    def test_has_source_path_attribute(self, sample_doc_path: Path):
        """GovernanceDocument must have a source_path attribute."""
        doc = load_governance_document(sample_doc_path)
        assert hasattr(doc, "source_path")
        assert isinstance(doc.source_path, (str, Path))
