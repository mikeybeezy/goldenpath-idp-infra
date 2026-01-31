"""
Unit tests for hybrid_retriever module.

Tests the hybrid retrieval combining vector similarity + graph traversal.
Per GOV-0017: TDD-first implementation.
"""

import pytest
from unittest.mock import MagicMock

from scripts.rag.hybrid_retriever import (
    HybridResult,
    HybridRetriever,
    expand_via_graph,
    fetch_chunks_for_docs,
)
from scripts.rag.retriever import RetrievalResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_vector_retriever():
    """Create a mock GovernanceRetriever."""
    retriever = MagicMock()
    retriever.query.return_value = []
    retriever.usage_log_path = None
    return retriever


@pytest.fixture
def mock_graph_client():
    """Create a mock Neo4j graph client."""
    client = MagicMock()
    # Mock session context manager
    session = MagicMock()
    client._driver.session.return_value.__enter__ = MagicMock(return_value=session)
    client._driver.session.return_value.__exit__ = MagicMock(return_value=None)
    session.run.return_value = []
    return client


@pytest.fixture
def sample_vector_results():
    """Sample RetrievalResult objects from vector search."""
    return [
        RetrievalResult(
            id="chunk-001",
            text="TDD requires tests before implementation.",
            metadata={"doc_id": "GOV-0017", "section": "Requirements"},
            score=0.1,
        ),
        RetrievalResult(
            id="chunk-002",
            text="Coverage target is 60% for V1.",
            metadata={"doc_id": "GOV-0017", "section": "Targets"},
            score=0.2,
        ),
        RetrievalResult(
            id="chunk-003",
            text="ADR-0182 defines TDD philosophy.",
            metadata={"doc_id": "ADR-0182", "section": "Context"},
            score=0.3,
        ),
    ]


@pytest.fixture
def sample_graph_expansion():
    """Sample graph expansion result mapping source -> related docs."""
    return {
        "GOV-0017": ["ADR-0182", "ADR-0162", "GOV-0016"],
        "ADR-0182": ["GOV-0017"],
    }


# ---------------------------------------------------------------------------
# Tests: HybridResult dataclass
# ---------------------------------------------------------------------------


class TestHybridResult:
    """Tests for HybridResult dataclass."""

    def test_hybrid_result_has_required_fields(self):
        """HybridResult must have id, text, metadata, score, source fields."""
        result = HybridResult(
            id="test-id",
            text="test text",
            metadata={"key": "value"},
            score=0.5,
            source="vector",
        )
        assert result.id == "test-id"
        assert result.text == "test text"
        assert result.metadata == {"key": "value"}
        assert result.score == 0.5
        assert result.source == "vector"

    def test_hybrid_result_defaults_related_docs_to_empty(self):
        """HybridResult must default related_docs to empty list."""
        result = HybridResult(
            id="test-id",
            text="test",
            metadata={},
            score=0.1,
            source="vector",
        )
        assert result.related_docs == []

    def test_hybrid_result_accepts_related_docs(self):
        """HybridResult must accept related_docs parameter."""
        result = HybridResult(
            id="test-id",
            text="test",
            metadata={},
            score=0.1,
            source="graph",
            related_docs=["DOC-001", "DOC-002"],
        )
        assert result.related_docs == ["DOC-001", "DOC-002"]


# ---------------------------------------------------------------------------
# Tests: expand_via_graph
# ---------------------------------------------------------------------------


