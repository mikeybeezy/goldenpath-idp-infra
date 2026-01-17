---
id: ADR-0063-platform-terraform-helm-bootstrap
title: 'ADR-0063: Terraform Helm Provider for Bootstrap'
type: adr
status: active
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 2
schema_version: 1
relates_to:
  - 01_adr_index
  - 04_PR_GUARDRAILS
  - ADR-0001-platform-argocd-as-gitops-operator
  - ADR-0063-platform-terraform-helm-bootstrap
  - ADR-0070-platform-terraform-aws-lb-controller
  - ADR-0148-seamless-build-deployment-with-immutability
  - CL-0002-bootstrap-refactor
  - READINESS_CHECKLIST
  - ROADMAP
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0063: Terraform Helm Provider for Bootstrap

- **Status:** Proposed
- **Date:** 2026-01-01
- **Owners:** platform
- **Domain:** Platform
- **Decision type:** Architecture
- **Related:** `docs/adrs/ADR-0001-platform-argocd-as-gitops-operator.md`

---

## Context

Running the platform requires a complex sequence of operations: provisioning AWS infrastructure (Terraform) and then installing Kubernetes controllers like ArgoCD (Bash scripts/Helm).

The current approach relies on `goldenpath-idp-bootstrap.sh`, which wraps Terraform triggers and then imperatively runs `helm install`. This creates several issues:

1. **Fragility**: The script must manually wait for the cluster to be ready, manage kubeconfig contexts, and handle partial failures.
2. **State Disconnect**: Terraform is unaware of the Helm releases. If Terraform destroys the cluster, it "forgets" the Helm state, but if only the Helm chart fails, Terraform thinks the apply succeeded.
3. **Maintenance**: We are maintaining custom shell logic that duplicates standard Terraform lifecycle management.

---

## Decision

We will **move the bootstrapping of ArgoCD (and critical system controllers)** directly into **Terraform** using the `hashicorp/helm` provider.

1. The `aws_eks` module (or a new `bootstrap` module) will interact with the EKS cluster endpoint directly.
2. ArgoCD will be defined as a `resource "helm_release" "argocd"` within the Terraform graph.
3. The `goldenpath-idp-bootstrap.sh` script will be deprecated and replaced by a standard `terraform apply`.
4. Terminating the "App of Apps" chain will be handled by Terraform. We will use `kubernetes_manifest` resources to inject the initial ArgoCD Application manifests (Kong, Autoscaler, etc.) immediately after the Helm release is ready.

---

## Consequences

### Positive

- **Atomic Operations**: A single `terraform apply` provisions the cluster AND installs the GitOps controller. If one fails, the entire apply fails cleanly.
- **Reduced Code**: We can delete ~500 lines of complex Bash scripting (`bootstrap/10_bootstrap/*.sh`, `bootstrap/10_gitops-controller/*.sh`).
- **Declarative State**: The version of ArgoCD is now tracked in the Terraform state file, allowing for controlled upgrades via PRs.

### Tradeoffs / Risks

- **Tight Coupling**: Terraform execution now requires network access to the K8s API server. This can complicate "private-only" cluster management (requires bastion hosts or VPC connectivity for the runner).
- **Provider Dependency**: The Terraform Helm provider can sometimes be "finicky" with timeouts or massive charts compared to the native CLI.

### Operational impact

- **Operators**: No longer need to run `make bootstrap`. They simply run `make apply`.
- **CI/CD**: The bootstrapping workflow (`ci-bootstrap.yml`) can be simplified or merged into the standard Apply workflow.
