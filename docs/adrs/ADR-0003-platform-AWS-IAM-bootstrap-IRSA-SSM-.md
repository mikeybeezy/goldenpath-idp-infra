---
id: ADR-0003
title: ADR-0003: Use AWS IAM for bootstrap access, IRSA for pod-to-AWS access, and SSM for node break-glass
type: adr
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2027-01-03
  breaking_change: false
relates_to: []
---

# ADR-0003: Use AWS IAM for bootstrap access, IRSA for pod-to-AWS access, and SSM for node break-glass

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security / Operations / Governance
- **Related docs:** docs/06_REBUILD_SEQUENCE.md, docs/08_SOURCE_OF_TRUTH.md, docs/10-governance/01_GOVERNANCE.md

## Context

We need secure and deterministic access patterns:

- Operators must bootstrap and manage the cluster safely without relying on SSH keys by default.
- Controllers (LB controller, autoscaler, external-secrets) require AWS API access with least privilege.
- The platform is frequently rebuilt; access must be reproducible, auditable, and low-friction.

## Decision

1. **Bootstrap human access** uses AWS IAM authentication to EKS:

- `aws eks update-kubeconfig` + Kubernetes RBAC mappings.

1. **Workload access to AWS APIs** uses **IRSA** (IAM Roles for Service Accounts):

- enable EKS OIDC issuer usage and create IAM OIDC provider

- create least-privilege IAM roles bound to specific Kubernetes service accounts.

1. **Node “break-glass” access** uses **AWS SSM Session Manager** as the default.

1. **SSH** is not enabled by default; it can be turned on only as an explicit, time-bound

   exception (Terraform flag) if SSM is insufficient.

## Scope

- Applies to: all V1 clusters/environments.
- Out of scope: Keycloak-based SSO for humans (planned later once platform is stable). Keycloak does not replace IRSA.

## Consequences

### Positive

- Least privilege for controllers; no long-lived AWS keys in cluster.
- Auditable operator access (SSM sessions) without opening inbound SSH.
- Deterministic bootstrap for ephemeral clusters.

### Negative / Tradeoffs

- IRSA requires correct OIDC/role wiring; misconfiguration can block controllers.
- SSM requires agent + network path (NAT or VPC endpoints); missing endpoints/permissions blocks break-glass access.
- If SSH is enabled, it adds key management and risk; must be tightly controlled.

### Operational implications

- Terraform must output required IRSA role ARNs for core controllers.
- Argo apps/Helm values must annotate service accounts with role ARNs (declarative, not manual injection).
- Document:

- how to verify IRSA works (token/STS calls, controller logs)

- how to verify SSM works (start-session)

- exception process for enabling SSH

## Alternatives considered

- **Node IAM role for all pods**: rejected due to blast radius and weak least privilege.
- **Static AWS keys in Kubernetes Secrets**: rejected due to secret sprawl and rotation risk.
- **SSH as default**: rejected due to auditability and key management burden.
- **Keycloak-first auth for bootstrap**: deferred due to chicken/egg and added complexity early.

## Follow-ups / Actions

- Implement IRSA roles for: aws-load-balancer-controller, autoscaler/karpenter, external-secrets (as needed).
- Codify SSM permissions for node role and break-glass operator role.
- Add CI/smoke checks: IRSA functional + SSM reachable (where feasible).

If you want, I can also suggest a simple numbering scheme and a docs/adrs/README.md that explains how you create/supersede ADRs (so future-you doesn’t have to remember the process).
