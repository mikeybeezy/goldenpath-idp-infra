# 🏛️ Golden Path IDP (Infra)

[![CI Status](https://img.shields.io/github/actions/workflow/status/mikeybeezy/goldenpath-idp-infra/ci-bootstrap.yml?label=Bootstrap)](https://github.com/mikeybeezy/goldenpath-idp-infra/actions)
[![Docs](https://img.shields.io/badge/Docs-Live-green)](docs/00_DOC_INDEX.md)
[![Metadata Fabric](https://img.shields.io/badge/Metadata-Enforced-blue)](docs/90-doc-system/METADATA_STRATEGY.md)

**The Engineering Foundation for the Golden Path Internal Developer Platform.**
This repository defines the infrastructure (AWS/EKS), governance (Policies), and delivery pipelines (GitOps/ArgoCD) that power our engineering capabilities.

---

## 🚀 Key Capabilities

### 1. Infrastructure as Code (IaC)
- **EKS & VPC:** Production-grade Kubernetes clusters managed via Terraform.
- **Bootstrapping:** Automated "Cluster-in-a-Box" logic via `make timed-build` sets up ArgoCD, Ingress, and Observability.
- **Teardown Automation:** Deterministic cleanup for ephemeral environments.

### 2. Governance & Metadata
- **Knowledge Graph:** All artifacts are linked via a [Rich Metadata Schema](docs/90-doc-system/METADATA_STRATEGY.md).
- **AI Protocols:** Strict [Agent Governance](docs/10-governance/07_AI_AGENT_GOVERNANCE.md) ensures safe AI collaboration.
- **Cost Visibility:** Infracost integration provides $ estimates on every PR.

### 3. Documentation System
We treat docs as code.
- **ADRs:** [Architectural Decision Records](docs/adrs/) for technical choices.
- **Changelogs:** [Structured release notes](docs/changelog/) linked to decisions.
- **Runbooks:** [Operational guides](docs/runbooks/) for on-call success.

---

## 📂 Repository Layout

```
.
├── envs/            # Environment Stacks (dev, staging, prod)
├── modules/         # Reusable Terraform Modules (EKS, VPC, IAM)
├── gitops/          # ArgoCD Application Manifests
├── docs/            # The Platform Knowledge Base
├── scripts/         # Automation (Teardown logs, Validation)
└── Makefile         # The Developer Control Plane
```

---

## ⚡ Quick Start

**Prerequisites:** Terraform 1.5+, AWS CLI, `make`.

### 1. The Standard Interface
We use `Makefile` targets to ensure consistency.

```bash
# Initialize & Plan (Persistent Envs)
make init ENV=dev
make plan ENV=dev

# Apply Infrastructure
make apply ENV=dev
```

### 2. Ephemeral Environment Workflow
For validation or testing, we use unique Build IDs to spin up and tear down complete stacks.

```bash
# Define a unique Build ID (Format: dd-mm-yy-NN)
export BUILD_ID="03-01-26-01"

# Spin up full stack (Infra + ArgoCD + Apps)
make timed-build ENV=dev BUILD_ID=$BUILD_ID

# ... Validate Platform ...

# Tear down completely
make timed-teardown ENV=dev BUILD_ID=$BUILD_ID
```

### 3. Validating Changes
Before submitting a PR, run the local validation suite:

```bash
# Validate Metadata Links
python3 scripts/validate-metadata.py docs
```

---

## 🧠 Governance & Contribution

*   **Humans:** Read the [Collaboration Guide](docs/80-onboarding/13_COLLABORATION_GUIDE.md).
*   **AI Agents:** Read [Protocol 26](docs/80-onboarding/26_AI_AGENT_PROTOCOLS.md) before performing any action.
*   **Decisions:** New features require an [ADR](docs/adrs/02_adr_template.md).

## 📊 Status
*   **Roadmap:** [View Active Priorities](docs/production-readiness-gates/ROADMAP.md)
*   **Policies:** [View Governance Index](docs/10-governance/01_GOVERNANCE.md)
