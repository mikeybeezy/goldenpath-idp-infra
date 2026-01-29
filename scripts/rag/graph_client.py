#!/usr/bin/env python3
"""
---
id: SCRIPT-0074
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
Purpose: Neo4j graph client for governance document relationships.

Provides a minimal client for upserting document nodes and relates_to edges.
Graphiti is expected to share the same Neo4j backend in Phase 1+, but Phase 0
ingestion uses direct Neo4j operations.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None  # Allow import without neo4j for testing


@dataclass
class GraphClientConfig:
    """Connection configuration for Neo4j."""

    uri: str
    user: str
    password: str
    database: Optional[str] = None


class Neo4jGraphClient:
    """
    Minimal Neo4j client for document node and edge operations.

    This client is intentionally small to keep Phase 0 deterministic
    and testable. Graphiti integration will layer on top of the same
    Neo4j backend in Phase 1.
    """

    def __init__(self, config: GraphClientConfig):
        if GraphDatabase is None:
            raise ImportError(
                "neo4j is not installed. Install with: pip install neo4j"
            )
        self._config = config
        self._driver = GraphDatabase.driver(
            config.uri, auth=(config.user, config.password)
        )

    def close(self) -> None:
        """Close the underlying Neo4j driver."""
        if self._driver:
            self._driver.close()

    def upsert_document(self, doc_id: str, props: Dict[str, Any]) -> None:
        """
        Upsert a document node by id.

        Args:
            doc_id: Document id to upsert.
            props: Properties to set on the node.
        """
        if not doc_id:
            return
        query = (
            "MERGE (d:Document {id: $id}) "
            "SET d += $props "
            "RETURN d.id"
        )
        params = {"id": doc_id, "props": props}
        self._run(query, params)

    def relate_documents(self, src_id: str, dst_id: str, rel_type: str) -> None:
        """
        Create a relationship between two documents.

        Args:
            src_id: Source document id.
            dst_id: Target document id.
            rel_type: Relationship type (e.g., RELATES_TO).
        """
        if not src_id or not dst_id:
            return
        query = (
            "MERGE (a:Document {id: $src}) "
            "MERGE (b:Document {id: $dst}) "
            f"MERGE (a)-[:{rel_type}]->(b)"
        )
        params = {"src": src_id, "dst": dst_id}
        self._run(query, params)

    def _run(self, query: str, params: Dict[str, Any]) -> None:
        """Execute a Cypher query with optional database selection."""
        if self._config.database:
            with self._driver.session(database=self._config.database) as session:
                session.run(query, params)
        else:
            with self._driver.session() as session:
                session.run(query, params)

    def health_check(self) -> Dict[str, Any]:
        """Check connection to Neo4j and return server info."""
        try:
            with self._driver.session() as session:
                result = session.run("RETURN 1 AS ok")
                result.single()
            info = self._driver.get_server_info()
            return {
                "status": "healthy",
                "server_version": info.agent if info else "unknown",
                "address": str(info.address) if info else self._config.uri,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


def create_client_from_env() -> Neo4jGraphClient:
    """
    Create a Neo4jGraphClient from environment variables.

    Environment variables:
        NEO4J_URI: Bolt URI (default: bolt://localhost:7687)
        NEO4J_USER: Username (default: neo4j)
        NEO4J_PASSWORD: Password (required)
        NEO4J_DATABASE: Database name (optional)
    """
    import os

    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE")

    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable is required")

    config = GraphClientConfig(uri=uri, user=user, password=password, database=database)
    return Neo4jGraphClient(config)


# Alias for convenience
Neo4jClient = Neo4jGraphClient


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "health":
        client = create_client_from_env()
        print(client.health_check())
        client.close()
    else:
        print("Usage: python -m scripts.rag.graph_client health")
