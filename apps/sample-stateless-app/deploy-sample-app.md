---
id: deploy-sample-app
title: Setup sample guestbook app
type: documentation
category: apps
version: '1.0'
owner: platform-team
status: active
dependencies:
- SAMPLE_STATELESS_APP
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
relates_to:
- scaling-pods
---

# Setup sample guestbook app

* based on <https://github.com/kubernetes/examples/tree/master/guestbook>

## Redis master

deploy the master Redis pod and a _service_ on top of it:

```
kubectl apply -f redis-master.yaml
kubectl get pods
kubectl get services
```

## Redis slaves

deploy the Redis slave pods and a _service_ on top of it:

```
kubectl apply -f redis-slaves.yaml
kubectl get pods
kubectl get services
```

## Frontend app

deploy the PHP Frontend pods and a _service_ of type **LoadBalancer** on top of it, to expose the loadbalanced service to the public via ELB:

```
kubectl apply -f frontend.yaml
```

some checks:

```
kubectl get pods
kubectl get pods -l app=guestbook
kubectl get pods -l app=guestbook -l tier=frontend
```

check AWS mgm console for the ELB which has been created !!!

## Access from outside the cluster

grab the public DNS of the frontend service LoadBalancer (ELB):

```
kubectl describe service frontend
```

copy the name and paste it into your browser !!!
