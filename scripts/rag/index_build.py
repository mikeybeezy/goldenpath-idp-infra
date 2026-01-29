#!/usr/bin/env python3
"""
---
id: SCRIPT-0078
type: script
owner: platform-team
status: active
maturity: 1
last_validated: 2026-01-28
test:
  runner: pytest
  command: "pytest -q tests/unit/test_index_build.py"
  evidence: declared
dry_run:
  supported: true
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
relates_to:
  - PRD-0008-governance-rag-pipeline
  - GOV-0017-tdd-and-determinism
---
Purpose: End-to-end index build (ingest → chunk → index → graph).
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from scripts.rag.loader import load_governance_document, GovernanceDocument
from scripts.rag.chunker import chunk_document
from scripts.rag.indexer import GovernanceIndex
from scripts.rag.scope import filter_paths
from scripts.rag.graph_ingest import ingest_documents
from scripts.rag.graph_client import GraphClientConfig, Neo4jGraphClient
from scripts.rag.index_metadata import build_index_metadata, write_index_metadata


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_markdown_paths(root: Optional[Path] = None) -> List[Path]:
    """
    Collect markdown files under repo root and filter by scope.
    """
    root = root or _repo_root()
    candidates = list(root.rglob("*.md"))
    allowed = filter_paths(candidates)
    return sorted(allowed)


def load_documents(paths: List[Path]) -> Tuple[List[GovernanceDocument], List[Dict[str, Any]]]:
    docs: List[GovernanceDocument] = []
    errors: List[Dict[str, Any]] = []
    for path in paths:
        try:
            docs.append(load_governance_document(path))
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
            continue
    return docs, errors


def write_index_errors(path: Path, errors: List[Dict[str, Any]]) -> None:
    """
    Write ingestion errors to a JSON artifact for visibility.
    """
    if not errors:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"error_count": len(errors), "errors": errors}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _graph_client_from_env() -> Optional[Neo4jGraphClient]:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    database = os.getenv("NEO4J_DATABASE")
    if not uri or not user or not password:
        return None
    config = GraphClientConfig(uri=uri, user=user, password=password, database=database)
    return Neo4jGraphClient(config)


def build_index(root: Optional[Path] = None, metadata_path: Optional[Path] = None) -> int:
    """
    Build vector index and ingest graph edges from governance docs.

    Returns:
        Number of documents indexed.
    """
    root = root or _repo_root()
    paths = collect_markdown_paths(root)
    docs, errors = load_documents(paths)

    index = GovernanceIndex()
    chunk_count = 0
    for doc in docs:
        chunks = chunk_document(doc)
        chunk_count += index.add(chunks)

    graph_client = _graph_client_from_env()
    if graph_client is not None:
        ingest_documents(docs, graph_client)
        graph_client.close()

    if errors:
        error_path = root / "reports" / "index_errors.json"
        write_index_errors(error_path, errors)

    meta_path = metadata_path or (root / "reports" / "index_metadata.json")
    write_index_metadata(meta_path, build_index_metadata(document_count=len(docs)))

    return chunk_count
