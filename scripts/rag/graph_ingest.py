#!/usr/bin/env python3
"""
---
id: SCRIPT-0075
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_graph_ingest.py"
  evidence: declared
dry_run:
  supported: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - ADR-0185-graphiti-agent-memory-framework
  - GOV-0017-tdd-and-determinism
---
Purpose: Graph ingestion for governance documents (Neo4j).

Takes GovernanceDocument objects and upserts document nodes plus
RELATES_TO edges into Neo4j via graph_client.
"""

from typing import Iterable, Dict, Any, List

from scripts.rag.loader import GovernanceDocument


DEFAULT_RELATIONSHIP = "RELATES_TO"


def _document_props(doc: GovernanceDocument) -> Dict[str, Any]:
    """Build graph properties from a governance document."""
    metadata = doc.metadata or {}
    return {
        "id": metadata.get("id"),
        "title": metadata.get("title"),
        "type": metadata.get("type"),
        "domain": metadata.get("domain"),
        "lifecycle": metadata.get("lifecycle"),
        "status": metadata.get("status"),
        "file_path": metadata.get("file_path") or str(doc.source_path),
    }


def _normalize_relates_to(value: Any) -> List[str]:
    """Normalize relates_to metadata to a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return [str(value)]


def ingest_documents(documents: Iterable[GovernanceDocument], graph_client) -> int:
    """
    Ingest governance documents into the graph.

    Args:
        documents: Iterable of GovernanceDocument objects.
        graph_client: Graph client with upsert_document and relate_documents methods.

    Returns:
        Count of documents ingested.
    """
    count = 0
    for doc in documents:
        props = _document_props(doc)
        doc_id = props.get("id")
        if not doc_id:
            continue

        graph_client.upsert_document(doc_id, props)

        relates_to = _normalize_relates_to(doc.metadata.get("relates_to"))
        for target_id in relates_to:
            graph_client.relate_documents(doc_id, target_id, DEFAULT_RELATIONSHIP)

        count += 1

    return count
