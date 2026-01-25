<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: RB-0021-backstage-helm-catalog-visibility
title: Backstage Helm Catalog Visibility (Runbook)
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0127
  - ADR-0128
supersedes: []
superseded_by: []
tags:
  - backstage
  - helm
  - catalog
  - troubleshooting
inheritance: {}
value_quantification:
  vq_class: 🟡 MV/HQ
  impact_tier: medium
  potential_savings_hours: 2.0
status: active
supported_until: 2028-01-01
version: '1.0'
dependencies:
  - kubectl
  - helm
  - curl
breaking_change: false
---

## Backstage Helm Catalog Visibility (Runbook)

This runbook provides step-by-step procedures to diagnose and fix catalog visibility issues in Backstage deployed via Helm.

Use this when:

- Backstage UI shows no catalog entities (Components, APIs, Resources, etc.)
- Catalog is empty after fresh Helm deployment
- ECR or other resources are not appearing in the portal
- Catalog was working but stopped showing entities

## Prerequisites

- Backstage is deployed via Helm in a Kubernetes cluster
- You have `kubectl` access to the namespace (default: `backstage`)
- You have `helm` CLI installed
- Port-forward to Backstage service is active (port 7007)

## Step 1: Verify Helm deployment status

Why: Ensures the Helm release exists and is in a healthy state.

```sh
helm list -n backstage
helm get values backstage -n backstage
```

Expected: Should show the backstage release with STATUS: deployed.

## Step 2: Check current catalog configuration

Why: Confirms the catalog location URL is correctly set.

```sh
kubectl get configmap -n backstage backstage-config -o yaml | grep -A 5 "DEMO_CATALOG"
```

Expected output should show:

```text
DEMO_CATALOG_LOCATION: https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/BRANCH/backstage-helm/backstage-catalog/all.yaml
```

**Problem**: If the URL is incorrect or points to PlatformersCommunity, continue to Step 5.

## Step 3: Check Backstage pod logs for errors

Why: Identifies catalog processing errors and permission issues.

```sh
kubectl logs -n backstage deployment/backstage --tail=50 | grep -i "catalog\|location\|error"
```

Common errors to look for:

- `NotAllowedError: Reading from 'https://raw.githubusercontent.com' is not allowed`
- `Unable to read url, Error: URL parsing failed`
- `401 Unauthorized` (GitHub token issues)

## Step 4: Verify catalog URL accessibility

Why: Ensures the catalog file is publicly accessible from GitHub.

```sh
curl -I "https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/BRANCH/backstage-helm/backstage-catalog/all.yaml"
```

Expected: `HTTP/2 200` response.

**Problem**: If you get 404, the file doesn't exist or the branch/path is wrong.

## Step 5: Fix catalog location URL

Why: Updates Helm deployment to point to the correct catalog.

```sh
helm upgrade backstage ./backstage-helm/charts/backstage \
  --set catalog.demoCatalogLocation='https://raw.githubusercontent.com/YOUR_ORG/YOUR_REPO/BRANCH/backstage-helm/backstage-catalog/all.yaml' \
  --namespace backstage \
  --wait
```

## Step 6: Fix backend reading permissions

Why: Backstage blocks reading from external URLs unless explicitly allowed.

Edit `backstage-helm/charts/backstage/values.yaml` and ensure the `backend` section includes:

```yaml
backend:
  baseUrl: ${BASE_URL}:7007
  listen: ':7007'

  reading:
    allow:
      - host: raw.githubusercontent.com
      - host: '*.githubusercontent.com'

  database:
    # ... rest of config
```

**Important**: There should be only ONE `backend:` section in the YAML. Duplicate sections will cause configuration to be ignored.

After editing, upgrade Helm:

```sh
helm upgrade backstage ./backstage-helm/charts/backstage \
  --namespace backstage \
  --wait
```

## Step 7: Force pod restart for fresh configuration

Why: Ensures pods load the updated ConfigMap without caching.

```sh
kubectl delete pods -n backstage -l app.kubernetes.io/name=backstage
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backstage -n backstage --timeout=60s
```

## Step 8: Verify catalog entities are loaded

Why: Confirms the fix worked and entities are now visible.

Wait 30-60 seconds for catalog processing, then check the API:

```sh
curl -s 'http://localhost:7007/api/catalog/entities' | jq 'length'
```

Expected: Should return a number greater than 0 (e.g., 39 for the full demo catalog).

To see breakdown by entity type:

```sh
curl -s 'http://localhost:7007/api/catalog/entities' | jq 'group_by(.kind) | map({kind: .[0].kind, count: length})'
```

## Step 9: Restart port-forward if needed

Why: Port-forward connections can become stale and need refreshing.

If Step 8 shows "Connection refused":

1. Stop any existing port-forward (Ctrl+C)
2. Start fresh:

```sh
kubectl port-forward svc/backstage -n backstage 7007:7007
```

1. Open browser: <http://localhost:7007>

## Verification

Navigate to **Catalog** in the Backstage UI. You should see:

- Components (13 in demo catalog)
- APIs (9 in demo catalog)
- Resources (12 with ECR entities)
- Systems and Domains

## Common Issues

### Issue: Helm values override not applied (catalog still points to development)

**Symptoms**:

- `helm get values backstage -n backstage` still shows `development` catalog URLs
- Backstage UI keeps loading the demo catalog

**Cause**:

- Helm upgrade used the upstream chart instead of the local chart, or
- The upgrade omitted one of the values files (`values-local.yaml` / `values-local.secrets.yaml`), or
- Old values persisted because Helm reused previous values.

**Fix**:

1) Upgrade using the local chart and both values files:

```sh
helm upgrade --install backstage /Users/mikesablaze/Documents/relaunch/goldenpath-idp-infra/backstage-helm/charts/backstage \
  -n backstage --create-namespace --reset-values \
  -f /Users/mikesablaze/Documents/relaunch/goldenpath-idp-infra/backstage-helm/values-local.yaml \
  -f /Users/mikesablaze/Documents/relaunch/goldenpath-idp-infra/backstage-helm/values-local.secrets.yaml
```

1) Confirm the rendered config:

```sh
helm get values backstage -n backstage
kubectl -n backstage get configmap backstage-app-config -o yaml | rg -n "catalog|DEMO_CATALOG"
```

1) Restart Backstage to pick up the new ConfigMap:

```sh
kubectl -n backstage rollout restart deployment/backstage
```

### Issue: "URL parsing failed" for "url:None"

**Cause**: The `CUSTOM_CATALOG_LOCATION` is set to "None" (string instead of unset).
**Fix**: Ensure Helm values use `customCatalogLocation: ""` or don't set it.

### Issue: Duplicate backend sections in values.yaml

**Cause**: YAML only recognizes the first key occurrence.
**Fix**: Merge all backend configuration into a single `backend:` block.

### Issue: GitHub 401 Unauthorized for private repos

**Cause**: Backstage needs a GitHub token to read private repositories.
**Fix**: Set `github.accessToken` in Helm values or via environment variable.

## Related Docs

- ADR-0127: Backstage Helm Deployment with ROI Telemetry
- ADR-0128: Automated IDP Catalog Mapping for AWS ECR
- `backstage-helm/values-local.yaml`: Example values override
