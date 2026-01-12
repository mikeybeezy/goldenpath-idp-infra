---
id: HELM_KONG
title: Kong Ingress Controller Helm Chart (Values)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0002
  - HELM_CERT_MANAGER
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: delivery
status: active
version: 1.0
dependencies:
  - chart:kong
  - image:kong
supported_until: 2028-01-01
breaking_change: false
---

# Kong Helm Deployment

Kong acts as the platform's ingress/API gateway, handling routing, auth, and policies for north-south traffic.

## Kong Manager UI

Kong Manager is the web UI for managing services, routes, plugins, and
certificates. It is powerful and should be treated as admin access.

We enabled Kong Manager for demo and validation. It is kept private (ClusterIP)
and should be exposed only through an authenticated ingress.

Temporary basic auth approach:

- Keep the Manager service as ClusterIP.
- Expose it via a Kong Ingress and attach a `basic-auth` plugin.
- Create a KongConsumer with basic auth credentials for limited access.

Backstage integration is possible later via a catalog link or a custom plugin,
so users can discover the UI without exposing it publicly.

```
gitops/helm/kong/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications under `gitops/argocd/apps/<env>/kong.yaml` reference these value files via `$values/gitops/helm/kong/values/<env>.yaml`.
