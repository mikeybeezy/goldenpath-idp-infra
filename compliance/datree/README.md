---
id: COMPLIANCE_DATREE_README
title: Datree Policies
type: documentation
category: compliance
version: '1.0'
owner: platform-team
status: active
dependencies: []
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

# Datree Policies

Datree enforces Kubernetes best practices in two places:

1. **CI checks** – the Datree CLI runs during pull requests to catch manifest violations (e.g., missing resource limits, `:latest` tags) before code merges.
2. **Admission webhook** – the Helm chart in `gitops/helm/datree/` deploys Datree’s validating webhook so that any manifest applied to the cluster is evaluated again. If CI missed something, the webhook blocks it at runtime.

This directory stores the Datree policy definitions (YAML) and documentation on how to run the CLI locally/inside CI. Keeping policies here ensures they’re version-controlled and evolve with the platform.
