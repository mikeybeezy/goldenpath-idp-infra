"""
Unit tests for RAG ChromaDB indexer.

Tests the indexer module's ability to:
- Create and manage ChromaDB collections
- Index chunks with text and metadata
- Handle duplicate document IDs
- Support collection lifecycle operations

Per GOV-0017: "Nothing that generates infrastructure, parses config, or emits
scaffolds may change without tests."

References:
- GOV-0017: TDD and Determinism Policy
- PRD-0008: Governance RAG Pipeline
"""

import pytest
from unittest.mock import MagicMock, patch

# Import will fail until indexer.py is implemented (RED phase)
from scripts.rag.indexer import (
    create_collection,
    index_chunks,
    get_collection,
    delete_collection,
    GovernanceIndex,
)
from scripts.rag.chunker import Chunk


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    """Create sample chunks for indexing."""
    return [
        Chunk(
            text="## Purpose\n\nThis policy defines testing requirements.",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Purpose",
                "chunk_index": 0,
            },
        ),
        Chunk(
            text="## Core Principle\n\nTests are executable contracts.",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Core Principle",
                "chunk_index": 1,
            },
        ),
        Chunk(
            text="## Coverage\n\nTarget 60% for V1.",
            metadata={
                "doc_id": "GOV-0017",
                "doc_title": "TDD Policy",
                "section": "Coverage",
                "chunk_index": 2,
            },
        ),
    ]


@pytest.fixture
def mock_chroma_client():
    """Create a mock ChromaDB client."""
    with patch("scripts.rag.indexer.chromadb") as mock_chromadb:
        mock_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_chromadb.Client.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_collection():
    """Create a mock ChromaDB collection."""
    collection = MagicMock()
    collection.name = "governance_docs"
    collection.count.return_value = 0
    return collection


# ---------------------------------------------------------------------------
# Tests: Collection Management
# ---------------------------------------------------------------------------


class TestCollectionManagement:
    """Tests for ChromaDB collection management."""

    def test_create_collection_returns_collection(self, mock_chroma_client):
        """create_collection must return a collection object."""
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        collection = create_collection("test_collection")

        assert collection is not None
        mock_chroma_client.get_or_create_collection.assert_called_once()

    def test_create_collection_uses_provided_name(self, mock_chroma_client):
        """create_collection must use the provided collection name."""
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        create_collection("my_custom_collection")

        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "my_custom_collection"

    def test_create_collection_default_name(self, mock_chroma_client):
        """create_collection must use default name if none provided."""
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        create_collection()

        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "governance_docs"

    def test_get_collection_returns_existing(self, mock_chroma_client):
        """get_collection must return an existing collection."""
        mock_collection = MagicMock()
        mock_chroma_client.get_collection.return_value = mock_collection

        collection = get_collection("existing_collection")

        assert collection is not None
        mock_chroma_client.get_collection.assert_called_with(name="existing_collection")

    def test_delete_collection_removes_collection(self, mock_chroma_client):
        """delete_collection must delete the specified collection."""
        delete_collection("test_collection")

        mock_chroma_client.delete_collection.assert_called_with(name="test_collection")


# ---------------------------------------------------------------------------
# Tests: Indexing Chunks
# ---------------------------------------------------------------------------


