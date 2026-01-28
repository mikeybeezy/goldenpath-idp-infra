---
id: EC-0017-platform-distribution-framework
title: 'EC-0017: GoldenPath Platform Distribution Framework'
type: enhancement-concept
status: draft
lifecycle: proposed
risk_profile:
  production_impact: none
  security_risk: low
  coupling_risk: medium
relates_to:
  - GOV-0020-rag-maturity-model
  - PRD-0008-governance-rag-pipeline
  - EC-0013-agent-context-architecture
tags:
  - platform
  - distribution
  - white-label
  - framework
  - reusability
version: '1.0'
---

# EC-0017: GoldenPath Platform Distribution Framework

## Problem Statement

GoldenPath IDP has evolved into a comprehensive platform combining:

- **Governance Framework** - Policies, ADRs, PRDs, contracts
- **Agentic Graph RAG** - Knowledge graph + agent orchestration
- **Infrastructure as Code** - Terraform modules, Helm charts, GitOps
- **Software Delivery Platform** - Backstage, CI/CD workflows, templates

Currently, this is bespoke to a single organization. Other teams wanting to adopt GoldenPath must:

1. Fork the entire repository
2. Manually remove organization-specific data
3. Hope they didn't miss sensitive information
4. Lose the ability to pull upstream improvements

This creates:

- **Security risk** - Sensitive data may leak during sanitization
- **Maintenance burden** - Forks diverge, improvements don't flow back
- **Adoption friction** - Hours of manual cleanup before first use
- **Inconsistent implementations** - Each fork evolves differently

## Proposed Solution

Transform GoldenPath from a single-org implementation into a **layered distribution framework** that separates:

| Layer | Contains | Distribution |
|-------|----------|--------------|
| **Instance Data** | Secrets, credentials, org-specific values | Never distributed |
| **Configuration** | Organization name, domain, team structure | Template variables |
| **Framework** | Governance patterns, RAG architecture, workflows | Core distribution |
| **Infrastructure** | Terraform modules, Helm charts, GitOps patterns | Core distribution |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTION LAYERS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Layer 4: Instance Data (NEVER DISTRIBUTED)                  ││
│  │ - .env files, AWS credentials, API keys                     ││
│  │ - Database connection strings                               ││
│  │ - Organization-specific secrets                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Layer 3: Configuration (TEMPLATE VARIABLES)                 ││
│  │ - organization.yaml (name, domain, teams)                   ││
│  │ - metadata-schema.yaml (custom fields)                      ││
│  │ - rag-config.yaml (vector store, graph endpoints)           ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Layer 2: Framework (CORE DISTRIBUTION)                      ││
│  │ - Governance patterns (GOV-*, ADR-*, PRD-*)                 ││
│  │ - RAG architecture (pipelines, embeddings, graph)           ││
│  │ - CI/CD workflows (templates, not instances)                ││
│  │ - Agent context architecture (EC-0013)                      ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Layer 1: Infrastructure (CORE DISTRIBUTION)                 ││
│  │ - Terraform modules (EKS, RDS, VPC)                         ││
│  │ - Helm charts (Backstage, ArgoCD, monitoring)               ││
│  │ - GitOps patterns (ApplicationSets, overlays)               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Details

### 1. Governance Framework Extraction

Transform organization-specific governance docs into templates:

**Current (Bespoke):**

```markdown
# GOV-0017: TDD and Determinism Policy

This policy applies to **Acme Corp** engineering teams...
```

**Distributed (Templated):**

```markdown
# GOV-0017: TDD and Determinism Policy

This policy applies to **{{ organization.name }}** engineering teams...
```

**Template Variables File (`organization.yaml`):**

```yaml
organization:
  name: "Your Organization"
  domain: "example.com"
  github_org: "your-org"

teams:
  platform: "platform-team"
  security: "security-team"

infrastructure:
  aws_region: "us-west-2"
  cluster_name: "goldenpath-cluster"

domains:
  backstage: "backstage.{{ organization.domain }}"
  argocd: "argocd.{{ organization.domain }}"
```

### 2. Configuration Abstraction

Create configuration files that isolate organization-specific settings:

**`config/metadata-schema.yaml`**

