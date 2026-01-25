---
id: ADR-0032-platform-eks-access-model
title: 'ADR-0032: EKS access model (bootstrap admin vs steady-state access)'
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
  - ADR-0015-platform-aws-oidc-for-github-actions
  - ADR-0032-platform-eks-access-model
  - ADR-0168
  - EKS_REQUEST_FLOW
  - MODULES_AWS_EKS_README
  - RB-0019-relationship-extraction-script
  - audit-20260103
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# ADR-0032: EKS access model (bootstrap admin vs steady-state access)

- **Status:** Accepted
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Operations
- **Related:** docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0015-platform-aws-oidc-for-github-actions.md

---

## Context

EKS grants cluster-admin access to the IAM principal that creates the cluster.
In our case, that is the GitHub Actions bootstrap role. This is useful for
initial provisioning, but it is a risk if left as the only admin path.

We need an explicit access model that:

- keeps bootstrap deterministic,
- allows human access in a controlled way,
- supports least-privilege in steady state.

## Decision

We will use the **EKS access entry + access policy** model for human access,
and keep CI access split into two phases:

1) **Bootstrap phase:** CI role has cluster-admin to create/seed the cluster.
2) **Steady state:** CI role is reduced; humans get explicit access entries.

This is accepted for V1 but remains open to alternatives as the platform matures.

## Scope

Applies to:

- Human access to EKS clusters
- CI role access during bootstrap vs steady state

Does not apply to:

- In-cluster workload access (covered by IRSA)
- External SSO integration (e.g., Keycloak)

## Access model (diagram)

```text
                           AWS ACCOUNT
+------------------------------+
|                                                            |
|  [GitHub Actions OIDC]  --->  AssumeRole (CI Bootstrap)     |
|                                        |                    |
|                                        v                    |
|                                 EKS Cluster Admin           |
|                                                            |
|  [Humans] ----------->  Access Entry + Policy         |
|                                      (EKS API)              |
|                                                            |
|  [Workloads] -> ServiceAccount -> IRSA Role -> AWS APIs     |
|                                                            |
+------------------------------+
```

## Commands (placeholders)

Create access entry:

```sh
aws eks create-access-entry \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --region <AWS_REGION>
```

Associate access policy:

```sh
aws eks associate-access-policy \
  --cluster-name <CLUSTER_NAME> \
  --principal-arn "<IAM_USER_OR_ROLE_ARN>" \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/<POLICY_NAME> \
  --access-scope type=cluster \
  --region <AWS_REGION>
```

## Consequences

### Positive

- Explicit, auditable human access to clusters.
- Clear separation between bootstrap admin and steady-state access.
- Reduced reliance on implicit creator-admin access.

### Tradeoffs / Risks

- Requires a follow-up step to grant human access.
- CI role remains powerful during bootstrap until reduced.

### Operational impact

- Platform owners must manage access entries for admins.
- CI role should be tightened after bootstrap is stable.

## Alternatives considered

- **Legacy aws-auth ConfigMap:** not preferred for new clusters.
- **SSO (Keycloak) in V1:** deferred to keep bootstrap simple.

## Follow-ups

- Introduce a reduced-privilege CI role for steady state.
- Document access entry management in governance/onboarding.

## Notes

Placeholders in commands are literal template fields (e.g., `<CLUSTER_NAME>`).
