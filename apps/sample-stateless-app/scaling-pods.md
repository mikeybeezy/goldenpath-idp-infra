---
id: scaling-pods
title: kubectl cmds for scaling pods
type: documentation
category: apps
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
------

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
