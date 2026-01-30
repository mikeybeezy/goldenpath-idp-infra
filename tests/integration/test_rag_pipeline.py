"""
Integration tests for RAG pipeline.

Tests the full RAG pipeline end-to-end:
- loader → chunker → indexer → retriever

These tests use real ChromaDB (in-memory) to verify component interactions.

Per GOV-0017: "Integration tests are selective — use them for workflows
that cross boundaries."

References:
- GOV-0017: TDD and Determinism Policy
- PRD-0008: Governance RAG Pipeline
- ADR-0186: LlamaIndex as Retrieval Layer
"""

import pytest
import uuid
from pathlib import Path
from typing import Generator

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_governance_doc(tmp_path: Path) -> Path:
    """Create a sample governance document for testing."""
    doc_content = """---
id: GOV-TEST-001
title: Test Governance Policy
type: governance
status: active
domain: testing
lifecycle: production
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0182-tdd-philosophy
---

# GOV-TEST-001: Test Governance Policy

## Purpose

This is a test governance policy for integration testing.
The purpose is to verify the RAG pipeline works end-to-end.

## Core Principles

1. Tests must be deterministic
2. Coverage target is 60% for V1
3. All scripts require tests before implementation

## Implementation

The implementation follows TDD principles:

- Write tests first (RED phase)
- Implement to pass tests (GREEN phase)
- Refactor as needed (REFACTOR phase)

## Coverage Requirements

Per GOV-0017, the coverage target for Python scripts is 60%.
This applies to all infrastructure scripts and RAG components.
"""
    doc_path = tmp_path / "GOV-TEST-001.md"
    doc_path.write_text(doc_content)
    return doc_path


@pytest.fixture
def sample_adr_doc(tmp_path: Path) -> Path:
    """Create a sample ADR document for testing."""
    doc_content = """---
id: ADR-TEST-001
title: Test Architecture Decision
type: adr
status: accepted
domain: testing
lifecycle: production
relates_to:
  - GOV-TEST-001
---

# ADR-TEST-001: Test Architecture Decision

## Context

We need to test the RAG pipeline integration.

## Decision

We will use ChromaDB in-memory mode for integration tests.

## Consequences

- Fast test execution
- No persistent state between tests
- Deterministic results
"""
    doc_path = tmp_path / "ADR-TEST-001.md"
    doc_path.write_text(doc_content)
    return doc_path


@pytest.fixture
def in_memory_index() -> Generator:
    """Create an in-memory GovernanceIndex for testing."""
    from scripts.rag.indexer import GovernanceIndex

    collection_name = f"test_integration_{uuid.uuid4().hex}"
    index = GovernanceIndex(
        collection_name=collection_name,
        in_memory=True,
        embedding_model="mock",  # Deterministic, dependency-free embedding
    )
    yield index
    # Cleanup
    try:
        index.clear()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Tests: Full Pipeline Integration
# ---------------------------------------------------------------------------


class TestRAGPipelineIntegration:
    """Integration tests for the full RAG pipeline."""

    def test_load_chunk_index_retrieve_single_doc(
        self, sample_governance_doc: Path, in_memory_index
    ):
        """Full pipeline: load → chunk → index → retrieve returns relevant results."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.retriever import GovernanceRetriever

        # 1. Load document
        doc = load_governance_document(str(sample_governance_doc))
        assert doc.metadata["id"] == "GOV-TEST-001"
        assert doc.metadata["title"] == "Test Governance Policy"

        # 2. Chunk document
        chunks = chunk_document(doc)
        assert len(chunks) > 0

        # 3. Index chunks
        count = in_memory_index.add(chunks)
        assert count == len(chunks)
        assert in_memory_index.count() == len(chunks)

        # 4. Retrieve results
        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,  # Disable logging for tests
        )
        results = retriever.query("What is the coverage target?")

        # Verify retrieval
        assert len(results) > 0
        # Check that we got relevant content
        found_coverage = any(
            "60%" in r.text or "coverage" in r.text.lower() for r in results
        )
        assert found_coverage, "Should retrieve coverage-related content"

    def test_load_chunk_index_retrieve_multiple_docs(
        self, sample_governance_doc: Path, sample_adr_doc: Path, in_memory_index
    ):
        """Pipeline handles multiple documents correctly."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.retriever import GovernanceRetriever

        # Load and index both documents
        all_chunks = []
        for doc_path in [sample_governance_doc, sample_adr_doc]:
            doc = load_governance_document(str(doc_path))
            chunks = chunk_document(doc)
            all_chunks.extend(chunks)

        in_memory_index.add(all_chunks)

        # Retrieve
        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        # Query should find content from governance doc
        results = retriever.query("What are the TDD principles?")
        assert len(results) > 0

        # Query should find content from ADR
        results = retriever.query("What database is used for integration tests?")
        assert len(results) > 0

    def test_metadata_preserved_through_pipeline(
        self, sample_governance_doc: Path, in_memory_index
    ):
        """Metadata flows correctly through load → chunk → index → retrieve."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.retriever import GovernanceRetriever

        # Process document
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)

        # Retrieve
        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )
        results = retriever.query("coverage target")

        # Verify metadata is preserved
        assert len(results) > 0
        result = results[0]
        assert "doc_id" in result.metadata
        assert result.metadata["doc_id"] == "GOV-TEST-001"

    def test_filter_by_doc_id(
        self, sample_governance_doc: Path, sample_adr_doc: Path, in_memory_index
    ):
        """Filtering by doc_id restricts results correctly."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.retriever import GovernanceRetriever

        # Index both documents
        for doc_path in [sample_governance_doc, sample_adr_doc]:
            doc = load_governance_document(str(doc_path))
            chunks = chunk_document(doc)
            in_memory_index.add(chunks)

        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        # Query with filter
        results = retriever.query(
            "test",
            filters={"doc_id": "GOV-TEST-001"},
        )

        # All results should be from the governance doc
        for result in results:
            assert result.metadata.get("doc_id") == "GOV-TEST-001"


