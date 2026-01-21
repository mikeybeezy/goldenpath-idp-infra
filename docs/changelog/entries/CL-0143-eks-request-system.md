---
id: CL-0143
title: EKS Request System
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
  - ADR-0165
  - ADR-0168
  - CL-0142
  - EKS_REQUEST_FLOW
  - session-2026-01-17-eks-backstage-scaffolder
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-17
---

# CL-0143: EKS Request System

## Summary

Implements the EKS request-file + parser pattern for self-service cluster provisioning, aligning with the RDS and Secrets request flows.

## Changes

### Added

- `scripts/eks_request_parser.py` - Parser that validates EKS request files and generates tfvars
- `schemas/requests/eks.schema.yaml` - JSON Schema for EKS request validation
- `.github/workflows/eks-request-apply.yml` - Manual workflow to apply EKS requests
- `.github/workflows/ci-eks-request-validation.yml` - CI validation for EKS request files
- `docs/20-contracts/eks-requests/dev/EKS-0001.yaml` - Sample EKS request file
- `schemas/metadata/enums.yaml` - Extended with EKS-specific enums

### Features

- **Mode support**: `cluster-only`, `bootstrap-only`, `cluster+bootstrap`
- **Environment parameterization**: Bucket, lock table, and IAM role resolved per environment
- **Non-dev guard**: Requires `allow_non_dev=true` for staging/prod applies
- **Mode-aware outputs**: `enable_k8s_resources` and `apply_kubernetes_addons` set based on mode
- **Warning emissions**: Non-wired fields (IRSA, ingress, bootstrap_profile) emit warnings

## Usage

```bash
# Validate an EKS request
python scripts/eks_request_parser.py \
  --mode validate \
  --input-files docs/20-contracts/eks-requests/dev/EKS-0001.yaml \
  --enums schemas/metadata/enums.yaml

# Generate tfvars from request
python scripts/eks_request_parser.py \
  --mode generate \
  --input-files docs/20-contracts/eks-requests/dev/EKS-0001.yaml \
  --enums schemas/metadata/enums.yaml
```

## Related

- Session capture: `session_capture/2026-01-17-eks-backstage-scaffolder-design.md`
- EKS scope gate: CL-0142
