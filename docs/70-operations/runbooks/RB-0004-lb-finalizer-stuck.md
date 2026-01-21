---
id: RB-0004-lb-finalizer-stuck
title: LoadBalancer Service Stuck on Finalizer
type: runbook
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: rerun-teardown
  observability_tier: silver
  maturity: 1
relates_to:
  - 08_MANAGED_LB_CLEANUP
  - 15_TEARDOWN_AND_CLEANUP
  - DOCS_RUNBOOKS_README
  - TEARDOWN_README
category: runbooks
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:kubernetes
  - chart:aws-load-balancer-controller
breaking_change: false
---

# LoadBalancer Service Stuck on Finalizer

## Purpose

Recover teardown when a Kubernetes LoadBalancer Service will not delete because
the AWS Load Balancer Controller is not running.

## What is happening (plain language)

Kubernetes adds a "finalizer" to some resources. A finalizer is a safety lock
that says: "Do not delete this object until the controller finishes cleanup."

For LoadBalancer Services, the AWS Load Balancer Controller adds this finalizer:

```
service.k8s.aws/resources
```

If the controller is not running (often because node groups were drained),
the finalizer never clears. The Service stays stuck and teardown waits forever.

## Symptoms

- Teardown hangs in Stage 2 (LoadBalancer cleanup).
- `kubectl get svc -A | rg LoadBalancer` still shows a Service.
- The controller pods are `Pending` or `CrashLoopBackOff`.

## Safe recovery steps

1) Confirm the Service is still present:

```bash
kubectl -n kong-system get svc dev-kong-kong-proxy
```

2) Check the finalizers:

```bash
kubectl -n kong-system get svc dev-kong-kong-proxy -o jsonpath='{.metadata.finalizers}'
```

If you see `service.k8s.aws/resources`, the Service is blocked by the AWS
Load Balancer Controller.

3) Remove the finalizer (forces deletion):

```bash
kubectl -n kong-system patch svc dev-kong-kong-proxy \
  -p '{"metadata":{"finalizers":[]}}' --type=merge
```

If using the v5 teardown runner, the break-glass flag defaults to on to prevent
teardown hangs when the LB controller is unavailable, but you can also set it
explicitly:

```bash
FORCE_DELETE_LB_FINALIZERS=true \
  TEARDOWN_VERSION=v5 make teardown ENV=dev BUILD_ID=<build_id> CLUSTER=<cluster> REGION=<region>
```

If Kubernetes access is unavailable, v5 skips Kubernetes cleanup and attempts
AWS-only LoadBalancer cleanup. This will not remove Service finalizers; restore
access to remove them if the Service still exists.

4) Delete the Service:

```bash
kubectl -n kong-system delete svc dev-kong-kong-proxy
```

5) Verify no LoadBalancer Services remain:

```bash
kubectl get svc -A | rg LoadBalancer
```

6) Resume teardown.

## Notes

- Removing a finalizer skips controller cleanup. If an AWS Load Balancer is
  left behind, run the orphan cleanup step (BuildId-tagged) to delete it.
- If the controller is running, prefer normal deletion without manual patching.