class TestExpandViaGraph:
    """Tests for expand_via_graph function."""

    def test_expand_via_graph_returns_empty_for_no_doc_ids(self, mock_graph_client):
        """expand_via_graph must return empty dict for empty input."""
        result = expand_via_graph(set(), mock_graph_client)
        assert result == {}

    def test_expand_via_graph_returns_empty_for_none_client(self):
        """expand_via_graph must return empty dict when client is None."""
        result = expand_via_graph({"DOC-001"}, None)
        assert result == {}

    def test_expand_via_graph_queries_neo4j(self, mock_graph_client):
        """expand_via_graph must query Neo4j with document IDs."""
        session = MagicMock()
        mock_graph_client._driver.session.return_value.__enter__.return_value = session
        session.run.return_value = []

        expand_via_graph({"DOC-001", "DOC-002"}, mock_graph_client)

        session.run.assert_called_once()
        call_args = session.run.call_args
        assert "MATCH" in call_args[0][0]
        # Parameters passed as second positional arg
        assert "doc_ids" in call_args[0][1]

    def test_expand_via_graph_returns_related_docs(self, mock_graph_client):
        """expand_via_graph must return mapping of source to related docs."""
        session = MagicMock()
        mock_graph_client._driver.session.return_value.__enter__.return_value = session

        # Mock Neo4j result
        mock_record = MagicMock()
        mock_record.__getitem__ = lambda self, key: {
            "source": "GOV-0017",
            "related": ["ADR-0182", "ADR-0162"],
        }[key]
        session.run.return_value = [mock_record]

        result = expand_via_graph({"GOV-0017"}, mock_graph_client)

        assert "GOV-0017" in result
        assert "ADR-0182" in result["GOV-0017"]
        assert "ADR-0162" in result["GOV-0017"]

    def test_expand_via_graph_filters_by_rel_types(self, mock_graph_client):
        """expand_via_graph must filter by relationship types when provided."""
        session = MagicMock()
        mock_graph_client._driver.session.return_value.__enter__.return_value = session
        session.run.return_value = []

        expand_via_graph(
            {"DOC-001"},
            mock_graph_client,
            rel_types=["RELATES_TO", "SUPERSEDES"],
        )

        call_args = session.run.call_args
        query = call_args[0][0]
        assert "RELATES_TO" in query or "|" in query

    def test_expand_via_graph_handles_exceptions_gracefully(self, mock_graph_client):
        """expand_via_graph must return empty dict on exception."""
        session = MagicMock()
        mock_graph_client._driver.session.return_value.__enter__.return_value = session
        session.run.side_effect = Exception("Connection failed")

        result = expand_via_graph({"DOC-001"}, mock_graph_client)

        assert result == {}


# ---------------------------------------------------------------------------
# Tests: fetch_chunks_for_docs
# ---------------------------------------------------------------------------


class TestFetchChunksForDocs:
    """Tests for fetch_chunks_for_docs function."""

    def test_fetch_chunks_returns_empty_for_no_doc_ids(self, mock_vector_retriever):
        """fetch_chunks_for_docs must return empty list for no doc_ids."""
        result = fetch_chunks_for_docs([], mock_vector_retriever)
        assert result == []

    def test_fetch_chunks_queries_each_doc_id(
        self, mock_vector_retriever, sample_vector_results
    ):
        """fetch_chunks_for_docs must query for each document ID."""
        mock_vector_retriever.query.return_value = [sample_vector_results[0]]

        fetch_chunks_for_docs(["DOC-001", "DOC-002"], mock_vector_retriever)

        assert mock_vector_retriever.query.call_count == 2

    def test_fetch_chunks_deduplicates_by_chunk_id(self, mock_vector_retriever):
        """fetch_chunks_for_docs must deduplicate by chunk ID."""
        same_chunk = RetrievalResult(
            id="same-chunk",
            text="same content",
            metadata={"doc_id": "DOC-001"},
            score=0.1,
        )
        mock_vector_retriever.query.return_value = [same_chunk]

        result = fetch_chunks_for_docs(["DOC-001", "DOC-002"], mock_vector_retriever)

        # Should only include the chunk once despite two queries
        assert len(result) == 1
        assert result[0].id == "same-chunk"

    def test_fetch_chunks_handles_query_exceptions(self, mock_vector_retriever):
        """fetch_chunks_for_docs must skip doc_ids that raise exceptions."""
        mock_vector_retriever.query.side_effect = Exception("Query failed")

        result = fetch_chunks_for_docs(["DOC-001"], mock_vector_retriever)

        assert result == []


# ---------------------------------------------------------------------------
# Tests: HybridRetriever initialization
# ---------------------------------------------------------------------------


class TestHybridRetrieverInit:
    """Tests for HybridRetriever initialization."""

    def test_hybrid_retriever_accepts_vector_retriever(self, mock_vector_retriever):
        """HybridRetriever must accept custom vector retriever."""
        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        assert retriever.vector_retriever == mock_vector_retriever

    def test_hybrid_retriever_accepts_graph_client(
        self, mock_vector_retriever, mock_graph_client
    ):
        """HybridRetriever must accept custom graph client."""
        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=mock_graph_client,
        )
        assert retriever.graph_client == mock_graph_client

    def test_hybrid_retriever_defaults_expand_depth_to_one(self, mock_vector_retriever):
        """HybridRetriever must default expand_depth to 1."""
        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        assert retriever.expand_depth == 1

    def test_hybrid_retriever_close_closes_auto_created_client(
        self, mock_vector_retriever, mock_graph_client
    ):
        """HybridRetriever.close must close auto-created graph client."""
        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=mock_graph_client,
        )
        retriever._auto_close_graph = True

        retriever.close()

        mock_graph_client.close.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: HybridRetriever.query
