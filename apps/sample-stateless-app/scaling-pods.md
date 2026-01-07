---
id: scaling-pods
title: kubectl cmds for scaling pods
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
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - deploy-sample-app
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
status: active
version: '1.0'
dependencies:
  - SAMPLE_STATELESS_APP
supported_until: 2028-01-01
breaking_change: false
---

## kubectl cmds for scaling pods

scaling a deployment:

```
kubectl scale --replicas <number-of-replicas> deployment <name-of-deployment>
```

e.g. set no of replicas for _frontend_ service to _5_ :

```
kubectl scale --replicas 5 deployment frontend
```

## commands to check state

* get all pods incl additional info like e.g. k8s worker node the pod is running on

```
kubectl get pods -o wide
```

* state of service(s)

```
kubectl get services
```

details of a particular service:

```
kubectl describe service <servicename>
```
