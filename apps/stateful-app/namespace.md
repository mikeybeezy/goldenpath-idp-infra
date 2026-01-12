---
id: namespace
title: Stateful App Namespace Setup
type: documentation
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: kubectl-delete
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - STATEFUL_APP_README
  - STATEFUL_APP_PVC
  - STATEFUL_APP_DEPLOY
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: 1.0
dependencies:
  - module:kubernetes
supported_until: 2028-01-01
breaking_change: false
---

# create namespace

to separate your cluster resources logically it is *best practice* to use *namespaces*. You can separate either by project, customer, team, environment,...
The benefit you gain is by getting control over resource qoutas, access control etc

```
kubectl create namespace ns-eks-course
```