# ---------------------------------------------------------------------------
# Tests: CLI Integration
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    """Integration tests for CLI with real retriever."""

    def test_cli_query_returns_results(
        self, sample_governance_doc: Path, in_memory_index, capsys
    ):
        """CLI query command returns formatted results."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.cli import run_query, format_results, OutputFormat
        from scripts.rag.retriever import GovernanceRetriever

        # Setup: index document
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)

        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        # Run query through CLI functions
        results = run_query("coverage", retriever=retriever)
        output = format_results(results, format_type=OutputFormat.TEXT)

        # Verify output
        assert len(output) > 0
        assert "coverage" in output.lower() or "60%" in output

    def test_cli_json_output_valid(self, sample_governance_doc: Path, in_memory_index):
        """CLI JSON output is valid and parseable."""
        import json
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.cli import run_query, format_results, OutputFormat
        from scripts.rag.retriever import GovernanceRetriever

        # Setup
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)

        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        # Run query
        results = run_query("TDD", retriever=retriever)
        output = format_results(results, format_type=OutputFormat.JSON)

        # Verify JSON is valid
        parsed = json.loads(output)
        assert "results" in parsed
        assert isinstance(parsed["results"], list)


# ---------------------------------------------------------------------------
# Tests: Error Handling
# ---------------------------------------------------------------------------


class TestPipelineErrorHandling:
    """Integration tests for error handling across the pipeline."""

    def test_query_empty_index_returns_empty(self, in_memory_index):
        """Querying an empty index returns empty results gracefully."""
        from scripts.rag.retriever import GovernanceRetriever

        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        results = retriever.query("anything")
        assert results == [] or len(results) == 0

    def test_invalid_filter_handled(self, sample_governance_doc: Path, in_memory_index):
        """Invalid filters are handled gracefully."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document
        from scripts.rag.retriever import GovernanceRetriever

        # Setup
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)

        retriever = GovernanceRetriever(
            collection=in_memory_index.collection,
            usage_log_path=None,
        )

        # Query with non-matching filter
        results = retriever.query(
            "coverage",
            filters={"doc_id": "NONEXISTENT-DOC"},
        )

        # Should return empty, not error
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Tests: Index Lifecycle
# ---------------------------------------------------------------------------


class TestIndexLifecycle:
    """Integration tests for index create/clear/rebuild."""

    def test_clear_removes_all_documents(
        self, sample_governance_doc: Path, in_memory_index
    ):
        """Clearing an index removes all documents."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document

        # Index document
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)
        assert in_memory_index.count() > 0

        # Clear
        in_memory_index.clear()
        assert in_memory_index.count() == 0

    def test_reindex_replaces_documents(
        self, sample_governance_doc: Path, in_memory_index
    ):
        """Re-indexing replaces documents correctly."""
        from scripts.rag.loader import load_governance_document
        from scripts.rag.chunker import chunk_document

        # Index document
        doc = load_governance_document(str(sample_governance_doc))
        chunks = chunk_document(doc)
        in_memory_index.add(chunks)
        initial_count = in_memory_index.count()

        # Clear and re-index
        in_memory_index.clear()
        in_memory_index.add(chunks)

        assert in_memory_index.count() == initial_count
