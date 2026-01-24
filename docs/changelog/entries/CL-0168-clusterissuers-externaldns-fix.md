---
id: CL-0168
title: ClusterIssuers and ExternalDNS Fixes
type: changelog
date: 2026-01-24
author: platform-team
breaking_change: false
---

## Summary

Fixed TLS certificate issuance and DNS record management for dev cluster.

## Changes

### ClusterIssuers for cert-manager
- Added `letsencrypt-staging`, `letsencrypt-prod`, and `selfsigned-issuer` ClusterIssuers
- Updated cert-manager ArgoCD Application to include kustomize source for ClusterIssuers
- Enables HTTP-01 ACME challenges for TLS certificate issuance

### ExternalDNS domainFilters Fix
- Removed incorrect `domainFilters[0]=dev.goldenpathidp.io` injection from Terraform
- ExternalDNS now uses correct apex domain (`goldenpathidp.io`) from values/dev.yaml
- Fixed hosted zone discovery for DNS record management

### Cleanup Script Improvements
- Added retry logic with exponential backoff for security group cleanup
- Handles transient ENI detachment delays after LB deletion

### Governance
- Added PROMPT-0004 hotfix policy with 25 requirements
- Enforces permanent fixes with prevention

## Impact

- Non-breaking change
- Fixes DNS and TLS for dev cluster
- Enables proper certificate issuance via Let's Encrypt staging
