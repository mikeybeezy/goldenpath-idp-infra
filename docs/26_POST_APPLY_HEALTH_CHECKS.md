# Post-Apply Health Checks (Living Document)

This document describes the health-check gate that runs after Terraform apply.

## What it checks (binary)

- EKS reachable (kubectl can list nodes)
- Nodes Ready
- Argo CD root app is Synced + Healthy
- Kong health endpoint returns success

## Data inputs

- Cluster name (from Terraform vars or outputs)
- Argo root app name (per env)
- Kong health URL or service reference

## ASCII flow

```
+--------------------+     +-----------------+     +-------------------------+
| Terraform apply    | --> | Bootstrap phase | --> | Post-apply health checks |
+--------------------+     +-----------------+     +-------------------------+
                                                         |   |      |
                                                         v   v      v
                                                    [EKS OK] [Argo OK] [Kong OK]
                                                         \    |     /
                                                          \   |    /
                                                           \  |   /
                                                           [READY]
                                                            /   \
                                                   pass -> /     \ -> fail
```

## Checklist (per environment)

- [ ] EKS reachable (`kubectl get nodes`)
- [ ] All nodes Ready
- [ ] Argo root app Synced and Healthy
- [ ] Kong health endpoint returns 200

## Failure handling

- Fail the workflow with a clear message.
- Retry up to 3 times with a 30s backoff if the failure looks transient.

## Change process

- Update ADR if checks change materially.
- Keep this doc aligned with the workflow.

## Deferment

Health checks will be wired into CI after multi-environment cluster bring-up and teardown are
stable in CI.
