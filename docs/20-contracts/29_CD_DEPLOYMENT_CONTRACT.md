---
id: 29_CD_DEPLOYMENT_CONTRACT
title: CD Deployment Contract
type: contract
risk_profile:
  production_impact: high
  security_risk: none
  coupling_risk: high
reliability:
  rollback_strategy: git-revert
  observability_tier: gold
relates_to:
  - 02_GOVERNANCE_MODEL
  - 12_GITOPS_AND_CICD
  - 39_GOLDEN_PATH_VALIDATION
  - ADR-0026-platform-cd-deployment-contract
  - ADR-0028-platform-dev-branch-gate
  - ADR-0172-cd-promotion-strategy-with-approval-gates
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# CD Deployment Contract

Doc contract:

- Purpose: Define deployment contract and promotion expectations for GitOps delivery.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/40-delivery/12_GITOPS_AND_CICD.md, docs/40-delivery/39_GOLDEN_PATH_VALIDATION.md, docs/adrs/ADR-0026-platform-cd-deployment-contract.md

This document defines the deployment contract for GoldenPath. It specifies the minimum information
and guarantees required for any deployment executed via the platform.

The goal is to make deployments:

- deterministic
- auditable
- reversible
- understandable without tribal knowledge

This contract applies to platform workloads and serves as the reference model for team workloads.

---

## Scope

This contract covers:

- what constitutes a deployment
- what metadata must be known
- how success and failure are determined
- how promotion and rollback occur

It does not define:

- application behavior
- runtime SLOs
- business logic

---

## Deployment definition

A deployment is considered valid when:

- a specific artifact is deployed
- to a specific environment
- via GitOps reconciliation
- and reaches a healthy state

---

## Required deployment metadata

Each deployment must be able to answer the following:

### What was deployed?

- container image (registry + name)
- immutable identifier (tag or digest)
- source commit SHA

### Where was it deployed?

- environment (dev | test | staging | prod)
- cluster name
- namespace

### How was it deployed?

- deployment controller (e.g. Argo CD)
- application identifier

---

## Source of truth

- Desired state: Git (GitOps repository)
- Actual state: Argo CD
- Deployment receipt: CI-generated release artifact

The platform does not treat CI logs as a source of truth.

---

## Deployment success criteria

A deployment is successful when:

- Argo CD reports the application as `Synced`
- Argo CD reports the application as `Healthy`
- required post-deploy checks (if any) pass

If these conditions are not met, the deployment is considered failed.

---

## Promotion model

Promotion between environments is achieved by:

- reusing the same immutable artifact
- updating the target environment configuration in Git
- allowing GitOps reconciliation to apply the change

Rebuilds are not used for promotion.

---

## Rollback model

Rollback is performed by:

- reverting the Git change that introduced the deployment
- allowing GitOps reconciliation to restore the previous state

No manual intervention is required in steady state.

---

## Progressive delivery

Argo Rollouts may be used in V1 as an optional capability for services that need safer rollouts.
It is not required by default.

---

## Invariants

- Deployments must be reproducible from Git history.
- Promotion must not change the artifact.
- Rollback must be possible without rebuilding.

---

## Ownership

This contract is owned by the platform. Changes that alter deployment semantics require an ADR.
