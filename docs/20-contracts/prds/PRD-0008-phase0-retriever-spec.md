---
id: PRD-0008-phase0-retriever-spec
title: PRD-0008 Phase 0 Retriever Spec (Graph-Enabled)
type: documentation
relates_to:
  - PRD-0008-governance-rag-pipeline
status: draft
---

# PRD-0008 Phase 0 Retriever Spec (Graph-Enabled)

**Note:** The content below is a verbatim capture of the extended Product Spec / Requirement Spec for Phase 0 retriever with graph retrieval.

---

**Product Spec: Phase 0 Retriever (CLI + Graph Retrieval)**

**Purpose**
Provide a deterministic CLI query tool that retrieves top‑N governance chunks with citations by combining **vector similarity** and **graph relationships**, to validate the “Agentic Graph RAG” model in Phase 0.

**Primary Users**
- Platform team engineers
- Governance owners (ADRs/PRDs/policies)

**Scope (Phase 0)**
- Local CLI only
- Vector index + Neo4j graph used in retrieval
- Returns citations (file + heading)
- Supports metadata filters
- Logs usage (query + timestamp)

**Out of Scope (Phase 0)**
- Web/API service
- Multi‑repo federation
- Automated re‑ranking pipelines (beyond basic merge rules)

---

**Requirement Spec**

**Functional Requirements**

1. **Query Execution (Vector Path)**
   - Input: `query` string
   - Output: top‑K chunks with `text`, `file_path`, `section`, `score`
2. **Query Execution (Graph Path)**
   - Input: `query` string or `doc_id` target
   - Output: related documents via graph edges (`relates_to`, `depends_on`, etc.)
3. **Merge Strategy**
   - Combine vector + graph results into one ranked list.
   - Must expose `source` per result: `vector` | `graph` | `both`.
4. **Citations**
   - Each result must include `file_path` + `section` (heading).
5. **Filters**
   - Support optional filters: `doc_type`, `domain`, `lifecycle/status`, `recency`.
6. **CLI Interface**
   - Example:
     ```
     python scripts/rag/query_cli.py \
       --query "What depends on GOV-0017?" \
       --top-k 5 \
       --use-graph \
       --filter doc_type=governance
     ```
7. **Usage Logging**
   - Log `{timestamp, query, filters, top_k, use_graph}` to JSONL.
8. **Determinism**
   - Same index + same graph + same query → stable ordering.

**Non‑Functional Requirements**
- **Performance:** response under 2s (local index + graph)
- **Determinism:** stable ordering for ties
- **Security:** only allowlisted paths; no secrets indexed
- **Minimal dependencies** beyond existing stack

---

**Data & Storage**

- **Vector Index:** Chroma/FAISS with persisted artifacts
- **Graph Store:** Neo4j with nodes for documents and edges for `relates_to`
- **Usage Log:** JSONL file (append‑only)

---

**Graph Retrieval Details**

**Graph Schema (Phase 0 minimum)**
- **Node:** `Document {id, title, type, file_path}`
- **Edges:** `RELATES_TO` (from frontmatter)

**Graph Query Contract**
- If query mentions a GOV/ADR/PRD ID, return its neighbors.
- If query is natural language, fallback to vector only (Phase 0).

**Merge Policy (Phase 0)**
- Default: `vector_rank + graph_boost`
- Graph edges give +X score (configurable), but vector order still stable.
- Include duplicates only once; mark `source="both"`.

---

**Error Handling**
- If graph unavailable → warn and continue vector‑only
- Invalid filters → error with usage hint
- Empty results → return empty list with no error

---

**Acceptance Criteria**
- CLI returns top‑N results with citations
- Graph neighbors appear when IDs are referenced
- Filters work
- Usage log created
- Tests cover merge logic and citations

---

**Test Requirements**
- Unit test: vector retrieval with filters
- Unit test: graph neighbor retrieval (mock Neo4j)
- Unit test: merge logic + deterministic ordering
- Golden test: output schema for a fixed query over fixture input
