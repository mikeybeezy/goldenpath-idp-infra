---
id: namespace
title: create namespace
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

# create namespace
to separate your cluster resources logically it is *best practice* to use _namespaces_. You can separate either by project, customer, team, environment,...
The benefit you gain is by getting control over resource qoutas, access control etc

```
kubectl create namespace ns-eks-course
```