# ---------------------------------------------------------------------------


class TestHybridRetrieverQuery:
    """Tests for HybridRetriever.query method."""

    def test_query_returns_hybrid_results(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query must return list of HybridResult objects."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query("test query")

        assert len(results) > 0
        assert all(isinstance(r, HybridResult) for r in results)

    def test_query_marks_vector_results_as_source_vector(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query must mark results from vector search with source='vector'."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query("test query")

        for result in results:
            assert result.source == "vector"

    def test_query_passes_top_k_to_vector_retriever(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query must pass top_k parameter to vector retriever."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        retriever.query("test query", top_k=10)

        mock_vector_retriever.query.assert_called_with(
            query_text="test query",
            top_k=10,
            filters=None,
        )

    def test_query_passes_filters_to_vector_retriever(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query must pass filters parameter to vector retriever."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        retriever.query("test query", filters={"doc_type": "governance"})

        mock_vector_retriever.query.assert_called_with(
            query_text="test query",
            top_k=5,  # Default
            filters={"doc_type": "governance"},
        )

    def test_query_skips_graph_when_expand_graph_false(
        self, mock_vector_retriever, mock_graph_client, sample_vector_results
    ):
        """query must skip graph expansion when expand_graph=False."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=mock_graph_client,
        )
        retriever.query("test query", expand_graph=False)

        # Graph client should not be used
        mock_graph_client._driver.session.assert_not_called()

    def test_query_expands_via_graph_when_enabled(
        self, mock_vector_retriever, mock_graph_client, sample_vector_results
    ):
        """query must expand via graph when expand_graph=True and client available."""
        mock_vector_retriever.query.return_value = sample_vector_results

        session = MagicMock()
        mock_graph_client._driver.session.return_value.__enter__.return_value = session
        session.run.return_value = []

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=mock_graph_client,
        )
        retriever.query("test query", expand_graph=True)

        # Graph client should be used
        mock_graph_client._driver.session.assert_called()

    def test_query_sorts_results_by_score(self, mock_vector_retriever):
        """query must return results sorted by score (ascending for distance)."""
        unsorted_results = [
            RetrievalResult(id="3", text="c", metadata={}, score=0.8),
            RetrievalResult(id="1", text="a", metadata={}, score=0.2),
            RetrievalResult(id="2", text="b", metadata={}, score=0.5),
        ]
        mock_vector_retriever.query.return_value = unsorted_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query("test query")

        scores = [r.score for r in results]
        assert scores == sorted(scores)


# ---------------------------------------------------------------------------
# Tests: HybridRetriever.query_with_citations
# ---------------------------------------------------------------------------


class TestHybridRetrieverQueryWithCitations:
    """Tests for HybridRetriever.query_with_citations method."""

    def test_query_with_citations_returns_dicts(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query_with_citations must return list of dictionaries."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query_with_citations("test query")

        assert len(results) > 0
        assert all(isinstance(r, dict) for r in results)

    def test_query_with_citations_includes_citation_field(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query_with_citations must include 'citation' field in each result."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query_with_citations("test query")

        for result in results:
            assert "citation" in result
            assert isinstance(result["citation"], str)

    def test_query_with_citations_includes_source_field(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query_with_citations must include 'source' field (vector/graph)."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query_with_citations("test query")

        for result in results:
            assert "source" in result
            assert result["source"] in ["vector", "graph", "both"]

    def test_query_with_citations_includes_related_docs(
        self, mock_vector_retriever, sample_vector_results
    ):
        """query_with_citations must include 'related_docs' field."""
        mock_vector_retriever.query.return_value = sample_vector_results

        retriever = HybridRetriever(
            vector_retriever=mock_vector_retriever,
            graph_client=None,
        )
        results = retriever.query_with_citations("test query")

        for result in results:
            assert "related_docs" in result
            assert isinstance(result["related_docs"], list)
