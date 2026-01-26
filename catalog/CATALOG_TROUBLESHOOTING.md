---
id: CATALOG_TROUBLESHOOTING
title: metadata
type: documentation
---

## Backstage Catalog Visibility Troubleshooting

## Problem

Backstage running localhost shows no catalog entities, including ECR resources.

## Root Cause

The Helm chart's default `values.yaml` points to a **remote catalog**:

```yaml
catalog:
  catalogLocation: "https://github.com/PlatformersCommunity/backstage-helm-chart/blob/main/catalog/all.yaml"
```

This loads entities from the PlatformersCommunity demo, **not** your local `catalog` with ECR resources.

## Solution

### Option 1: Update Helm Deployment (Recommended)

Use the provided `values-local.yaml` override:

```bash
# Re-deploy Backstage with local catalog
helm upgrade backstage ./gitops/helm/backstage/chart \
  -f gitops/helm/backstage/values/local.yaml \
  --namespace backstage
```

### Option 2: Quick CLI Override

```bash
helm upgrade backstage ./gitops/helm/backstage/chart \
  --set catalog.catalogLocation='https://raw.githubusercontent.com/mikeybeezy/goldenpath-idp-infra/main/catalog/all.yaml' \
  --namespace backstage
```

### Option 3: Local Development Mode

If running Backstage in local dev mode (yarn dev):

1. Update `app-config.yaml` in your Backstage app:

```yaml
catalog:
  locations:
    - type: file
      target: /absolute/path/to/goldenpath-idp-infra/catalog/all.yaml
```

## Verification

After updating the catalog location:

1. Wait 30-60 seconds for Backstage to refresh
2. Navigate to Catalog → Default
3. You should now see:
   - **12 Resources** (1 ECR Registry + 10 Repositories + 1 DB)
   - **13 Components**
   - **9 APIs**
   - **3 Systems**
   - **2 Domains**

## Current Status

- ✅ ECR catalog bridge created: `scripts/generate_backstage_ecr.py`
- ✅ Backstage entities generated: `catalog/resources/ecr/`
- ✅ Resource index updated: `catalog/all-resources.yaml`
- ⚠️ **Catalog location needs configuration update**
