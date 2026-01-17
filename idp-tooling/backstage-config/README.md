---
id: IDP_TOOLING_BACKSTAGE_CONFIG
title: Backstage Configuration Module
type: documentation
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: low
relates_to:
  - ADR-0008-app-backstage-portal
  - HELM_BACKSTAGE
version: 1.0
dependencies:
  - provider:backstage
supported_until: 2028-01-01
breaking_change: false
---
# Backstage Configuration Module

Helm installs Backstage (`gitops/helm/backstage`). This Terraform module stores Backstage catalog entities, locations, groups, and plugin settings so the portal’s structure is managed as code.

Use it to:

- Register default catalog locations (Git repos, templates).
- Seed groups/users/service metadata.
- Configure integrations (GitHub, GitLab, Argo CD) via Backstage APIs.

Result: Backstage content stays version-controlled and consistent across environments; Helm only handles runtime deployment.
