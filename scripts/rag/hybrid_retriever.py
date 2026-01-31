#!/usr/bin/env python3
"""
---
id: SCRIPT-0079
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-29
test:
  runner: pytest
  command: "pytest -q tests/unit/test_hybrid_retriever.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
  - SCRIPT-0073-retriever
  - SCRIPT-0074-graph-client
---
Purpose: Hybrid retriever combining vector similarity + graph traversal.

Queries ChromaDB for semantic matches, then expands results using
Neo4j graph relationships (RELATES_TO, SUPERSEDES, etc.).

Phase 1 implementation per PRD-0008.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set

from scripts.rag.retriever import (
    GovernanceRetriever,
    RetrievalResult,
    format_citation,
    log_usage,
    DEFAULT_TOP_K,
)

try:
    from scripts.rag.graph_client import create_client_from_env, Neo4jGraphClient
except ImportError:
    Neo4jGraphClient = None


@dataclass
class HybridResult:
    """Result from hybrid retrieval with source tracking."""

    id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    source: str  # "vector", "graph", or "both"
    related_docs: List[str] = field(default_factory=list)


def _graph_client_from_env() -> Optional["Neo4jGraphClient"]:
    """Create graph client if env vars are set."""
    if Neo4jGraphClient is None:
        return None
    uri = os.getenv("NEO4J_URI")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not password:
        return None
    try:
        return create_client_from_env()
    except Exception:
        return None


def expand_via_graph(
    doc_ids: Set[str],
    graph_client: "Neo4jGraphClient",
    max_depth: int = 1,
    rel_types: Optional[List[str]] = None,
) -> Dict[str, List[str]]:
    """
    Expand document IDs via graph relationships.

    Args:
        doc_ids: Set of document IDs to expand from.
        graph_client: Neo4j graph client.
        max_depth: How many hops to traverse (default: 1).
        rel_types: Relationship types to follow. Default: all.

    Returns:
        Dict mapping source doc_id to list of related doc_ids.
    """
    if not doc_ids or graph_client is None:
        return {}

    # Build Cypher query
    rel_filter = ""
    if rel_types:
        rel_filter = ":" + "|".join(rel_types)

    query = f"""
    MATCH (src:Document)-[r{rel_filter}]-(related:Document)
    WHERE src.id IN $doc_ids
    RETURN src.id AS source, collect(DISTINCT related.id) AS related
    """

    expanded = {}
    try:
        with graph_client._driver.session() as session:
            result = session.run(query, {"doc_ids": list(doc_ids)})
            for record in result:
                expanded[record["source"]] = record["related"]
    except Exception:
        pass

    return expanded


def fetch_chunks_for_docs(
    doc_ids: List[str],
    retriever: GovernanceRetriever,
    top_k_per_doc: int = 2,
) -> List[RetrievalResult]:
    """
    Fetch chunks for specific document IDs from vector store.

    Args:
        doc_ids: List of document IDs to fetch.
        retriever: GovernanceRetriever instance.
        top_k_per_doc: Max chunks per document.

    Returns:
        List of RetrievalResult objects.
    """
    results = []
    seen_ids = set()

    for doc_id in doc_ids:
        try:
            # Query with doc_id filter
            chunks = retriever.query(
                query_text=doc_id,  # Use doc_id as query for relevant chunks
                top_k=top_k_per_doc,
                filters={"doc_id": doc_id},
            )
            for chunk in chunks:
                if chunk.id not in seen_ids:
                    seen_ids.add(chunk.id)
                    results.append(chunk)
        except Exception:
            continue

    return results


@dataclass
class HybridRetriever:
    """
    Hybrid retriever combining vector similarity and graph traversal.

    Flow:
    1. Query ChromaDB for top-k semantically similar chunks
    2. Extract unique doc_ids from results
    3. Query Neo4j for related documents (1-hop)
    4. Fetch chunks for related documents
    5. Merge and rank all results

    Attributes:
        vector_retriever: GovernanceRetriever for vector search.
        graph_client: Optional Neo4j client for graph expansion.
        expand_depth: Graph traversal depth (default: 1).
        rel_types: Relationship types to follow (default: all).
    """

    vector_retriever: GovernanceRetriever = field(default_factory=GovernanceRetriever)
    graph_client: Optional[Any] = None
    expand_depth: int = 1
    rel_types: Optional[List[str]] = None
    _auto_close_graph: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Initialize graph client if not provided."""
        if self.graph_client is None:
            self.graph_client = _graph_client_from_env()
            if self.graph_client is not None:
                self._auto_close_graph = True

    def close(self):
        """Close graph client if auto-created."""
        if self._auto_close_graph and self.graph_client is not None:
            self.graph_client.close()
            self.graph_client = None

    def query(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
        expand_graph: bool = True,
        graph_top_k: int = 3,
    ) -> List[HybridResult]:
        """
        Execute hybrid query combining vector and graph retrieval.

        Args:
            query_text: The search query string.
            top_k: Number of vector results to return.
            filters: Optional metadata filters for vector search.
            expand_graph: Whether to expand via graph (default: True).
            graph_top_k: Max results from graph expansion per source doc.

        Returns:
            List of HybridResult objects, ranked by relevance.
        """
        # Step 1: Vector search
        vector_results = self.vector_retriever.query(
            query_text=query_text,
            top_k=top_k,
            filters=filters,
        )

        # Convert to HybridResult
        hybrid_results = []
        seen_chunks = set()

        for result in vector_results:
            hybrid_results.append(
                HybridResult(
                    id=result.id,
                    text=result.text,
                    metadata=result.metadata,
                    score=result.score,
                    source="vector",
                    related_docs=[],
                )
            )
            seen_chunks.add(result.id)

        # Step 2: Graph expansion (if enabled and client available)
        if expand_graph and self.graph_client is not None:
            # Extract unique doc_ids from vector results
            doc_ids = set()
            for result in vector_results:
                doc_id = result.metadata.get("doc_id")
                if doc_id:
                    doc_ids.add(doc_id)

            # Expand via graph
            expanded = expand_via_graph(
                doc_ids=doc_ids,
                graph_client=self.graph_client,
                max_depth=self.expand_depth,
                rel_types=self.rel_types,
            )

            # Collect all related doc_ids
            related_doc_ids = set()
            for source_id, related in expanded.items():
                related_doc_ids.update(related)
                # Update source results with related docs
                for hr in hybrid_results:
                    if hr.metadata.get("doc_id") == source_id:
                        hr.related_docs = related

            # Remove doc_ids we already have
            new_doc_ids = related_doc_ids - doc_ids

            # Fetch chunks for new related documents
            if new_doc_ids:
                graph_chunks = fetch_chunks_for_docs(
                    doc_ids=list(new_doc_ids)[: graph_top_k * len(doc_ids)],
                    retriever=self.vector_retriever,
                    top_k_per_doc=2,
                )

                # Add graph-sourced results
                for chunk in graph_chunks:
                    if chunk.id not in seen_chunks:
                        seen_chunks.add(chunk.id)
                        hybrid_results.append(
                            HybridResult(
                                id=chunk.id,
                                text=chunk.text,
                                metadata=chunk.metadata,
                                score=chunk.score
                                + 0.5,  # Slight penalty for graph-only
                                source="graph",
                                related_docs=[],
                            )
                        )

        # Log usage
        log_usage(
            query=query_text,
            top_k=top_k,
            filters=filters,
            use_graph=expand_graph and self.graph_client is not None,
            path=self.vector_retriever.usage_log_path,
        )

        # Sort by score (lower is better for distance-based)
        hybrid_results.sort(key=lambda x: x.score)

        return hybrid_results

    def query_with_citations(
        self,
        query_text: str,
        top_k: int = DEFAULT_TOP_K,
        filters: Optional[Dict[str, Any]] = None,
        expand_graph: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query and return results with formatted citations.

        Args:
            query_text: The search query string.
            top_k: Number of results to return.
            filters: Optional metadata filters.
            expand_graph: Whether to expand via graph.

        Returns:
            List of dicts with result details and citations.
        """
        results = self.query(
            query_text=query_text,
            top_k=top_k,
            filters=filters,
            expand_graph=expand_graph,
        )

        return [
            {
                "id": result.id,
                "text": result.text,
                "citation": format_citation(
                    RetrievalResult(
                        id=result.id,
                        text=result.text,
                        metadata=result.metadata,
                        score=result.score,
                    )
                ),
                "score": result.score,
                "source": result.source,
                "related_docs": result.related_docs,
            }
            for result in results
        ]
