---
id: CL-0144
title: Secrets Scaffolder Workflow Dispatch
type: changelog
domain: platform-core
owner: platform-team
status: active
date: 2026-01-17
relates_to:
  - SECRET_REQUEST_FLOW
  - ADR-0135
---

# CL-0144: Secrets Scaffolder Workflow Dispatch

## Summary

Updates the Backstage secrets scaffolder to use workflow dispatch instead of direct PR creation, reusing the existing `request-app-secret.yml` workflow.

## Changes

### Modified

- `backstage-helm/backstage-catalog/templates/secret-request.yaml`
  - Changed from `fetch:template` + `publish:github:pull-request` to `github:actions:dispatch`
  - Now triggers `request-app-secret.yml` directly
  - Added `recovery_window` calculation based on risk level
  - Output links updated to workflow runs page

- `.github/workflows/secret-approval-guard.yml`
  - Added `workflow_dispatch` input for `warn_only` mode
  - Improved YAML parsing to use `yaml.safe_load` instead of regex
  - Better error handling for malformed files

### Removed

- `backstage-helm/backstage-catalog/templates/skeletons/secret-request/${{ values.secret_name }}.yaml`
  - Skeleton template no longer needed (workflow creates request file)

### Added

- `backstage-helm/backstage-catalog/templates/skeletons/secret-request/${{ values.request_id }}.yaml`
  - New skeleton with request_id-based naming

## Flow

```
Backstage form → workflow dispatch → request-app-secret.yml
                                           ↓
                         Creates request YAML + runs parser
                                           ↓
                         Generates tfvars + ExternalSecret
                                           ↓
                         Creates PR → approval guard runs
```

## Benefits

- Reuses existing workflow logic (DRY)
- Parser generates ESO manifests consistently
- Single source of truth for secret request creation
