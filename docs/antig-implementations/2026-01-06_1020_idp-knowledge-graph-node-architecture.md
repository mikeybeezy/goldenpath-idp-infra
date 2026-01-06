---
id: 2026-01-06_1020_idp-knowledge-graph-node-architecture
title: IDP Knowledge Graph Node Architecture
type: implementation-plan
category: architecture
version: '1.0'
owner: platform-team
status: approved
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: '2028-01-01'
  breaking_change: false
relates_to:
  - ADR-0110
---

# IDP Knowledge Graph Node Architecture

Implement a structured, graph-based entity model that transforms disconnected YAML sidecars into a unified Knowledge Graph. This architecture enables automated impact analysis, compliance auditing, and autonomous agent reasoning.

## Proposed Node Architecture

We will move from **"Files with tags"** to **"Entities with Edges"**.

### 1. Minimal Node Types (Practical Schema)
| Node Category | Description | Responsibility |
| :--- | :--- | :--- |
| **Registry** | ECR / Container Repos | The "Vault" for artifacts. |
| **Application** | Microservices / Repos | The functional code consuming resources. |
| **Infra** | EKS, VPC, Cluster | The foundational physical/virtual resources. |
| **Dockerfile** | Build Definition | The "Recipe" for the application. |
| **Image** | Container Artifact | The immutable "Result" stored in a Registry. |
| **Workflow** | GitHub Actions | The automation path (Create/Destroy). |
| **Environment** | Dev, Test, Prod | The deployment context and blast radius. |
| **Team** | Platform / App Teams | Ownership and accountability. |
| **ADR** | Decisions / Architecture | The "Why" behind the state. |
| **Policy** | Governance Rules | The guardrails (Security/Compliance). |

## 📐 Evolution: Generic Proposal vs. Practical Suggestion

| Aspect | Initial Proposal (Generic) | Your Suggestion (Practical) |
| :--- | :--- | :--- |
| **Node Naming** | High-level (Infra, Product) | Domain-specific (Registry, App) |
| **Relationship Verbs**| Abstract (OWNS, PROV_BY) | Semantic (USED_BY, DECIDED_BY) |
| **Implementation** | Requires translation layer | Direct mapping from existing logs/YAML |
| **Target Audience** | Architecture Board | Platform Engineer / Agent |

**Conclusion**: Your suggestion eliminates "Translation Debt." By using the names we already use in the `ecr-catalog.yaml` and `.github/workflows/`, we can build the graph faster and make it more intuitive for both humans and agents.

### 2. Relationships (Practical Edges)
| From | Relationship | To |
| :--- | :--- | :--- |
| **Registry** | `OWNED_BY` | Team |
| **Registry** | `USED_BY` | Application |
| **Application** | `HOSTED_ON` | Infra |
| **Image** | `STORED_IN` | Registry |
| **Image** | `BUILT_BY` | Workflow |
| **Infra** | `OWNED_BY` | Team |
| **Infra** | `CREATED_VIA` | Workflow |
| **Any Node** | `DEPENDS_ON` | Any Node |

## 🧬 Schema Evolution Strategy

The Knowledge Graph is a **Living System**.
- **Core Nodes** (Registry, App, Team) are stable foundations.
- **Extended Nodes** (Dockerfile, Image) bridge specific domains (Supply Chain).
- **Future Nodes** (e.g., `Secret`, `Database`, `Network`) will be introduced as the "Healer" scripts learn to mine those areas.

Labels are **versioned**. If we move from `USED_BY` to `CONSUMES`, we run a migration script to update the "Edges" without breaking the "Nodes".

## 🚀 Advanced Evolutionary Patterns (Improvements)

Beyond static mapping, we can improve the graph with:

1.  **Telemetry-Linked Nodes (Live State)**:
    - `Registry` node pulls live storage data from CloudWatch.
    - `Image` node links to the latest Vulnerability Scan result (Pass/Fail).
2.  **Temporal Dimensions (Time Travel)**:
    - Adding `VALID_FROM` and `VALID_TO` metadata to edges to track how architecture evolved.
    - *Query:* "Show me the graph state as of Dec 1st."
3.  **Human-in-the-Loop Edges (Verification)**:
    - `Security-Team` ---**VERIFIED**---> `Image`.
    - This creates a cryptographic or audit-trail bridge between automated builds and human safety gates.

## 🤖 The Agent Layer

While **Scripts** (the "Healers") mine the data and build the graph, we introduce a **Dedicated System Agent** to act as the primary operator of the Knowledge Graph.

### Agent Responsibilities
- **Contextual Reasoning**: "I see a High-Risk ECR registry without a corresponding security ADR. I am opening a PR to link them."
- **Root Cause Analysis**: "A production apply failed. I have traced the dependencies through the graph and found the culprit: an unmerged VPC change."
- **Drift Remediation**: Automatically opening PRs to re-align "Dark Nodes" (resources found in AWS but not in the Graph).

### 3. Mapping to Existing Data

- **Catalog** (`ecr-catalog.yaml`) -> `Registry` node, `Owner`, `Risk`, `Lifecycle state`.
- **ADRs** (`docs/adrs/`) -> `DECIDED_BY` relationship, Scope, Justification.
- **Workflows** (`.github/workflows/`) -> `CREATED_VIA`, `DECOMMISSIONED_VIA`.
- **Environments** (`envs/`) -> `Promotion`, `Blast-radius context`.

## ⚖️ Path to Intelligence: Foundation vs Evolution

| Feature | Current (High-Integrity Foundation) | Proposed (Intelligence Layer) |
| :--- | :--- | :--- |
| **Data Model** | Standardized YAML Sidecars. | Unified, interlinked entity nodes. |
| **Connectivity**| Implicit (implied by path/name). | Explicit (edges like `OWNS`, `DEPENDS`). |
| **Analysis** | Fast-Grep / Sidecar Audit. | Programmatic Graph Traversal. |
| **Decisioning** | "Is metadata present?" | "Is resource aligned with ADR-0110?" |
| **Agent Role** | Data Entry & Compliance Assistant. | Autonomous Reasoning & Risk Analyst. |
| **Visibility** | Component-level Health Cards. | System-level Topology Diagrams. |

## Proposed Changes

### [Docs & Research]

#### [NEW] [docs/adrs/ADR-0110-idp-knowledge-graph-architecture.md](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0110-idp-knowledge-graph-architecture.md)
-   Define the formal schema for the Knowledge Graph.
-   Document the transition from `metadata.yaml` to JSON-LD or Graph-compatible structures.

### [Tooling]

#### [MODIFY] [scripts/extract_relationships.py](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/extract_relationships.py)
-   Upgrade to handle complex node types.
-   Implement "Edge Discovery" logic (e.g., parsing Terraform `depends_on` to create `DEPENDS_ON` edges in the graph).

#### [NEW] [scripts/graph_validator.py](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/graph_validator.py)
-   Ensure that every `Infra` node has a mandatory `OWNED_BY` relationship to an `Identity` node.
-   Verify that `Service` nodes mapped to `High Risk` have required `Security Policy` nodes linked.

## Verification Plan

### Automated Tests
- Run `extract_relationships.py` on the dev environment and verify the generated graph.
- Test the "Agent Reasoning" capability by querying the graph: *"Which Teams have orphaned ECR registries?"*

### Manual Verification
- Review the Mermaid diagram of the generated graph in `PLATFORM_HEALTH.md`.
- Validate that ADR relationships are correctly extracted from markdown headers.
