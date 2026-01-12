---
id: 11_SECRETS_CATALOG_POLICY
title: Secrets Cataloging Policy (Backstage)
type: policy
domain: security
risk_profile:
  production_impact: low
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 10_SECRET_SCANNING_POLICY
  - 35_RESOURCE_TAGGING
  - ADR-0138
  - ADR-0139
tags:
  - governance
  - security
  - secrets
category: governance
supported_until: 2027-01-03
version: '1.0'
breaking_change: false
---

# Secrets Cataloging Policy (Backstage)

Purpose: define when secrets infrastructure is first-class in Backstage and how
to model it without catalog sprawl.

## What is first-class (Resource)

Catalog AWS Secrets Manager resources only when they are:

- shared across services or teams
- medium+ risk or security-critical
- long-lived platform secrets (OIDC clients, shared integrations)
- required for onboarding or audits

## What is not first-class

Do not create a Backstage entity per `ExternalSecret` or per app secret. Link
app-specific secrets from the service entity instead.

## Required Backstage model (V1)

- **System**: `secrets-platform`
- **Component**: `external-secrets-operator`
- **Resources**: `aws-secrets-manager-dev`, `aws-secrets-manager-test`,
  `aws-secrets-manager-staging`, `aws-secrets-manager-prod`

Relationships:

- component -> system
- resource -> system
- resource -> ownedBy (platform-team / security-team)

## Terraform representation (alignment)

Every Secrets Manager resource must include:

- `goldenpath.idp/id` (unique per instance, per environment)
- `goldenpath.idp/logical_id` (shared logical grouping)
- `Owner`, `Environment`, and standard tags per
  `docs/10-governance/35_RESOURCE_TAGGING.md`

## Coupled updates

If tag keys change, update this policy and
`docs/10-governance/35_RESOURCE_TAGGING.md` together in the same PR.

## Enforcement

- Reviewers must reject catalog entries that violate the scope rules above.
- Catalog entities must map to Terraform-managed resources (no manual drift).