class TestIndexingChunks:
    """Tests for indexing chunks into ChromaDB."""

    def test_index_chunks_adds_to_collection(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must add chunks to the collection."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(sample_chunks, collection=mock_collection)

        mock_collection.add.assert_called_once()

    def test_index_chunks_includes_text(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must include chunk text as documents."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(sample_chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        documents = call_args[1]["documents"]
        assert len(documents) == 3
        assert "## Purpose" in documents[0]

    def test_index_chunks_includes_metadata(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must include chunk metadata."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(sample_chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        metadatas = call_args[1]["metadatas"]
        assert len(metadatas) == 3
        assert metadatas[0]["doc_id"] == "GOV-0017"
        assert metadatas[0]["section"] == "Purpose"

    def test_index_chunks_generates_unique_ids(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must generate unique IDs for each chunk."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(sample_chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        ids = call_args[1]["ids"]
        assert len(ids) == 3
        assert len(set(ids)) == 3  # All IDs are unique

    def test_index_chunks_id_format(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must use doc_id and chunk_index in ID format."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(sample_chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        ids = call_args[1]["ids"]
        # IDs should follow pattern: {doc_id}_{chunk_index}
        assert "GOV-0017_0" in ids[0] or "GOV-0017" in ids[0]

    def test_index_chunks_returns_count(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """index_chunks must return the number of indexed chunks."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        result = index_chunks(sample_chunks, collection=mock_collection)

        assert result == 3

    def test_index_empty_chunks_returns_zero(
        self, mock_chroma_client, mock_collection
    ):
        """index_chunks must return 0 for empty chunk list."""
        result = index_chunks([], collection=mock_collection)

        assert result == 0
        mock_collection.add.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: GovernanceIndex Class
# ---------------------------------------------------------------------------


class TestGovernanceIndex:
    """Tests for the GovernanceIndex convenience class."""

    def test_governance_index_creates_collection(self, mock_chroma_client):
        """GovernanceIndex must create a collection on init."""
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index = GovernanceIndex()

        assert index.collection is not None

    def test_governance_index_custom_name(self, mock_chroma_client):
        """GovernanceIndex must support custom collection name."""
        mock_collection = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        GovernanceIndex(collection_name="custom_index")

        call_args = mock_chroma_client.get_or_create_collection.call_args
        assert call_args[1]["name"] == "custom_index"

    def test_governance_index_add_chunks(
        self, mock_chroma_client, mock_collection, sample_chunks
    ):
        """GovernanceIndex.add must index chunks."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index = GovernanceIndex()
        count = index.add(sample_chunks)

        assert count == 3
        mock_collection.add.assert_called_once()

    def test_governance_index_count(self, mock_chroma_client, mock_collection):
        """GovernanceIndex.count must return collection size."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_collection.count.return_value = 42

        index = GovernanceIndex()

        assert index.count() == 42

    def test_governance_index_clear(self, mock_chroma_client, mock_collection):
        """GovernanceIndex.clear must delete and recreate collection."""
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index = GovernanceIndex()
        index.clear()

        mock_chroma_client.delete_collection.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: Metadata Handling
# ---------------------------------------------------------------------------


class TestMetadataHandling:
    """Tests for metadata handling during indexing."""

    def test_flattens_list_metadata(self, mock_chroma_client, mock_collection):
        """Indexer must flatten list metadata to strings for ChromaDB."""
        chunks = [
            Chunk(
                text="Test content",
                metadata={
                    "doc_id": "DOC-001",
                    "relates_to": ["REF-001", "REF-002"],
                    "chunk_index": 0,
                },
            )
        ]
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        metadatas = call_args[1]["metadatas"]
        # ChromaDB doesn't support lists, so they should be stringified
        relates_to = metadatas[0].get("relates_to")
        assert isinstance(relates_to, str)
        assert "REF-001" in relates_to

    def test_preserves_string_metadata(self, mock_chroma_client, mock_collection):
        """Indexer must preserve string metadata as-is."""
        chunks = [
            Chunk(
                text="Test content",
                metadata={
                    "doc_id": "DOC-001",
                    "section": "Introduction",
                    "chunk_index": 0,
                },
            )
        ]
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        metadatas = call_args[1]["metadatas"]
        assert metadatas[0]["section"] == "Introduction"

    def test_preserves_numeric_metadata(self, mock_chroma_client, mock_collection):
        """Indexer must preserve numeric metadata."""
        chunks = [
            Chunk(
                text="Test content",
                metadata={
                    "doc_id": "DOC-001",
                    "chunk_index": 5,
                    "header_level": 2,
                },
            )
        ]
        mock_chroma_client.get_or_create_collection.return_value = mock_collection

        index_chunks(chunks, collection=mock_collection)

        call_args = mock_collection.add.call_args
        metadatas = call_args[1]["metadatas"]
        assert metadatas[0]["chunk_index"] == 5
        assert metadatas[0]["header_level"] == 2
