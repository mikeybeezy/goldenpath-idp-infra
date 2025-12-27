# CI Environment Contract

This document defines the environment variables used by GoldenPath CI pipelines.
It serves as the contract between:
- CI workflows
- Terraform
- Bootstrap scripts
- GitOps reconciliation

These variables are intentionally explicit to support deterministic behavior and safe automation.

---

## Required Variables

### ENV
**Purpose:** Target environment  
**Values:** dev | test | staging | prod  
**Used by:** Terraform, GitOps overlays, naming

---

### BUILD_ID
**Purpose:** Uniquely identifies a CI run  
**Source:** GitHub Actions run ID or timestamp  
**Used by:** Cluster naming, tagging, logs

---

### CLUSTER_NAME
**Purpose:** EKS cluster identifier  
**Derived from:** ENV + BUILD_ID  
**Example:** goldenpath-dev-eks-20250115-02

---

## Optional Variables

### DESTROY_AFTER
**Purpose:** Controls automatic teardown  
**Values:** true | false  
**Default:** false

---

### TF_VAR_region
**Purpose:** AWS region override  
**Default:** eu-west-2

---

## Secrets (Referenced, Not Defined)

Secrets are **not** defined here.
They are provided via:
- Repository secrets (role ARNs)
- AWS OIDC role assumption
- AWS Secrets Manager / SSM

---

## Invariants

- Pipelines must behave deterministically given the same inputs.
- No variable should change behavior silently.
- Defaults must be explicit and documented.

---

## Ownership

This contract is owned by the platform.
Changes require:
- an ADR if behavior changes
- doc update in the same PR
