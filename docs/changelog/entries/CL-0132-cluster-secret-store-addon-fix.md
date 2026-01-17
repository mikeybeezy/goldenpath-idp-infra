---
id: CL-0132
title: ClusterSecretStore Addon Deployment Fix
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0135
  - ADR-0143
  - CL-0132
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - secrets
  - eso
  - addons
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
supported_until: '2028-01-01'
date: 2026-01-15
---

## CL-0132: ClusterSecretStore Addon Deployment Fix

**Type**: Bug Fix
**Component**: Infrastructure / EKS Addons
**Date**: 2026-01-15
**Related**: ADR-0135, ADR-0143

## Problem Statement

The `ClusterSecretStore` resource (required for External Secrets Operator to sync from AWS Secrets Manager) was not being deployed during the `make apply` phase when `var.apply_kubernetes_addons = false`. This caused `ExternalSecret` resources to fail with `SecretSyncedError` because the backend connection was missing.

## Root Cause

The `kubernetes_manifest.cluster_secret_store` resource in `envs/dev/main.tf` had a `count` condition tied to `var.apply_kubernetes_addons`:

```hcl
count = var.apply_kubernetes_addons ? 1 : 0
```

This prevented the ClusterSecretStore from being created during infrastructure provisioning, requiring manual intervention.

## Solution

The ClusterSecretStore should be deployed as part of the standard EKS addon workflow. The resource configuration exists in `envs/dev/main.tf` (lines 460-489) and includes:

* Dependency on ESO namespace and service account
* IRSA role ARN reference for AWS authentication
* Proper configuration for AWS Secrets Manager backend

## Action Items

* [x] Document the issue in this changelog
* [ ] Review `var.apply_kubernetes_addons` usage across all environments
* [ ] Consider splitting addon deployment into "infrastructure-critical" (ESO, ClusterSecretStore) vs "application-level" (ArgoCD apps)
* [ ] Update platform documentation to reflect ClusterSecretStore as a core addon

## Verification

```bash
# Verify ClusterSecretStore exists
kubectl get clustersecretstore aws-secretsmanager

# Verify it's Valid and Ready
kubectl get clustersecretstore aws-secretsmanager -o jsonpath='{.status.conditions[*].type}'
```

## References

* Issue discovered during: V1 Stabilization (Build ID: 15-01-26-15)
* Manual fix applied: `kubectl apply -f cluster-secret-store.yaml`
* Documentation: `/docs/70-operations/35_TOOLING_SECRETS_LIFECYCLE.md`
