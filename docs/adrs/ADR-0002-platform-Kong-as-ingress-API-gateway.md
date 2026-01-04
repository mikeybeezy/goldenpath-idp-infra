---
id: ADR-0002
title: 'ADR-0002: Use Kong as the primary ingress/API gateway behind an internal NLB'
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
relates_to:

- ADR-0002

---

# ADR-0002: Use Kong as the primary ingress/API gateway behind an internal NLB

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Architecture / Security
- **Related docs:** docs/50-observability/05_OBSERVABILITY_DECISIONS.md, docs/06_REBUILD_SEQUENCE.md, docs/10-governance/01_GOVERNANCE.md

## Context

We need a consistent “front door” for platform and workloads on EKS.

We want an opinionated V1 that is secure-by-default and avoids public exposure of platform surfaces while iterating (Argo, Kong Manager/UI, Backstage, etc.).

## Decision

Deploy **Kong** as the primary ingress/API gateway.

Expose Kong via a Kubernetes Service of type LoadBalancer using **AWS Load Balancer Controller** to provision an **internal NLB** (private scheme).

User access to internal endpoints will be provided via a controlled access path (e.g., VPN such as Pritunl).

## Scope

- Applies to: V1 ingress entrypoint for platform and sample apps.
- Out of scope: public edge hardening (WAF, public ALB), multi-region ingress, advanced L7 at AWS edge.

## Consequences

### Positive

- Clear, opinionated default: one ingress/gateway to learn and support.
- Private-by-default reduces attack surface during early iterations.
- Kong can own L7 routing/policies consistently across environments.

### Negative / Tradeoffs

- Requires an access path (VPN) for users/operators to reach internal endpoints.
- If teams want AWS-native L7 routing/WAF at the edge, that is not the default in V1.
- Some features (OIDC at ALB edge, AWS WAF integration) are easier with ALB and would be deferred/optional.

### Operational implications

- Must maintain AWS Load Balancer Controller (and its IAM/IRSA) as a core dependency.
- Provide runbooks for:

- verifying NLB creation

- Kong readiness and routing checks

- private access (VPN) onboarding and troubleshooting

## Alternatives considered

- **ALB Ingress Controller / AWS ALB as primary edge**: not chosen for V1 because Kong is the opinionated gateway and we want private-by-default posture.
- **ingress-nginx/traefik**: kept as potential future alternatives/escape hatches but not installed by default to avoid ambiguity.
- **Public NLB/ALB**: not chosen due to increased exposure during iteration.

## Follow-ups / Actions

- Standardize Kong service annotations for internal NLB.
- Document internal access approach (Pritunl) and “break-glass” paths.
- Add smoke tests validating ingress reachability via internal endpoint.
