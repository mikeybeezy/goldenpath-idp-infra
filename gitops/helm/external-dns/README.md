---
id: HELM_EXTERNAL_DNS
title: ExternalDNS Helm Chart (Values)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - PRD-0002-route53-externaldns
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
  - chart:external-dns
  - image:external-dns
supported_until: 2028-01-01
breaking_change: false
---
# ExternalDNS Helm Deployment

ExternalDNS manages DNS records in Route53 based on Kubernetes Services and
Ingress resources. Values are pinned per environment.

```
gitops/helm/external-dns/
└── values/
    ├── dev.yaml
    ├── test.yaml
    ├── staging.yaml
    └── prod.yaml
```

Argo CD Applications (for example `gitops/argocd/apps/dev/external-dns.yaml`)
pull the relevant file via `$values/gitops/helm/external-dns/values/<env>.yaml`.
