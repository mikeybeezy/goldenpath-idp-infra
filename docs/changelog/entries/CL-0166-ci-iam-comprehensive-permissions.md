---
id: CL-0166
title: CI IAM Comprehensive Permissions with Resource Scoping
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - docs/10-governance/policies/iam/github-actions-terraform-full.json
  - docs/adrs/ADR-0177-ci-iam-comprehensive-permissions.md
  - docs/adrs/ADR-0030-platform-precreated-iam-policies.md
  - modules/aws_secrets_manager/main.tf
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
schema_version: 1
relates_to:
  - ADR-0177-ci-iam-comprehensive-permissions
  - ADR-0030-platform-precreated-iam-policies
  - 33_IAM_ROLES_AND_POLICIES
supersedes: []
superseded_by: []
tags:
  - security
  - ci-cd
  - iam
  - terraform
inheritance: {}
supported_until: 2028-01-23
value_quantification:
  vq_class: HV/HQ
  impact_tier: high
  potential_savings_hours: 8.0
date: 2026-01-23
author: platform-team
---

# CI IAM Comprehensive Permissions with Resource Scoping

## Summary

Resolved CI pipeline failures by creating comprehensive IAM permissions for the `github-actions-terraform` role with proper resource scoping. Created ADR-0177 superseding ADR-0030's restrictive approach.

## Problem

Ephemeral builds were failing with multiple `AccessDenied` errors:

* `iam:CreatePolicy` for ESO and ExternalDNS policies
* `secretsmanager:CreateSecret` for Backstage/Keycloak secrets
* `secretsmanager:RotateSecret` for secret rotation

ADR-0030 restricted the CI role from creating IAM policies, requiring manual pre-creation. As the Terraform codebase evolved to dynamically create policies and secrets, this became unsustainable.

## Root Cause

* ADR-0030 established least-privilege CI role without `iam:CreatePolicy`
* Terraform code evolved to create IAM policies dynamically (ESO, ExternalDNS)
* Terraform also creates Secrets Manager secrets for application credentials
* Mismatch between what Terraform expects to create and what CI can create

## Changes Made

### New IAM Policy

Created comprehensive policy at `docs/10-governance/policies/iam/github-actions-terraform-full.json`:

* IAM roles/policies scoped to `goldenpath-*` prefix
* Secrets Manager scoped to `goldenpath/*` path
* EC2/ELB/ASG scoped by `goldenpath-*` tag conditions
* EKS clusters scoped to `cluster/goldenpath-*` ARN pattern
* KMS limited to approved services via `kms:ViaService`

### Terraform Fix

Fixed `modules/aws_secrets_manager/main.tf` count dependency:

```hcl
locals {
  # Plan-time determinable: will we have a secret ARN after apply?
  will_have_secret = local.should_create || local.secret_exists
}
```

### ADR Updates

* Created ADR-0177 granting comprehensive permissions with scoping
* Marked ADR-0030 as superseded

## Security Mitigations

* All IAM permissions scoped to `goldenpath-*` prefix
* EC2/ELB permissions require `goldenpath-*` tags on resources
* KMS restricted to approved AWS services only
* GitHub OIDC trust limits which repos can assume role
* CloudTrail audit trail for all IAM actions

## Migration Steps

1. Copy policy from `github-actions-terraform-full.json` to AWS console
2. Apply to `github-actions-terraform` IAM role
3. Trigger new ephemeral build to verify

## Impact

* CI can apply all Terraform-managed resources without manual intervention
* No more emergency fixes for AccessDenied errors
* Policy is documented in code (single source of truth)
* Reduced operational overhead

## Follow-ups

* V1.1: Create bootstrap Terraform to manage CI permissions in code
* Add CI permission drift detection
