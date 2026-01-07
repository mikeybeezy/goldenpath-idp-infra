---
id: 30_dev_baseline_checklist
title: Dev Environment Baseline Checklist
type: documentation
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: rerun-bootstrap
  observability_tier: bronze
schema_version: 1
relates_to:
  - BOOTSTRAP_README
  - GOLDENPATH_IDP_BOOTSTRAP
  - DEV_ENV_README
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
version: 1.0
dependencies:
  - module:kubernetes
supported_until: 2028-01-01
breaking_change: false
---

# Dev Baseline Checklist

Use this as a living checklist to validate the dev environment after bootstrap.

## Cluster access

- `aws eks update-kubeconfig` succeeds for dev.
- `kubectl get nodes` shows all nodes `Ready`.

## Core add-ons

- `coredns`, `kube-proxy`, `vpc-cni` are `Active`.
- `aws-ebs-csi-driver`, `aws-efs-csi-driver`, `snapshot-controller` are `Active`.
- Argo CD Applications include `cert-manager` and it is `Healthy` / `Synced`.

## Metrics

- Metrics Server installed.
- `kubectl top nodes` returns data.

## Storage (PV/PVC)

- StorageClass exists.
- Test PVC is `Bound`.
- Pod can mount the PVC and read/write data.

## Stateless app

- App deploys successfully.
- Service responds in-cluster.

## Stateful app

- Stateful app deploys successfully.
- PVC bound and data persists across pod restart.

## Ingress / Load balancer

- AWS Load Balancer Controller is running.
- Kong is installed and has a LoadBalancer address.
- Ingress routes traffic to the stateless app.

## GitOps sync

- Argo CD Applications exist for dev.
- Sync status is `Healthy` and `Synced`.

## Audit

- `bootstrap/0.5_bootstrap/40_smoke-tests/20_audit.sh <cluster> <region>` report saved.
