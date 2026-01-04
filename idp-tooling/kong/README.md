---
id: README
title: Kong Configuration Module
type: documentation
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
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Kong Configuration Module

Helm installs the Kong ingress controller (`gitops/helm/kong/`). This Terraform module manages Kong’s configuration—services, routes, plugins, consumers—so API contracts stay in code.

Use it to:
- Define upstream services/backends exposed through Kong.
- Apply authentication/rate-limiting plugins.
- Provision consumers/credentials for internal teams.

Helm keeps the controller running; Terraform keeps gateway configuration declarative and promotable.
