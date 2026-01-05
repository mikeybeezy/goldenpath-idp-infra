---
id: IDP_TOOLING_BACKSTAGE_CONFIG
title: Backstage Configuration Module
type: documentation
category: idp-tooling
version: 1.0
owner: platform-team
status: active
dependencies:
  - provider:backstage
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - HELM_BACKSTAGE
  - ADR-0008
---

# Backstage Configuration Module

Helm installs Backstage (`gitops/helm/backstage`). This Terraform module stores Backstage catalog entities, locations, groups, and plugin settings so the portal’s structure is managed as code.

Use it to:

- Register default catalog locations (Git repos, templates).
- Seed groups/users/service metadata.
- Configure integrations (GitHub, GitLab, Argo CD) via Backstage APIs.

Result: Backstage content stays version-controlled and consistent across environments; Helm only handles runtime deployment.
