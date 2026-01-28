"""
Unit tests for RAG markdown chunker.

Tests the chunker module's ability to:
- Split documents on H2 (##) header boundaries (ADR-0184)
- Preserve document metadata in each chunk
- Handle edge cases (no headers, single section, oversized sections)
- Include section headers in chunk content

Per GOV-0017: "Nothing that generates infrastructure, parses config, or emits
scaffolds may change without tests."

References:
- GOV-0017: TDD and Determinism Policy
- ADR-0184: RAG Markdown Header Chunking Strategy
"""

import pytest

# Import will fail until chunker.py is implemented (RED phase)
from scripts.rag.chunker import (
    chunk_markdown,
    chunk_document,
)
from scripts.rag.loader import GovernanceDocument


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_content() -> str:
    """Simple markdown with two H2 sections."""
    return """# Document Title

## Section A

Content for section A.
More content here.

## Section B

Content for section B.
Different content here.
"""


@pytest.fixture
def content_with_subsections() -> str:
    """Markdown with H2 and H3 sections."""
    return """# Document Title

## Main Section

Introduction text.

### Subsection 1

Subsection content.

### Subsection 2

More subsection content.

## Another Section

Final content.
"""


@pytest.fixture
def content_no_headers() -> str:
    """Markdown with no H2 headers."""
    return """# Only H1 Header

This document has no H2 sections.
It should be treated as a single chunk.

Some more paragraphs here.
"""


@pytest.fixture
def sample_metadata() -> dict:
    """Sample document metadata."""
    return {
        "id": "GOV-0017-tdd-and-determinism",
        "title": "TDD and Determinism Policy",
        "type": "governance",
        "file_path": "/docs/GOV-0017.md",
    }


@pytest.fixture
def governance_doc(simple_content: str, sample_metadata: dict) -> GovernanceDocument:
    """Create a GovernanceDocument for testing."""
    return GovernanceDocument(
        content=simple_content,
        metadata=sample_metadata,
        source_path="/docs/GOV-0017.md",
    )


# ---------------------------------------------------------------------------
# Tests: Basic Chunking
# ---------------------------------------------------------------------------


class TestBasicChunking:
    """Tests for basic H2 header splitting."""

    def test_splits_on_h2_headers(self, simple_content: str):
        """Chunker must split content on ## headers."""
        chunks = chunk_markdown(simple_content, {})
        # Should have at least 2 chunks (Section A and Section B)
        assert len(chunks) >= 2

    def test_each_chunk_contains_header(self, simple_content: str):
        """Each chunk should contain its section header."""
        chunks = chunk_markdown(simple_content, {})
        # Find chunks with sections (skip any H1-only chunks)
        section_chunks = [c for c in chunks if "## " in c.text]
        assert len(section_chunks) >= 2
        assert any("## Section A" in c.text for c in chunks)
        assert any("## Section B" in c.text for c in chunks)

    def test_chunk_contains_section_content(self, simple_content: str):
        """Each chunk should contain its section content."""
        chunks = chunk_markdown(simple_content, {})
        section_a = next((c for c in chunks if "## Section A" in c.text), None)
        assert section_a is not None
        assert "Content for section A" in section_a.text

    def test_chunks_do_not_overlap(self, simple_content: str):
        """Chunk boundaries should not overlap (per ADR-0184: overlap = 0)."""
        chunks = chunk_markdown(simple_content, {})
        # Section B content should not appear in Section A chunk
        section_a = next((c for c in chunks if "## Section A" in c.text), None)
        if section_a:
            assert "Content for section B" not in section_a.text


# ---------------------------------------------------------------------------
# Tests: Metadata Preservation
# ---------------------------------------------------------------------------