```yaml
# Define your organization's metadata extensions
custom_fields:
  cost_center:
    type: string
    required: false
    description: "Internal cost center code"

  data_classification:
    type: enum
    values: [public, internal, confidential, restricted]
    required: true

  compliance_frameworks:
    type: array
    items: [SOC2, HIPAA, PCI-DSS, GDPR]
```

**`config/rag-config.yaml`**

```yaml
# RAG pipeline configuration
vector_store:
  provider: "pinecone"  # or qdrant, weaviate, pgvector
  index_name: "{{ organization.name }}-governance"

knowledge_graph:
  provider: "neo4j"
  database: "governance"

embeddings:
  model: "text-embedding-3-small"
  dimensions: 1536

agent:
  model: "claude-sonnet-4-20250514"
  max_tokens: 4096
```

### 3. Agentic Graph RAG as Framework

The RAG system becomes a pluggable framework:

```
goldenpath-rag/
  core/
    embeddings.py        # Abstract embedding interface
    graph.py             # Knowledge graph operations
    retrieval.py         # Hybrid retrieval (vector + graph)
    agents/
      base.py            # Base agent class
      governance.py      # Governance-specific agent

  providers/
    vector/
      pinecone.py
      qdrant.py
      pgvector.py
    graph/
      neo4j.py
      memgraph.py
    llm/
      anthropic.py
      openai.py

  config/
    __init__.py          # Loads from config/*.yaml
```

**Usage by Adopters:**

```python
from goldenpath_rag import GovernanceRAG
from goldenpath_rag.providers import Neo4jGraph, PineconeVectors, ClaudeAgent

# Initialize with organization config
rag = GovernanceRAG(
    config_path="config/rag-config.yaml",
    graph=Neo4jGraph(),
    vectors=PineconeVectors(),
    agent=ClaudeAgent()
)

# Query works against YOUR governance docs
result = rag.query("What is our TDD policy?")
```

### 4. Infrastructure Generalization

Terraform modules accept organization-specific variables:

**Current (Hardcoded):**

```hcl
module "eks" {
  cluster_name = "acme-goldenpath-prod"
  tags = {
    Organization = "Acme Corp"
  }
}
```

**Distributed (Parameterized):**

```hcl
# variables.tf
variable "organization" {
  type = object({
    name         = string
    cluster_name = string
    environment  = string
  })
}

# main.tf
module "eks" {
  cluster_name = var.organization.cluster_name
  tags = {
    Organization = var.organization.name
    Environment  = var.organization.environment
  }
}
```

### 5. Distribution Model

#### Repository Structure

```
goldenpath-platform/           # GitHub Organization
├── goldenpath-core/           # Framework + Infrastructure
│   ├── docs/
│   │   ├── 00-foundations/    # Philosophy, principles (templated)
│   │   ├── 10-governance/     # Policy templates
│   │   └── 20-contracts/      # PRD/ADR templates
│   ├── modules/               # Terraform modules
│   ├── charts/                # Helm charts
│   └── workflows/             # Reusable GitHub Actions
│
├── goldenpath-rag/            # Agentic Graph RAG Framework
│   ├── core/                  # Core RAG logic
│   ├── providers/             # Pluggable backends
│   └── cli/                   # gov-rag CLI tool
│
├── goldenpath-backstage/      # Backstage distribution
│   ├── packages/              # Core packages
│   ├── plugins/               # Platform plugins
│   └── templates/             # Software templates
│
└── goldenpath-starter/        # Quick-start template
    ├── organization.yaml      # EDIT THIS
    ├── bootstrap.sh           # Run this
    └── README.md              # Start here
```

#### Starter Template

New organizations run:

```bash
# Clone starter
git clone https://github.com/goldenpath-platform/goldenpath-starter my-platform
cd my-platform

# Configure organization
vim organization.yaml  # Set your org name, domain, etc.

# Bootstrap
./bootstrap.sh

# Result:
# - Governance docs templated with your org name
# - Terraform variables populated
# - RAG config initialized
# - Backstage configured for your domain
```

## Bootstrapping Process

### Step 1: Clone Starter

```bash
git clone https://github.com/goldenpath-platform/goldenpath-starter acme-platform
cd acme-platform
```

### Step 2: Configure Organization

Edit `organization.yaml`:

```yaml
organization:
  name: "Acme Corp"
  domain: "acme.io"
  github_org: "acme-corp"

teams:
  platform: "@acme-corp/platform"
  security: "@acme-corp/security"

infrastructure:
  aws_region: "us-east-1"
  cluster_name: "acme-goldenpath"
```

