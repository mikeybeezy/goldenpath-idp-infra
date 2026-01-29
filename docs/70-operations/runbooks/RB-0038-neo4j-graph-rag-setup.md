---
id: RB-0038
title: Neo4j Graph RAG Local Setup
type: runbook
domain: operations
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: restart-instance
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - PRD-0008-governance-rag-pipeline
  - PRD-0010-governance-rag-mcp-server
  - ADR-0185-graphiti-temporal-memory
  - DOCS_RUNBOOKS_README
supersedes: []
superseded_by: []
tags:
  - neo4j
  - graph-rag
  - local-dev
inheritance: {}
status: active
supported_until: '2028-01-01'
date: 2026-01-29
---

# RB-0038: Neo4j Graph RAG Local Setup

## Purpose

Set up a local Neo4j instance for the Governance Graph RAG pipeline. This enables graph-based queries like "What documents relate to GOV-0017?" that complement vector similarity search.

## Prerequisites

- Neo4j Desktop installed ([download](https://neo4j.com/download/))
- Python 3.11+ with `neo4j` package (`pip install neo4j`)
- Governance RAG scripts from `scripts/rag/`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Hybrid RAG Query                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   Question ──┬──► Vector Search (ChromaDB)              │
│              │    "semantic similarity"                  │
│              │                                           │
│              └──► Graph Traversal (Neo4j)               │
│                   "structural relationships"             │
│                                                          │
│   Results merged by relevance + relationship strength   │
└─────────────────────────────────────────────────────────┘
```

## Neo4j Desktop Setup

### Step 1: Create Project and Database

1. Open **Neo4j Desktop**
2. Click **New** → **Create project**
3. Name: `goldenpath-governance`
4. Click **Add** → **Local DBMS**
5. Configure:
   - Name: `governance-graph`
   - Password: `governanceRAG2026` (or choose your own)
   - Version: `5.x` (latest stable)
6. Click **Create**

### Step 2: Start the Database

1. Click the **Start** button on `governance-graph`
2. Wait for status: **Running**
3. Note the connection details:
   - **Bolt URL:** `bolt://localhost:7687`
   - **HTTP URL:** `http://localhost:7474` (Browser)
   - **User:** `neo4j`
   - **Password:** (what you set above)

### Step 3: Verify via Browser

1. Click **Open** → **Neo4j Browser**
2. Connect with credentials
3. Run test query:
   ```cypher
   RETURN "Neo4j is running!" AS status
   ```

## Environment Configuration

### Option A: Export Variables (Session)

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="governanceRAG2026"
```

### Option B: .env File (Persistent)

Create `.env` in project root:

```bash
# .env (DO NOT COMMIT - add to .gitignore)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=governanceRAG2026
```

Load with:
```bash
source .env
# or use python-dotenv in scripts
```

### Option C: direnv (Recommended)

Create `.envrc`:
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="governanceRAG2026"
```

Then:
```bash
direnv allow
```

## Test Connection

### Python Test

```bash
python -c "
from scripts.rag.graph_client import create_client_from_env
client = create_client_from_env()
print(client.health_check())
client.close()
"
```

Expected output:
```
{'status': 'healthy', 'server_version': 'Neo4j/2025.12.1', 'address': '127.0.0.1:7687'}
```

### CLI Test

```bash
python -m scripts.rag.graph_client health
```

## Ingest Governance Documents

### Step 1: Load Documents into Graph

```bash
# Default: ingest from docs/
python -m scripts.rag.graph_ingest

# Or specify source directory
python -m scripts.rag.graph_ingest docs/
```

Expected output:

```text
Loading documents from docs/...
Loaded 690 documents (0 errors)
Connecting to Neo4j...
Neo4j status: healthy (Neo4j/2025.12.1)
Ingesting documents into graph...
Ingested 654 documents
{
  "status": "success",
  "documents_ingested": 654,
  "relationships_created": 4062,
  "errors": 0
}
```

This will:
- Create `Document` nodes for each governance file
- Extract `relates_to` edges from frontmatter
- Build relationship graph

### Step 2: Verify Ingestion

Open Neo4j Browser and run:

```cypher
// Count nodes and relationships
MATCH (d:Document) RETURN count(d) AS documents;
MATCH ()-[r:RELATES_TO]->() RETURN count(r) AS relationships;
```

Expected:
- Documents: ~690
- Relationships: ~4,062

### Step 3: Explore the Graph

```cypher
// Find documents related to GOV-0017
MATCH (d:Document {id: 'GOV-0017-tdd-and-determinism'})-[:RELATES_TO]->(related)
RETURN d.id, related.id, related.title
```

```cypher
// Find all PRDs and their dependencies
MATCH (p:Document)-[:RELATES_TO]->(dep)
WHERE p.id STARTS WITH 'PRD-'
RETURN p.id, collect(dep.id) AS dependencies
```

## Graph Schema

### Node Labels

| Label | Properties | Description |
|-------|------------|-------------|
| `Document` | id, title, type, file_path, owner, status | Governance document |

### Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| `RELATES_TO` | Document references another | GOV-0017 → ADR-0182 |
| `SUPERSEDES` | Document replaces another | ADR-0200 → ADR-0150 |
| `DEPENDS_ON` | Hard dependency | PRD-0008 → GOV-0017 |

### Indexes

Create for query performance:

```cypher
CREATE INDEX doc_id_idx FOR (d:Document) ON (d.id);
CREATE INDEX doc_type_idx FOR (d:Document) ON (d.type);
```

## Hybrid Query (Vector + Graph)

Once both ChromaDB and Neo4j are populated:

```bash
python -m scripts.rag.cli query "What are the testing requirements?" --hybrid
```

This:
1. Searches ChromaDB for semantic matches
2. Expands results via Neo4j graph traversal
3. Merges and ranks results

## Troubleshooting

### Connection Refused

```
neo4j.exceptions.ServiceUnavailable: Unable to connect to bolt://localhost:7687
```

**Fix:** Ensure Neo4j Desktop instance is **Running** (green dot).

### Authentication Failed

```
neo4j.exceptions.AuthError: Invalid credentials
```

**Fix:** Check `NEO4J_PASSWORD` matches what you set in Neo4j Desktop.

### Out of Memory

```
java.lang.OutOfMemoryError: Java heap space
```

**Fix:** In Neo4j Desktop → Settings → increase heap:
```
dbms.memory.heap.initial_size=512m
dbms.memory.heap.max_size=1G
```

### Port Conflict

```
Address already in use: 7687
```

**Fix:** Another Neo4j instance is running. Stop it or change port:
```
server.bolt.listen_address=:7688
```

## Resource Usage

| Resource | Default | Recommended (Dev) |
|----------|---------|-------------------|
| Heap Memory | 512MB | 512MB - 1GB |
| Page Cache | 512MB | 256MB |
| Disk | ~50MB | ~100MB (with data) |

## Cleanup

### Stop Instance

In Neo4j Desktop: Click **Stop** on the instance.

### Delete Instance

1. Stop the instance
2. Click **...** → **Remove**
3. Confirm deletion

### Clear Data Only

In Neo4j Browser:
```cypher
MATCH (n) DETACH DELETE n
```

## References

- [PRD-0008: Governance RAG Pipeline](../../20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
- [PRD-0010: MCP Server](../../20-contracts/prds/PRD-0010-governance-rag-mcp-server.md)
- [ADR-0185: Graphiti Temporal Memory](../../adrs/ADR-0185-graphiti-temporal-memory.md)
- [Neo4j Desktop Documentation](https://neo4j.com/docs/desktop-manual/current/)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-01-29 | platform-team | Initial version |
