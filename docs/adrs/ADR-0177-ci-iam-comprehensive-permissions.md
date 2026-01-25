---
id: ADR-0177-ci-iam-comprehensive-permissions
title: 'ADR-0177: Grant CI role comprehensive IAM permissions with resource scoping'
type: adr
status: active
domain: platform-core
value_quantification:
  vq_class: VO/HQ
  impact_tier: high
  potential_savings_hours: 8.0
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
  - 21_CI_ENVIRONMENT_CONTRACT
  - ADR-0015-platform-aws-oidc-for-github-actions
  - ADR-0030-platform-precreated-iam-policies
  - 33_IAM_ROLES_AND_POLICIES
supersedes:
  - ADR-0030-platform-precreated-iam-policies
superseded_by: []
tags:
  - security
  - ci-cd
  - iam
inheritance: {}
supported_until: 2027-01-22
version: '1.0'
breaking_change: false
---

# ADR-0177: Grant CI role comprehensive IAM permissions with resource scoping

- **Status:** Accepted
- **Date:** 2026-01-22
- **Owners:** Platform (GoldenPath IDP)
- **Domain:** Platform
- **Decision type:** Security | Operations
- **Supersedes:** ADR-0030-platform-precreated-iam-policies
- **Related:** docs/10-governance/policies/iam/github-actions-terraform-full.json

---

## Context

ADR-0030 established that the CI apply role should NOT have `iam:CreatePolicy` permissions,
requiring IAM policies for IRSA controllers (Cluster Autoscaler, AWS Load Balancer Controller)
to be pre-created manually.

However, the Terraform codebase evolved to create additional IAM policies dynamically:

- External Secrets Operator (ESO) policy
- ExternalDNS policy
- Future IRSA controller policies

Additionally, the codebase now creates Secrets Manager secrets dynamically for application
credentials (Keycloak, Backstage, etc.).

This created a mismatch where:

1. Terraform code expects to create these resources
2. CI role lacks permissions to create them
3. Builds fail with `AccessDenied` errors
4. Fixing requires manual AWS console intervention each time

The brittleness of ADR-0030's approach has become a significant operational burden,
causing repeated CI failures and requiring emergency fixes.

## Decision

We will **grant the CI role comprehensive IAM permissions** with appropriate resource scoping
to allow Terraform to manage all infrastructure resources it defines.

The permissions are scoped by:

- **Resource prefix:** `goldenpath-*` for IAM roles and policies
- **Region:** `eu-west-2` for EC2 and regional services
- **Account:** `593517239005` for all resources

The full policy is documented in:
`docs/10-governance/policies/iam/github-actions-terraform-full.json`

## Scope

The CI role now has permissions to manage:

- IAM roles prefixed with `goldenpath-*`
- IAM policies prefixed with `goldenpath-*`
- IAM OIDC providers (for EKS)
- Secrets Manager secrets prefixed with `goldenpath/`
- EC2/VPC resources (region-scoped)
- EKS clusters and node groups
- RDS instances
- S3 buckets prefixed with `goldenpath-*`
- ECR repositories prefixed with `goldenpath-*`
- Route53 hosted zones and records
- Lambda functions prefixed with `goldenpath-*`
- CloudWatch alarms and logs
- Elastic Load Balancers
- Auto Scaling groups

## Consequences

### Positive

- CI can apply all Terraform-managed resources without manual intervention
- No more `AccessDenied` failures when Terraform adds new resource types
- Single source of truth: policy is documented in code
- Reduced operational overhead and emergency fixes
- Faster iteration on infrastructure changes

### Tradeoffs / Risks

- Wider CI permissions than ADR-0030 allowed
- Must maintain resource prefix discipline (`goldenpath-*`)
- CI compromise could affect more resources (mitigated by scoping)

### Security mitigations

- All permissions are scoped to `goldenpath-*` prefix where possible
- EC2 permissions are region-scoped to `eu-west-2`
- GitHub OIDC trust limits which repos can assume the role
- Audit trail via CloudTrail for all IAM actions

### Operational impact

- Platform operators must apply the new policy to the `github-actions-terraform` role
- Policy changes are reviewed via PR to the policy JSON file
- Future permission additions follow the same pattern

## Alternatives considered

- **Keep ADR-0030 approach:** Rejected due to operational burden and repeated failures
- **Bootstrap Terraform for CI permissions:** Good long-term solution, but adds complexity for V1
- **Pre-create all policies:** Doesn't scale as codebase evolves

## Migration steps

1. Copy policy from `github-actions-terraform-full.json` to AWS console
2. Apply to the `github-actions-terraform` IAM role
3. Trigger new build to verify permissions

## Follow-ups

- V1.1: Create bootstrap Terraform to manage CI permissions in code
- Add CI permission drift detection
- Document required permissions per Terraform module

## Notes

This supersedes ADR-0030. The V1 compromise of pre-creating policies has proven
unsustainable as the codebase evolved. The new approach trades tighter least-privilege
for operational reliability, with security maintained through resource scoping.
