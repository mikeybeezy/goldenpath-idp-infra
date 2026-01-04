---
id: IDP_TOOLING_KONG_CONFIG
title: Kong Configuration Module
type: documentation
category: idp-tooling
version: 1.0
owner: platform-team
status: active
dependencies:
  - provider:kong
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - HELM_KONG
  - ADR-0002
---

# Kong Configuration Module

Helm installs the Kong ingress controller (`gitops/helm/kong/`). This Terraform module manages Kong’s configuration—services, routes, plugins, consumers—so API contracts stay in code.

Use it to:

- Define upstream services/backends exposed through Kong.
- Apply authentication/rate-limiting plugins.
- Provision consumers/credentials for internal teams.

Helm keeps the controller running; Terraform keeps gateway configuration declarative and promotable.
