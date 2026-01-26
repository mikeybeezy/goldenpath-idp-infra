---
id: CL-0198-argocd-lbc-webhook-race-fix
title: ArgoCD/LBC Webhook Race Condition Fix
type: changelog
domain: platform-core
applies_to:
  - modules/kubernetes_addons
owner: platform-team
lifecycle: active
exempt: false
schema_version: 1
relates_to:
  - session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success
  - ADR-0180-argocd-orchestrator-contract
supersedes: []
superseded_by: []
tags:
  - terraform
  - argocd
  - aws-load-balancer-controller
  - race-condition
  - hotfix
inheritance: {}
status: active
category: platform
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# CL-0198: ArgoCD/LBC Webhook Race Condition Fix

**Date:** 2026-01-27
**Author:** platform-team + Claude Opus 4.5
**Branch:** feature/tdd-foundation

## Summary

Fixed a race condition in `modules/kubernetes_addons/main.tf` where ArgoCD and
AWS Load Balancer Controller (LBC) Helm releases were deployed in parallel,
causing intermittent deployment failures.

## Problem

When running `make deploy-persistent ENV=dev BOOTSTRAP_VERSION=v4`, the deployment
would fail with:

```
Error: failed calling webhook "mservice.elbv2.k8s.aws": failed to call webhook:
Post "https://aws-load-balancer-webhook-service.kube-system.svc:443/mutate-v1-service":
no endpoints available for service "aws-load-balancer-webhook-service"
```

## Root Cause

1. `helm_release.argocd` and `helm_release.aws_load_balancer_controller` had no
   dependency between them and were created **in parallel**
2. LBC installs a MutatingWebhookConfiguration that intercepts Service creation
3. ArgoCD creates Services (argocd-server, argocd-repo-server, etc.) during install
4. When ArgoCD created Services, the LBC webhook intercepted them
5. If LBC pods weren't ready yet, the webhook had no endpoints and Service creation failed

## Fix Applied

Added explicit dependency from ArgoCD to LBC:

```terraform
resource "helm_release" "argocd" {
  # ... config ...

  # ArgoCD creates Services/Ingresses that get intercepted by the LBC webhook.
  # LBC must be fully deployed first or the webhook has no endpoints.
  depends_on = [helm_release.aws_load_balancer_controller]
}
```

## Deployment Order (After Fix)

1. `helm_release.aws_load_balancer_controller` - LBC deployed first
2. LBC pods become ready, webhook has endpoints
3. `helm_release.argocd` - ArgoCD deployed, Services created successfully
4. `helm_release.bootstrap_apps` - depends on both, runs last

## Files Modified

| File | Change |
|------|--------|
| `modules/kubernetes_addons/main.tf` | Added `depends_on = [helm_release.aws_load_balancer_controller]` to argocd |

## Prevention

This dependency ordering is now codified in Terraform. Future deployments will
always deploy LBC before ArgoCD, preventing the webhook race condition.

## Historical Context

A similar webhook issue was encountered on 2026-01-23 (documented in
`session_capture/2026-01-23-v1-milestone-ephemeral-deploy-success.md`) where the
error was "IngressClass.networking.k8s.io kong not found". That fix added
`kubernetes_ingress_class_v1.kong` as a dependency. This fix addresses a
different race condition with the webhook Service endpoints.

## Verification

```bash
make deploy-persistent ENV=dev REGION=eu-west-2 BOOTSTRAP_VERSION=v4 CREATE_RDS=false SKIP_ARGO_SYNC_WAIT=true
```

Deploy should complete without webhook endpoint errors.
