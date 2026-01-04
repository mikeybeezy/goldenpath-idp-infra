---
id: ADR-0082
title: Platform Graph RAG Strategy
type: adr
owner: platform-team
status: proposed
risk_profile:
  production_impact: none
  security_risk: low
  coupling_risk: low
lifecycle:
  supported_until: 2027-01-01
  breaking_change: false
relates_to:
  - ADR-0081
  - METADATA_STRATEGY
---

# ADR-0082: Platform Graph RAG Strategy

## Context
We have established a "Metadata Fabric" (ADR-0081) that links our documentation (ADRs, Changelogs) and infrastructure (Terraform Tags).
Standard RAG (Vector Search) is insufficient for complex platform queries because it lacks "reasoning" across these links.
We need a strategy to enable **Graph RAG**—allowing AI agents to traverse relationships (e.g., "Find all Services owned by Team X that are over budget").

## Options Considered
1.  **Vector Only (Standard RAG):** Good for "How do I...?" queries. Fails at "What is the impact of...?" queries.
2.  **Graph RAG (Vector + Knowledge Graph):** Combines semantic search with structured graph traversal.

## Decision
We will adopt **Graph RAG** as the target architecture for our internal developer platform AI capabilities.
Our *Metadata Schema* is the schema for this graph.

### The Graph Model
*   **Nodes:**
    *   **Documents:** ADRs, Changelogs, Runbooks Policy.
    *   **Infrastructure:** Clusters, VPCs, Services (from Terraform State).
    *   **Entities:** Teams, Owners, Cost Centers.
*   **Edges:**
    *   `relates_to` (Doc -> Doc)
    *   `implements` (Code -> Doc)
    *   `owned_by` (Resource -> Team)
    *   `governed_by` (Resource -> Policy)

### Implementation Phases
1.  **Phase 1: Structure (Done):** Enforce metadata schema in all markdowns and tags.
2.  **Phase 2: Ingestion (Next):** Build a pipeline to parse `.md` frontmatter and `.tfstate` into a Graph Database (e.g., Neo4j, NetworkX, or in-memory implementation like Microsoft GraphRAG).
3.  **Phase 3: Querying:** Expose a "Platform Copilot" interface that targets this graph.

## Consequences
*   **Positive:** Enables high-order reasoning ("Impact Analysis", "Audit", "Cost Optimization").
*   **Negative:** Requires maintaining the graph integrity (hence `validate-metadata.py` is critical).
