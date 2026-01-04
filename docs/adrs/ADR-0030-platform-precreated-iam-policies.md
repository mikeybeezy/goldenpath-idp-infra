---
id: ADR-0030
title: 'ADR-0030: Pre-create IAM policies for IRSA controllers in V1'
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
- ADR-0015
- ADR-0030
---

# ADR-0030: Pre-create IAM policies for IRSA controllers in V1

- **Status:** Accepted
- **Date:** 2025-12-28
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Operations
- **Related:** docs/20-contracts/21_CI_ENVIRONMENT_CONTRACT.md, docs/adrs/ADR-0015-platform-aws-oidc-for-github-actions.md

---

## Context

The Terraform apply role used by GitHub Actions is intentionally scoped and cannot create IAM policies.
Some IRSA controller roles (Cluster Autoscaler, AWS Load Balancer Controller) require custom IAM policies.
Allowing CI to create policies increases permissions and risk; blocking policy creation stalls apply.

We need a short‑term path that keeps CI least‑privilege while still enabling cluster bootstrap.

## Decision

We will **pre‑create the IAM policies** for Cluster Autoscaler and AWS Load Balancer Controller
and pass their ARNs into Terraform. Terraform will attach those policies to the IRSA roles
and will **not** create or manage the policies themselves in V1.

## Scope

Applies to:

- Cluster Autoscaler policy
- AWS Load Balancer Controller policy

Does not apply to:

- AWS‑managed policies (e.g., EBS/EFS CSI driver)
- Other IAM policies created by Terraform for core infra

## Consequences

### Positive

- Keeps CI apply role least‑privilege (no `iam:CreatePolicy`).
- Unblocks dev cluster bootstrap in V1.
- Clear separation between policy authoring and infrastructure provisioning.

### Tradeoffs / Risks

- Manual pre‑creation step (operational overhead).
- Policy drift risk if JSON changes but ARNs are not updated.
- Slightly harder to reproduce in a fresh account without additional setup.

### Operational impact

- Platform operators must create the two policies once per account.
- The policy ARNs must be stored in `terraform.tfvars` or provided via `TF_VAR_*`.
- Changes to policy JSON require explicit update and re‑attachment.

## Alternatives considered

- **Allow CI role to create IAM policies:** rejected for now due to widened permissions.
- **Create policies outside Terraform via pipeline step:** adds tooling complexity and still needs IAM.
- **Disable IRSA controllers:** rejected because it blocks required platform components.

## Follow-ups

- Document the policy creation steps and ARNs in the environment contract.
- Revisit in V2: move policy creation back into Terraform with tighter IAM scoping.
- Add automated checks to detect policy drift.

## Notes

This is a deliberate V1 compromise. It is acceptable as long as it is documented and revisited.
