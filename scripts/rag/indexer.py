#!/usr/bin/env python3
"""
---
id: SCRIPT-0072
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_indexer.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - GOV-0017-tdd-and-determinism
  - ADR-0184-rag-markdown-header-chunking
  - PRD-0008-governance-rag-pipeline
---
Purpose: RAG ChromaDB Indexer for GoldenPath governance documents.

Indexes document chunks into ChromaDB for vector similarity search.
This module handles the indexing stage of the RAG pipeline.

Phase 0 uses ChromaDB's default embedding function (all-MiniLM-L6-v2).
Phase 1+ will support custom embedding models.

Per GOV-0017: Metadata engines are determinism-critical and require test coverage.

Example:
    >>> from scripts.rag.indexer import GovernanceIndex
    >>> from scripts.rag.chunker import chunk_document
    >>> from scripts.rag.loader import load_governance_document
    >>> doc = load_governance_document("docs/GOV-0017.md")
    >>> chunks = chunk_document(doc)
    >>> index = GovernanceIndex()
    >>> index.add(chunks)
    6
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import json

try:
    import chromadb
except ImportError:
    chromadb = None  # Allow import without chromadb for testing

from scripts.rag.chunker import Chunk


# Default collection name for governance documents
DEFAULT_COLLECTION_NAME = "governance_docs"

# Default persist directory for ChromaDB
DEFAULT_PERSIST_DIR = ".chroma"


def _get_client(persist_dir: Optional[str] = None, in_memory: bool = False):
    """
    Get a ChromaDB client.

    Args:
        persist_dir: Directory for persistent storage. If None, uses DEFAULT_PERSIST_DIR.
        in_memory: If True, use in-memory client (for testing).

    Returns:
        ChromaDB client instance.
    """
    if chromadb is None:
        raise ImportError(
            "chromadb is not installed. Install with: pip install chromadb"
        )

    if in_memory:
        return chromadb.Client()

    persist_path = persist_dir or DEFAULT_PERSIST_DIR
    return chromadb.PersistentClient(path=persist_path)


def _flatten_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten metadata for ChromaDB compatibility.

    ChromaDB only supports string, int, float, and bool metadata values.
    Lists and dicts are converted to JSON strings.

    Args:
        metadata: Original metadata dictionary.

    Returns:
        Flattened metadata with ChromaDB-compatible types.
    """
    flattened = {}
    for key, value in metadata.items():
        if isinstance(value, (list, dict)):
            flattened[key] = json.dumps(value)
        elif value is None:
            flattened[key] = ""
        else:
            flattened[key] = value
    return flattened


def _generate_chunk_id(chunk: Chunk, index: int) -> str:
    """
    Generate a unique ID for a chunk.

    Format: {doc_id}_{chunk_index} or fallback to index-based ID.

    Args:
        chunk: The chunk to generate an ID for.
        index: Fallback index if chunk metadata is missing.

    Returns:
        Unique string ID for the chunk.
    """
    doc_id = chunk.metadata.get("doc_id", f"doc_{index}")
    chunk_index = chunk.metadata.get("chunk_index", index)
    return f"{doc_id}_{chunk_index}"


def create_collection(
    name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[str] = None,
    in_memory: bool = False,
):
    """
    Create or get a ChromaDB collection.

    Args:
        name: Collection name. Defaults to 'governance_docs'.
        persist_dir: Directory for persistent storage.
        in_memory: If True, use in-memory storage (for testing).

    Returns:
        ChromaDB collection.

    Example:
        >>> collection = create_collection("my_docs")
        >>> collection.name
        'my_docs'
    """
    client = _get_client(persist_dir=persist_dir, in_memory=in_memory)
    return client.get_or_create_collection(name=name)


def get_collection(
    name: str,
    persist_dir: Optional[str] = None,
    in_memory: bool = False,
):
    """
    Get an existing ChromaDB collection.

    Args:
        name: Collection name.
        persist_dir: Directory for persistent storage.
        in_memory: If True, use in-memory storage.

    Returns:
        ChromaDB collection.

    Raises:
        ValueError: If collection does not exist.
    """
    client = _get_client(persist_dir=persist_dir, in_memory=in_memory)
    return client.get_collection(name=name)


def delete_collection(
    name: str,
    persist_dir: Optional[str] = None,
    in_memory: bool = False,
):
    """
    Delete a ChromaDB collection.

    Args:
        name: Collection name to delete.
        persist_dir: Directory for persistent storage.
        in_memory: If True, use in-memory storage.
    """
    client = _get_client(persist_dir=persist_dir, in_memory=in_memory)
    client.delete_collection(name=name)


def index_chunks(
    chunks: List[Chunk],
    collection=None,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    persist_dir: Optional[str] = None,
    in_memory: bool = False,
) -> int:
    """
    Index chunks into a ChromaDB collection.

    Args:
        chunks: List of Chunk objects to index.
        collection: Optional existing collection. If None, creates/gets one.
        collection_name: Name for the collection if creating new.
        persist_dir: Directory for persistent storage.
        in_memory: If True, use in-memory storage.

    Returns:
        Number of chunks indexed.

    Example:
        >>> from scripts.rag.chunker import Chunk
        >>> chunks = [Chunk(text="Hello", metadata={"doc_id": "DOC-1", "chunk_index": 0})]
        >>> count = index_chunks(chunks)
        >>> count
        1
    """
    if not chunks:
        return 0

    if collection is None:
        collection = create_collection(
            name=collection_name,
            persist_dir=persist_dir,
            in_memory=in_memory,
        )

    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(_generate_chunk_id(chunk, i))
        documents.append(chunk.text)
        metadatas.append(_flatten_metadata(chunk.metadata))

    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(chunks)


@dataclass
class GovernanceIndex:
    """
    High-level interface for indexing governance documents.

    Provides a convenient wrapper around ChromaDB operations for
    the governance document use case.

    Attributes:
        collection_name: Name of the ChromaDB collection.
        persist_dir: Directory for persistent storage.
        in_memory: Whether to use in-memory storage.
        collection: The underlying ChromaDB collection.

    Example:
        >>> index = GovernanceIndex()
        >>> index.add(chunks)
        6
        >>> index.count()
        6
    """

    collection_name: str = DEFAULT_COLLECTION_NAME
    persist_dir: Optional[str] = None
    in_memory: bool = False
    collection: Any = field(default=None, init=False)
    _client: Any = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialize the collection after dataclass init."""
        self._client = _get_client(
            persist_dir=self.persist_dir,
            in_memory=self.in_memory,
        )
        self.collection = self._client.get_or_create_collection(
            name=self.collection_name
        )

    def add(self, chunks: List[Chunk]) -> int:
        """
        Add chunks to the index.

        Args:
            chunks: List of Chunk objects to index.

        Returns:
            Number of chunks added.
        """
        return index_chunks(chunks, collection=self.collection)

    def count(self) -> int:
        """
        Get the number of documents in the index.

        Returns:
            Number of indexed documents.
        """
        return self.collection.count()

    def clear(self):
        """
        Clear all documents from the index.

        Deletes and recreates the collection.
        """
        self._client.delete_collection(name=self.collection_name)
        self.collection = self._client.get_or_create_collection(
            name=self.collection_name
        )
