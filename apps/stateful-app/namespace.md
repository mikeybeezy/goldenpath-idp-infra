---
id: STATEFUL_APP_NAMESPACE
title: Stateful App Namespace Setup
type: documentation
category: apps
version: 1.0
owner: platform-team
status: active
dependencies:
  - module:kubernetes
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: kubectl-delete
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - STATEFUL_APP_README
  - STATEFUL_APP_PVC
  - STATEFUL_APP_DEPLOY
---

# create namespace
to separate your cluster resources logically it is *best practice* to use _namespaces_. You can separate either by project, customer, team, environment,...
The benefit you gain is by getting control over resource qoutas, access control etc

```
kubectl create namespace ns-eks-course
```
