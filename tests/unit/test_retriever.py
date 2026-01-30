"""
Unit tests for RAG retriever.

Tests the retriever module's ability to:
- Query ChromaDB for similar chunks (vector search)
- Support metadata filtering (doc_type, doc_id)
- Return ranked results with source citations
- Format citations for governance documents

Per GOV-0017: "Nothing that generates infrastructure, parses config, or emits
scaffolds may change without tests."

Per ADR-0186: Use LlamaIndex for retrieval with ChromaDB backend.

References:
- GOV-0017: TDD and Determinism Policy
- ADR-0186: LlamaIndex as Retrieval Layer
- PRD-0008: Governance RAG Pipeline
"""

import pytest
from unittest.mock import MagicMock, patch

# Import will fail until retriever.py is implemented (RED phase)
from scripts.rag.retriever import (
    retrieve,
    RetrievalResult,
    format_citation,
    GovernanceRetriever,
    log_usage,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_chroma_client():
    """Create a mock ChromaDB client."""
    with patch("scripts.rag.retriever.chromadb") as mock_chromadb:
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_chromadb.Client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_collection():
    """Create a mock ChromaDB collection with query results."""
    collection = MagicMock()
    collection.name = "governance_docs"
    collection.count.return_value = 10

    # Mock query results
    collection.query.return_value = {
        "ids": [["GOV-0017_0", "GOV-0017_1", "ADR-0184_0"]],
        "documents": [
            [
                "## Purpose\n\nThis policy defines testing requirements.",
                "## Core Principle\n\nTests are executable contracts.",
                "## Decision\n\nUse H2 headers for chunking.",
            ]
        ],
        "metadatas": [
            [
                {
                    "doc_id": "GOV-0017",
                    "doc_title": "TDD Policy",
                    "section": "Purpose",
                    "chunk_index": 0,
                    "file_path": "docs/10-governance/policies/GOV-0017.md",
                },
                {
                    "doc_id": "GOV-0017",
                    "doc_title": "TDD Policy",
                    "section": "Core Principle",
                    "chunk_index": 1,
                    "file_path": "docs/10-governance/policies/GOV-0017.md",
                },
                {
                    "doc_id": "ADR-0184",
                    "doc_title": "RAG Chunking Strategy",
                    "section": "Decision",
                    "chunk_index": 0,
                    "file_path": "docs/adrs/ADR-0184.md",
                },
            ]
        ],
        "distances": [[0.1, 0.3, 0.5]],
    }
    return collection


@pytest.fixture
def sample_query():
    """Sample query string for testing."""
    return "What are the testing requirements for TDD?"


# ---------------------------------------------------------------------------
# Tests: Basic Retrieval
# ---------------------------------------------------------------------------


class TestBasicRetrieval:
    """Tests for basic vector search retrieval."""

    def test_retrieve_returns_results(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must return a list of RetrievalResult objects."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_retrieve_returns_top_k_results(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must respect the top_k parameter."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection, top_k=2)

        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert call_args[1]["n_results"] == 2

    def test_retrieve_default_top_k(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must use default top_k of 5."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retrieve(sample_query, collection=mock_collection)

        call_args = mock_collection.query.call_args
        assert call_args[1]["n_results"] == 5

    def test_retrieve_passes_query_text(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must pass the query text to ChromaDB."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retrieve(sample_query, collection=mock_collection)

        call_args = mock_collection.query.call_args
        assert call_args[1]["query_texts"] == [sample_query]


# ---------------------------------------------------------------------------
# Tests: RetrievalResult Dataclass
# ---------------------------------------------------------------------------


class TestRetrievalResult:
    """Tests for the RetrievalResult data structure."""

    def test_result_has_text(self, mock_chroma_client, mock_collection, sample_query):
        """RetrievalResult must have a text attribute."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        assert hasattr(results[0], "text")
        assert isinstance(results[0].text, str)
        assert "Purpose" in results[0].text

    def test_result_has_metadata(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """RetrievalResult must have a metadata attribute."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        assert hasattr(results[0], "metadata")
        assert isinstance(results[0].metadata, dict)
        assert results[0].metadata["doc_id"] == "GOV-0017"

    def test_result_has_score(self, mock_chroma_client, mock_collection, sample_query):
        """RetrievalResult must have a score attribute."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        assert hasattr(results[0], "score")
        assert isinstance(results[0].score, float)

    def test_result_has_id(self, mock_chroma_client, mock_collection, sample_query):
        """RetrievalResult must have an id attribute."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        assert hasattr(results[0], "id")
        assert results[0].id == "GOV-0017_0"

    def test_results_ordered_by_relevance(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """Results must be ordered by relevance (lowest distance first)."""
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve(sample_query, collection=mock_collection)

        # First result should have lowest distance (highest relevance)
        assert results[0].score <= results[1].score


# ---------------------------------------------------------------------------
# Tests: Metadata Filtering
# ---------------------------------------------------------------------------


class TestMetadataFiltering:
    """Tests for metadata-based filtering."""

    def test_filter_by_doc_id(self, mock_chroma_client, mock_collection, sample_query):
        """retrieve must support filtering by doc_id."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retrieve(
            sample_query,
            collection=mock_collection,
            filters={"doc_id": "GOV-0017"},
        )

        call_args = mock_collection.query.call_args
        where_clause = call_args[1].get("where")
        assert where_clause is not None
        assert where_clause.get("doc_id") == "GOV-0017"

    def test_filter_by_doc_type(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must support filtering by doc_type."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retrieve(
            sample_query,
            collection=mock_collection,
            filters={"doc_type": "governance"},
        )

        call_args = mock_collection.query.call_args
        where_clause = call_args[1].get("where")
        assert where_clause is not None
        assert where_clause.get("doc_type") == "governance"

    def test_no_filter_when_none_provided(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """retrieve must not add where clause when no filters provided."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retrieve(sample_query, collection=mock_collection)

        call_args = mock_collection.query.call_args
        where_clause = call_args[1].get("where")
        assert where_clause is None


# ---------------------------------------------------------------------------
# Tests: Citation Formatting
# ---------------------------------------------------------------------------


class TestCitationFormatting:
    """Tests for citation formatting."""

    def test_format_citation_includes_doc_id(self):
        """Citation must include the document ID."""
        result = RetrievalResult(
            id="GOV-0017_0",
            text="Test content",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.1,
        )

        citation = format_citation(result)

        assert "GOV-0017" in citation

    def test_format_citation_includes_section(self):
        """Citation must include the section name."""
        result = RetrievalResult(
            id="GOV-0017_0",
            text="Test content",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.1,
        )

        citation = format_citation(result)

        assert "Purpose" in citation

    def test_format_citation_includes_file_path(self):
        """Citation must include the file path."""
        result = RetrievalResult(
            id="GOV-0017_0",
            text="Test content",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.1,
        )

        citation = format_citation(result)

        assert "docs/10-governance/policies/GOV-0017.md" in citation

    def test_format_citation_markdown_link(self):
        """Citation must be formatted as a markdown link."""
        result = RetrievalResult(
            id="GOV-0017_0",
            text="Test content",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "file_path": "docs/10-governance/policies/GOV-0017.md",
            },
            score=0.1,
        )

        citation = format_citation(result)

        # Should be a markdown link format: [text](path)
        assert "[" in citation
        assert "](" in citation
        assert ")" in citation


# ---------------------------------------------------------------------------
# Tests: GovernanceRetriever Class
# ---------------------------------------------------------------------------


class TestGovernanceRetriever:
    """Tests for the GovernanceRetriever convenience class."""

    def test_retriever_creates_with_collection(self, mock_chroma_client):
        """GovernanceRetriever must accept a collection on init."""
        mock_collection = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(collection=mock_collection, usage_log_path=None)

        assert retriever.collection is not None

    def test_retriever_creates_collection_by_name(self, mock_chroma_client):
        """GovernanceRetriever must create collection from name."""
        mock_collection = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(
            collection_name="test_index", usage_log_path=None
        )

        mock_chroma_client.get_collection.assert_called()

    def test_retriever_query_returns_results(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """GovernanceRetriever.query must return results."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(collection=mock_collection, usage_log_path=None)
        results = retriever.query(sample_query)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_retriever_query_with_top_k(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """GovernanceRetriever.query must support top_k parameter."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(collection=mock_collection, usage_log_path=None)
        retriever.query(sample_query, top_k=3)

        call_args = mock_collection.query.call_args
        assert call_args[1]["n_results"] == 3

    def test_retriever_query_with_filters(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """GovernanceRetriever.query must support filters."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(collection=mock_collection, usage_log_path=None)
        retriever.query(sample_query, filters={"doc_type": "governance"})

        call_args = mock_collection.query.call_args
        where_clause = call_args[1].get("where")
        assert where_clause is not None

    def test_retriever_query_with_citations(
        self, mock_chroma_client, mock_collection, sample_query
    ):
        """GovernanceRetriever.query_with_citations must return formatted results."""
        mock_chroma_client.get_collection.return_value = mock_collection

        retriever = GovernanceRetriever(collection=mock_collection, usage_log_path=None)
        results = retriever.query_with_citations(sample_query)

        assert isinstance(results, list)
        # Each result should have a citation key
        for result in results:
            assert "citation" in result or hasattr(result, "citation")


# ---------------------------------------------------------------------------
# Tests: Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Tests for edge cases in retrieval."""

    def test_empty_query_returns_empty(self, mock_chroma_client, mock_collection):
        """retrieve must handle empty query gracefully."""
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve("", collection=mock_collection)

        assert results == []

    def test_no_results_returns_empty_list(self, mock_chroma_client, mock_collection):
        """retrieve must return empty list when no results found."""
        mock_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve("nonexistent query", collection=mock_collection)

        assert results == []

    def test_handles_missing_metadata_fields(self, mock_chroma_client, mock_collection):
        """retrieve must handle results with missing metadata fields."""
        mock_collection.query.return_value = {
            "ids": [["doc_1"]],
            "documents": [["Some content"]],
            "metadatas": [[{"doc_id": "DOC-001"}]],  # Missing section, file_path
            "distances": [[0.2]],
        }
        mock_chroma_client.get_collection.return_value = mock_collection

        results = retrieve("test query", collection=mock_collection)

        assert len(results) == 1
        assert results[0].metadata.get("doc_id") == "DOC-001"


# ---------------------------------------------------------------------------
# Tests: Usage Logging
# ---------------------------------------------------------------------------


class TestUsageLogging:
    """Tests for usage log output."""

    def test_log_usage_writes_jsonl(self, tmp_path):
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="test query",
            top_k=3,
            filters={"doc_type": "governance"},
            use_graph=False,
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        content = log_path.read_text().strip()
        assert "test query" in content
        assert "2026-01-28T22:45:00Z" in content

    def test_log_usage_appends_multiple_entries(self, tmp_path):
        """log_usage must append entries, not overwrite."""
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="first query",
            top_k=3,
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )
        log_usage(
            query="second query",
            top_k=5,
            path=log_path,
            timestamp="2026-01-28T22:46:00Z",
        )

        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert "first query" in lines[0]
        assert "second query" in lines[1]

    def test_log_usage_creates_parent_directories(self, tmp_path):
        """log_usage must create parent directories if missing."""
        log_path = tmp_path / "nested" / "dir" / "usage.jsonl"

        log_usage(
            query="test query",
            top_k=3,
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        assert log_path.exists()
        assert "test query" in log_path.read_text()

    def test_log_usage_skips_when_path_is_none(self, tmp_path):
        """log_usage must do nothing when path is None."""
        # Should not raise any errors
        log_usage(
            query="test query",
            top_k=3,
            path=None,
        )

    def test_log_usage_includes_filters(self, tmp_path):
        """log_usage must include filters in output."""
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="test query",
            top_k=3,
            filters={"doc_type": "governance", "status": "active"},
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        import json

        entry = json.loads(log_path.read_text().strip())
        assert entry["filters"]["doc_type"] == "governance"
        assert entry["filters"]["status"] == "active"

    def test_log_usage_includes_graph_flag(self, tmp_path):
        """log_usage must include use_graph flag in output."""
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="test query",
            top_k=3,
            use_graph=True,
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        import json

        entry = json.loads(log_path.read_text().strip())
        assert entry["use_graph"] is True

    def test_log_usage_produces_valid_json(self, tmp_path):
        """log_usage must produce valid JSON entries."""
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="query with 'quotes' and \"double quotes\"",
            top_k=3,
            filters={"key": "value with\nnewline"},
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        import json

        entry = json.loads(log_path.read_text().strip())
        assert entry["query"] == "query with 'quotes' and \"double quotes\""
        assert "newline" in entry["filters"]["key"]

    def test_log_usage_sorts_keys_for_determinism(self, tmp_path):
        """log_usage must sort keys for deterministic output."""
        log_path = tmp_path / "usage.jsonl"

        log_usage(
            query="test query",
            top_k=3,
            filters={"z_key": "z", "a_key": "a"},
            path=log_path,
            timestamp="2026-01-28T22:45:00Z",
        )

        content = log_path.read_text().strip()
        # Keys should be sorted: filters, query, top_k, ts, use_graph
        assert content.index('"filters"') < content.index('"query"')
        assert content.index('"query"') < content.index('"top_k"')
