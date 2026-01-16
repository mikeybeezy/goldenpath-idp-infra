---
id: RB-0022-backstage-techdocs-setup
title: Enabling Native TechDocs Rendering
type: runbook
domain: idp
tags:
  - backstage
  - techdocs
  - documentation
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
  frequency: monthly
  time_saved_per_run: 2h
  risk_reduction: medium
category: runbooks
---

## Runbook: Enabling Native TechDocs Rendering

## Overview

This runbook details how to enable native markdown rendering (TechDocs) for Backstage components. This allows documentation (like ADRs, Changelogs, and Health Reports) to be read directly within the Backstage UI without navigating to GitHub.

## 🛠️ Prerequisites

1. **`mkdocs.yml`**: Must exist in the root of the repository (or the target directory).
2. **Helm Configuration**: `values.yaml` must enable local building.

    ```yaml
    backstage:
      techdocs:
        builder: 'local'
        generator:
          runIn: 'local'
        publisher:
          type: 'local'
    ```

3. **Backend Permissions**: The `backend.reading.allow` list must include GitHub.

    ```yaml
    backstage:
      appConfig:
        backend:
          reading:
            allow:
              - host: raw.githubusercontent.com
    ```

## Procedure: Enabling TechDocs for a Component

To turn a standard Component into a Documentation Portal:

1. **Locate the Component YAML**
    * Example: `backstage-helm/backstage-catalog/components/platform-health.yaml`

2. **Add the TechDocs Annotation**
    Add `backstage.io/techdocs-ref: dir:.` to the `metadata.annotations` section.

    ```yaml
    apiVersion: backstage.io/v1alpha1
    kind: Component
    metadata:
      name: platform-health-dashboard
      annotations:
        github.com/project-slug: mikeybeezy/goldenpath-idp-infra
        backstage.io/techdocs-ref: dir:.  <-- THIS LINE ENABLES RENDERING
    ```

    * `dir:.` means "build the TechDocs site from the current directory (root) of the repo defined in project-slug".

3. **Deploy Changes**
    * Commit and push the YAML change.
    * Restart Backstage pods to pick up the catalog change immediately (or wait for refresh).

4. **Verify**
    * Open the Component in Backstage.
    * Click the **"Docs"** tab.
    * Verify the left navigation matches your `mkdocs.yml`.

## Troubleshooting

### "Failed to generate docs" or "Builder not found"

* **Cause**: The Backstage container might lack `mkdocs` or `techdocs-core`.
* **Fix**: Ensure your Backstage image includes these dependencies, or switch to `techdocs.builder: 'external'` (requires S3/GCS).

### "Authentication failed" or "FetchUrlReader" errors

* **Cause**: The `GITHUB_TOKEN` in `backstage-secrets` is missing, invalid, or lacks scopes.
* **Fix**: Update the secret with a Classic Token having these scopes:
  * **repo** (Required for reading software components)
  * **read:org**, **read:user**, **user:email** (Reading organization data)
  * **workflow** (If templates include GitHub workflows)

```bash
kubectl create secret generic backstage-secrets \
  --from-literal=GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE \
  --from-literal=POSTGRES_PASSWORD=password \
  --from-literal=POSTGRES_USER=app \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Docs are stale

* **Cause**: Local builder caches builds.
* **Fix**: In a `local` setup, restarting the pod usually clears the cache. In production `external` setups, trigger a rebuild via the API.
