---
id: ADR-0005-app-keycloak-as-identity-provider-for-human-sso
title: 'ADR-0005: Adopt Keycloak for platform SSO (humans) and keep IRSA for pod-to-AWS
  auth'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
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
  - 06_IDENTITY_AND_ACCESS
  - 20_TOOLING_APPS_MATRIX
  - ADR-0003-platform-AWS-IAM-bootstrap-IRSA-SSM-
  - ADR-0005-app-keycloak-as-identity-provider-for-human-sso
  - ADR-0162
  - HELM_KEYCLOAK
  - IDP_TOOLING_KEYCLOAK_CONFIG
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0005: Adopt Keycloak for platform SSO (humans) and keep IRSA for pod-to-AWS auth

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Application
- **Decision type:** Security / Identity / UX
- **Related docs:** docs/10-governance/01_GOVERNANCE.md, docs/06_REBUILD_SEQUENCE.md, ADR-0003-iam-irsa-ssm.md

## Context

We want a consistent identity layer for platform UIs and developer experience:

- Argo CD login
- Backstage login
- other internal tools as needed

We also want to avoid a bootstrap deadlock where identity must exist before the platform can be deployed.

## Decision

Use **Keycloak** as the long-term identity provider for **human authentication** (OIDC/SAML) to platform applications.

Keycloak is **not a hard dependency for V1 bootstrap**.

Bootstrap and break-glass access remain:

- AWS IAM for initial EKS admin bootstrap
- SSM for node break-glass access

Workload AWS API access remains:

- IRSA (Keycloak does not replace IRSA)

## Scope

- Applies to: Argo CD SSO, Backstage SSO, platform UI identity.
- Out of scope (initially):

- Keycloak as a prerequisite for cluster bootstrap

- replacing Kubernetes API auth entirely (optional later)

## Consequences

### Positive

- Centralized identity and group management for platform UIs.
- Consistent access patterns across tooling.
- Supports internal-only posture (VPN + SSO) cleanly.

### Negative / Tradeoffs

- Adds operational burden (availability, upgrades, backups).
- Requires secrets/config hygiene.
- If introduced too early, can distract from CI-ready bootstrap goals.

### Operational implications

- Deploy Keycloak via GitOps like other platform apps.
- Define realm/client setup for Argo CD and Backstage.
- Maintain a fallback admin path during SSO outages.

## Alternatives considered

- AWS Cognito (viable but less portable/control for internal platform)
- Dex (lighter but less full-featured as primary IdP)
- No central IdP (rejected long-term)

## Follow-ups / Actions

- Implement Keycloak after core V1 loop is stable (bootstrap + promotion).
- Define Keycloak client configuration for:

- argocd

- backstage

- Document migration from initial local auth to SSO to avoid lockouts.
