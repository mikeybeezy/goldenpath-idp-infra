# Rag_v1_ROADMAP

## V1 Usefulness Checklist (Graphiti + Agentic GraphRAG)

**A. Deterministic Answer Contract**
- [ ] Every answer follows a fixed schema: **Answer -> Evidence -> Timestamp -> Limitations -> Next step**.
- [ ] If evidence is missing, agent must **abstain** (no free-form answer).
- [ ] Evidence must include **Graphiti node/edge IDs** *and* file paths.

**B. Graphiti as Primary Evidence**
- [ ] Owners, services, policies, dependencies exist as **Graphiti nodes** with `updated_at` and `source_sha`.
- [ ] All "relates_to" and dependency edges exist in Graphiti.
- [ ] Graph query runs **before** text retrieval; text retrieval must link to graph nodes.

**C. RAG + Graph Alignment**
- [ ] Every retrieved chunk must map to a graph node or edge.
- [ ] If chunk is not graph-linked, it is excluded from answers.
- [ ] Conflicts resolve in favor of **Graph truth** (latest timestamp).

**D. VQ Determinism**
- [ ] VQ inputs are explicit (tags, telemetry, ledger entries).
- [ ] The VQ computation path is retrievable (inputs -> formula -> outputs).
- [ ] VQ answers must cite **Graphiti nodes + doc sources**.

**E. Testable Quality Gates**
- [ ] 10-20 **golden questions** with expected evidence and abstention rules.
- [ ] Graph schema validation passes (nodes/edges + required properties).
- [ ] Index build emits `index_metadata.json` and `index_errors.json`.

## How to enforce this deterministically (not just a prompt)

**1) Contract schemas**
- Define a JSON schema for answers (Answer/Evidence/Timestamp/etc.).
- Reject responses that don't match the schema.

**2) Graph validation tests**
- Unit tests: required node types and properties (`updated_at`, `source_sha`).
- Integration tests: "graph-first retrieval" and "graph-linked chunks only."

**3) Golden Q/A tests**
- Each golden question asserts:
  - evidence exists,
  - graph nodes referenced,
  - abstain if no evidence.

**4) CI gate**
- CI fails if any response lacks citations or schema compliance.
- Run goldens + graph validation + integration tests before merge.

**5) Runtime guardrails**
- If retrieval returns no graph-linked evidence, agent returns "unknown."

## Answer Contract JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RAG Answer Contract",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "answer",
    "evidence",
    "timestamp",
    "limitations",
    "next_step"
  ],
  "properties": {
    "answer": {
      "type": "string"
    },
    "evidence": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/evidenceItem"
      }
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "limitations": {
      "type": "string"
    },
    "next_step": {
      "type": "string"
    }
  },
  "oneOf": [
    {
      "properties": {
        "evidence": {
          "minItems": 1
        }
      }
    },
    {
      "properties": {
        "answer": {
          "const": "unknown"
        },
        "evidence": {
          "maxItems": 0
        }
      }
    }
  ],
  "definitions": {
    "evidenceItem": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "graph_ids",
        "file_paths"
      ],
      "properties": {
        "graph_ids": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 1
        },
        "file_paths": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 1
        },
        "excerpt": {
          "type": "string"
        },
        "source_sha": {
          "type": "string"
        }
      }
    }
  }
}
```

## Implementation References

- Added answer contract schema: `schemas/metadata/answer_contract.schema.json`
- Added golden fixtures:
  - `tests/golden/fixtures/inputs/ANSWER-CONTRACT-valid.json`
  - `tests/golden/fixtures/inputs/ANSWER-CONTRACT-invalid.json`
- Added golden tests:
  - `tests/golden/test_answer_contract_golden.py`