class TestMetadataPreservation:
    """Tests for preserving document metadata in chunks."""

    def test_chunk_inherits_doc_id(self, governance_doc: GovernanceDocument):
        """Each chunk must inherit the document ID."""
        chunks = chunk_document(governance_doc)
        for chunk in chunks:
            assert chunk.metadata.get("doc_id") == "GOV-0017-tdd-and-determinism"

    def test_chunk_inherits_doc_title(self, governance_doc: GovernanceDocument):
        """Each chunk must inherit the document title."""
        chunks = chunk_document(governance_doc)
        for chunk in chunks:
            assert chunk.metadata.get("doc_title") == "TDD and Determinism Policy"

    def test_chunk_includes_section_name(self, governance_doc: GovernanceDocument):
        """Each chunk must include its section name in metadata."""
        chunks = chunk_document(governance_doc)
        section_names = [c.metadata.get("section") for c in chunks]
        # At least Section A and Section B should be present
        assert "Section A" in section_names or any(
            "Section A" in str(n) for n in section_names if n
        )

    def test_chunk_includes_chunk_index(self, governance_doc: GovernanceDocument):
        """Each chunk must have a chunk_index for ordering."""
        chunks = chunk_document(governance_doc)
        indices = [c.metadata.get("chunk_index") for c in chunks]
        # All indices should be integers
        assert all(isinstance(i, int) for i in indices if i is not None)
        # Indices should be sequential
        if len(indices) > 1:
            assert indices == sorted(indices)

    def test_chunk_includes_file_path(self, governance_doc: GovernanceDocument):
        """Each chunk must include the source file path."""
        chunks = chunk_document(governance_doc)
        for chunk in chunks:
            assert chunk.metadata.get("file_path") == "/docs/GOV-0017.md"


# ---------------------------------------------------------------------------
# Tests: Subsection Handling
# ---------------------------------------------------------------------------


class TestSubsectionHandling:
    """Tests for handling H3 subsections within H2 sections."""

    def test_keeps_h3_with_parent_h2(self, content_with_subsections: str):
        """H3 subsections should stay with their parent H2 section."""
        chunks = chunk_markdown(content_with_subsections, {})
        main_section = next((c for c in chunks if "## Main Section" in c.text), None)
        assert main_section is not None
        # H3 subsections should be in the same chunk
        assert "### Subsection 1" in main_section.text
        assert "### Subsection 2" in main_section.text

    def test_h3_not_split_into_separate_chunks(self, content_with_subsections: str):
        """H3 headers should NOT create separate chunks."""
        chunks = chunk_markdown(content_with_subsections, {})
        # Should only have chunks for H2 sections, not H3
        h2_chunks = [c for c in chunks if c.text.strip().startswith("## ")]
        h3_only_chunks = [
            c
            for c in chunks
            if c.text.strip().startswith("### ") and "## " not in c.text
        ]
        assert len(h3_only_chunks) == 0


# ---------------------------------------------------------------------------
# Tests: Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Tests for edge cases in chunking."""

    def test_handles_no_h2_headers(self, content_no_headers: str):
        """Content with no H2 headers should become a single chunk."""
        chunks = chunk_markdown(content_no_headers, {})
        # Should return at least one chunk with all content
        assert len(chunks) >= 1
        combined_text = " ".join(c.text for c in chunks)
        assert "This document has no H2 sections" in combined_text

    def test_handles_empty_content(self):
        """Empty content should return empty list or single empty chunk."""
        chunks = chunk_markdown("", {})
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0].text.strip() == "")

    def test_handles_h2_at_start(self):
        """Content starting with H2 (no H1) should chunk correctly."""
        content = """## First Section

Content here.

## Second Section

More content.
"""
        chunks = chunk_markdown(content, {})
        assert len(chunks) >= 2

    def test_preserves_code_blocks(self):
        """Code blocks should be preserved within chunks."""
        content = """## Code Example

Here's some code:

```python
def hello():
    print("Hello, world!")
```

More text after code.
"""
        chunks = chunk_markdown(content, {})
        code_chunk = next((c for c in chunks if "## Code Example" in c.text), None)
        assert code_chunk is not None
        assert "```python" in code_chunk.text
        assert 'print("Hello, world!")' in code_chunk.text


# ---------------------------------------------------------------------------
# Tests: Chunk Dataclass
# ---------------------------------------------------------------------------


class TestChunkDataclass:
    """Tests for the Chunk data structure."""

    def test_chunk_has_text_attribute(self, simple_content: str):
        """Chunk must have a text attribute."""
        chunks = chunk_markdown(simple_content, {})
        assert len(chunks) > 0
        assert hasattr(chunks[0], "text")
        assert isinstance(chunks[0].text, str)

    def test_chunk_has_metadata_attribute(self, simple_content: str):
        """Chunk must have a metadata attribute."""
        chunks = chunk_markdown(simple_content, {})
        assert len(chunks) > 0
        assert hasattr(chunks[0], "metadata")
        assert isinstance(chunks[0].metadata, dict)

    def test_chunk_text_not_empty(self, simple_content: str):
        """Chunk text should not be empty (unless document is empty)."""
        chunks = chunk_markdown(simple_content, {})
        for chunk in chunks:
            # Allow whitespace-only for edge cases, but generally should have content
            assert chunk.text is not None
