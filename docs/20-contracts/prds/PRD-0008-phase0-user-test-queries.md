---
id: PRD-0008-phase0-user-test-queries
title: "PRD-0008 Phase 0 User Test Queries"
type: documentation
owner: platform-team
status: draft
schema_version: 1
relates_to:
  - PRD-0008-governance-rag-pipeline
  - PRD-0008-phase0-retriever-spec
---

# PRD-0008 Phase 0 User Test Queries

Use these sample queries to validate Phase 0 retrieval quality and citations.

## How to Run

```bash
python -m scripts.rag.cli query "<query>"
```

## Sample Queries (8)

1. What are the testing requirements in GOV-0017?
2. What does ADR-0184 decide about chunking?
3. What are the coverage targets in GOV-0017?
4. Which documents relate to GOV-0017?
5. What is excluded from indexing in PRD-0008?
6. What are the Phase 0 acceptance criteria in PRD-0008?
7. What is the rollback strategy for PRD-0008?
8. What is the purpose of the Agentic Graph RAG pipeline?

## Expected Checks

- Each result includes citations (file path + section heading).
- Results are relevant and not empty.
- Deterministic ordering for repeat runs.
