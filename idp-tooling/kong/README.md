---
id: IDP_TOOLING_KONG_CONFIG
title: Kong Configuration Module
type: documentation
risk_profile:
  production_impact: high
  security_risk: low
  coupling_risk: low
relates_to:
  - ADR-0002-platform-Kong-as-ingress-API-gateway
  - HELM_KONG
version: 1.0
dependencies:
  - provider:kong
supported_until: 2028-01-01
breaking_change: false
---
# Kong Configuration Module

Helm installs the Kong ingress controller (`gitops/helm/kong/`). This Terraform module manages Kong’s configuration—services, routes, plugins, consumers—so API contracts stay in code.

Use it to:

- Define upstream services/backends exposed through Kong.
- Apply authentication/rate-limiting plugins.
- Provision consumers/credentials for internal teams.

Helm keeps the controller running; Terraform keeps gateway configuration declarative and promotable.
