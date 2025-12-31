# CL-0002: Kube-prometheus-stack baseline and storage defaults

Date: 2025-12-31
Owner: platform
Scope: monitoring, bootstrap, gitops
Related: docs/adrs/ADR-0052-platform-kube-prometheus-stack-bundle.md, docs/adrs/ADR-0053-platform-storage-lifecycle-separation.md

## Summary

- Replace standalone Prometheus/Grafana/Alertmanager with kube-prometheus-stack.
- Persist monitoring data by default and validate storage add-ons during bootstrap.
- Document storage defaults, sizing, and tradeoffs.

## Impact

- Monitoring apps move to a single Argo CD bundle in the `monitoring` namespace.
- Storage add-ons must be Active for bootstrap to succeed when persistence is required.

## Changes

### Added

- kube-prometheus-stack Helm values and Argo CD Applications per environment.
- Storage add-on validation during bootstrap when enabled.
- Storage and persistence living doc.

### Changed

- Monitoring baseline now uses kube-prometheus-stack (45.7.1).
- Storage add-ons are treated as default for persistent monitoring data.

### Fixed

- N/A.

### Deprecated

- Standalone Prometheus/Grafana/Alertmanager app manifests (retained only for reference docs).

### Removed

- Argo CD Applications for standalone Prometheus/Grafana/Alertmanager.

### Documented

- StorageClass defaults vs gp3 tradeoffs and baseline sizing.

### Known limitations

- Storage cleanup remains a separate workflow from teardown.

## Rollback / Recovery

- Reintroduce standalone monitoring apps and disable kube-prometheus-stack.

## Validation

- Not run (requires cluster apply + Argo sync).