### Step 3: Run Bootstrap

```bash
./bootstrap.sh

# Output:
#  Templating governance docs...
#  Configuring Terraform variables...
#  Setting up RAG config...
#  Initializing Backstage...
#  Creating initial commit...
#
# GoldenPath initialized for Acme Corp!
# Next steps:
#   1. Review docs/10-governance/policies/
#   2. Run: terraform init && terraform plan
#   3. Deploy Backstage: helm install backstage ./charts/backstage
```

### Step 4: Customize

Add organization-specific:

- Policies (extend GOV-* templates)
- ADRs (record your decisions)
- Terraform modules (your infrastructure)
- Backstage plugins (your integrations)

### Step 5: Stay Updated

```bash
# Add upstream remote
git remote add upstream https://github.com/goldenpath-platform/goldenpath-core

# Pull framework updates (non-breaking)
git fetch upstream
git merge upstream/main --no-edit

# Framework updates flow in, your customizations preserved
```

## Benefits

| Benefit | Description |
|---------|-------------|
| **Zero-friction adoption** | Clone, configure, deploy in hours not weeks |
| **Security by design** | Sensitive data never enters distribution |
| **Upstream improvements** | Pull framework updates without conflicts |
| **Consistent implementations** | All adopters share core patterns |
| **Customization preserved** | Organization-specific changes in separate layer |
| **Community contributions** | Improvements flow back to framework |

## Migration Path (Existing GoldenPath)

For current GoldenPath implementation:

### Phase 1: Identify Layers

```bash
# Script to classify files by distribution layer
./scripts/classify-distribution-layers.sh

# Output:
# Layer 4 (Instance): 23 files (secrets, .env, credentials)
# Layer 3 (Config): 45 files (org-specific values)
# Layer 2 (Framework): 156 files (governance, workflows)
# Layer 1 (Infra): 89 files (modules, charts)
```

### Phase 2: Extract Framework

```bash
# Create framework repo from current
./scripts/extract-framework.sh --output ../goldenpath-core

# Replaces org-specific values with {{ variables }}
# Moves sensitive files to .gitignore template
```

### Phase 3: Validate

```bash
# Bootstrap a test organization from extracted framework
cd ../goldenpath-core
./bootstrap.sh --org "Test Corp" --domain "test.io" --output ../test-platform

# Verify test-platform builds and deploys
```

## Open Questions

1. **Versioning strategy for framework updates?**
   - Recommendation: SemVer with breaking change policy

2. **How to handle framework customizations that should flow upstream?**
   - Recommendation: Contribution guidelines + RFC process

3. **Commercial licensing model?**
   - Recommendation: Apache 2.0 for core, enterprise support optional

4. **Hosting for shared RAG infrastructure (embeddings, graph)?**
   - Recommendation: Self-hosted by default, managed option for enterprise

## Decision

**Status:** Awaiting review

**Recommendation:** Implement layered distribution model starting with governance framework extraction, followed by RAG framework packaging.

## Implementation Plan

### Phase 1: Framework Extraction

- [ ] Create classification script for distribution layers
- [ ] Template governance docs with variable substitution
- [ ] Extract reusable Terraform modules
- [ ] Package Helm charts for distribution

### Phase 2: RAG Framework

- [ ] Abstract RAG providers (vector, graph, LLM)
- [ ] Create pluggable configuration system
- [ ] Package as standalone Python library
- [ ] Document provider implementations

### Phase 3: Starter Template

- [ ] Create goldenpath-starter repository
- [ ] Build bootstrap.sh script
- [ ] Write adoption documentation
- [ ] Create video walkthrough

### Phase 4: Community

- [ ] Publish to GitHub organization
- [ ] Create contribution guidelines
- [ ] Set up discussions/issues process
- [ ] Build example implementations

---

Proposed by: platform-team
Date: 2026-01-28

---

## Related Documents

- [GOV-0020: Agentic Graph RAG Maturity Model](../10-governance/policies/GOV-0020-rag-maturity-model.md) - RAG architecture this framework packages
- [PRD-0008: Agentic Graph RAG Pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md) - Implementation PRD
- [EC-0013: Agent Context Architecture](EC-0013-agent-context-architecture.md) - Agent bootstrap pattern included in framework
