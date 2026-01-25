---
id: CL-0173
title: Kong URLs Updated in Tooling Matrix
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
  - CL-0170-kong-manager-ingress
  - CL-0171-kong-admin-api-ingress
  - CL-0172-kong-admin-api-tls-fix
  - 20_TOOLING_APPS_MATRIX
supersedes: []
superseded_by: []
tags: []
inheritance: {}
supported_until: '2028-01-01'
date: 2026-01-24
author: platform-team
breaking_change: false
---

## Summary

Updated Platform Tooling Apps Matrix documentation with correct Kong URLs.

## Changes

### Dev Environment URLs

| Service | Old URL | New URL |
|---------|---------|---------|
| Kong Manager | `https://kong.dev.goldenpathidp.io` | `https://kong-manager.dev.goldenpathidp.io` |
| Kong Admin API | (not listed) | `https://kong-admin.dev.goldenpathidp.io` |

### Staging Environment URLs

| Service | Old URL | New URL |
|---------|---------|---------|
| Kong Manager | `https://kong.staging.goldenpathidp.io` | `https://kong-manager.staging.goldenpathidp.io` |

### Production Environment URLs

| Service | Old URL | New URL |
|---------|---------|---------|
| Kong Manager | `https://kong.goldenpathidp.io` | `https://kong-manager.goldenpathidp.io` |

### Example Configuration Updated
- Updated Kong values example in documentation to use correct hostname pattern

### Changelog Section Updated
- Added entry: "Updated Kong Manager hostname to `kong-manager.{env}.goldenpathidp.io` (ingress enabled)"

## Files Changed

- `docs/70-operations/20_TOOLING_APPS_MATRIX.md`

## Hostname Naming Convention

The new naming follows the pattern: `{service}-{role}.{env}.goldenpathidp.io`

- `kong-manager` - UI for viewing Kong configuration
- `kong-admin` - API for managing Kong (internal/dev only)

This distinguishes Kong Manager (UI) from Kong Admin API (API) and aligns with other services like `argocd`, `backstage`, `grafana`.

## Impact

- Documentation only change
- No runtime impact
- Ensures developers use correct URLs
