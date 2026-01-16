---
id: PLUGIN_ENABLEMENT_MATRIX
title: Backstage Plugin Enablement Matrix (Helm + Stock Image)
type: documentation
---

## Backstage Plugin Enablement Matrix (Helm + Stock Image)

Purpose: clarify what can be enabled via config-only (Helm values) versus what
requires a custom Backstage image.

Assumptions:

- The running image is built from `goldenpath-idp-backstage/goldenpath`.
- The Helm chart mounts `app-config.cm.yaml` only (no dynamic plugin loader).

If the image differs, verify the compiled plugin list before relying on the
"Config-only" column below.

## Summary

- Config-only enablement is possible only for plugins already compiled into the
  image.
- Any new plugin (frontend or backend) requires a custom image.
- Dynamic plugins are not configured in this chart.

## Plugin Matrix

Legend:

- Config-only: "Yes" means you can enable/configure via `values.yaml` or
  `values-local.yaml` without rebuilding the image.
- Custom image: "Yes" means you must rebuild to add or change plugin code.

|Plugin|Layer|What it does|Config-only|Custom image|Notes|
|---|---|---|---|---|---|
|catalog|frontend+backend|Indexes and serves software entities.|Yes|No|Already wired in Helm values.|
|catalog-import|frontend|Imports entities from external locations.|Yes|No|UI-only; config only.|
|catalog-graph|frontend|Visualizes entity relationships.|Yes|No|UI-only; config only.|
|techdocs|frontend+backend|Renders documentation sites from repo docs.|Yes|No|Uses local builder/publisher in values.|
|scaffolder|frontend+backend|Scaffolds new services/templates.|Yes|No|Config-only if templates exist.|
|kubernetes|frontend+backend|Shows K8s workloads/health for entities.|Yes|No|Requires cluster config in values.|
|search|frontend+backend|Unified search across catalog and docs.|Yes|No|Backend modules present (pg/catalog/techdocs).|
|api-docs|frontend|Displays API docs (OpenAPI/AsyncAPI).|Yes|No|UI-only; depends on catalog entities.|
|org|frontend|Manages org structure (groups/users).|Yes|No|Uses Group/User entities in catalog.|
|user-settings|frontend|User profile/preferences UI.|Yes|No|UI-only; config only.|
|notifications|frontend+backend|In-product notifications and events.|Yes|No|Backend present; config-only.|
|signals|frontend+backend|Real-time event stream for UI components.|Yes|No|Backend present; config-only.|
|auth (github/guest)|backend|Authentication providers and sessions.|Yes|No|Providers available; values drive config.|
|permissions|backend|Permission policy evaluation.|Yes|No|Allow-all policy module present.|
|proxy|backend|Proxies external APIs for frontend use.|Yes|No|Config-only per app-config.|

## What Requires a Custom Image

You must build a custom image to:

- Add any plugin not listed above.
- Add custom UI routes, pages, or theme overrides.
- Add backend modules not already in `packages/backend`.
- Use enterprise plugins not bundled in the repo.

## What We Can Do Today (Config-Only)

Examples that do not require a custom image:

- Enable TechDocs for ADRs/changelogs/governance via catalog entities.
- Turn on Kubernetes plugin against in-cluster or remote clusters.
- Extend scaffolder with new templates in `backstage-helm/backstage-catalog/templates`.
- Enable additional search collators via config if the module exists.

## Gaps to Resolve Before Custom Image

- Confirm the running image is built from `goldenpath-idp-backstage/goldenpath`.
- Align `app-config.yaml` between the app repo and Helm values to avoid drift.
- Decide which plugins are V1-critical to justify image build work.

## V1 Recommendations

Priority if staying config-only:

1. Catalog + TechDocs + Scaffolder + Kubernetes + Search.
2. Notifications + Org + API Docs.

Trigger for custom image:

- Need to add any new plugin or custom UI surface beyond config.

## V1 Recommendation Matrix

|Recommendation|What it does|Why it matters in V1|Enabled (V1)|
|---|---|---|---|
|Catalog|Indexes and serves software entities.|Establishes the system of record for services and docs.|Yes|
|TechDocs|Renders documentation sites from repo docs.|Makes ADRs, governance, and runbooks readable.|Yes|
|Scaffolder|Creates new services from templates.|Implements the golden path for new projects.|Yes|
|Kubernetes|Shows K8s workloads/health for entities.|Provides deployment visibility per service.|Yes|
|Search|Unified search across catalog and docs.|Reduces time-to-find across platform assets.|Yes|
|Notifications|In-product notifications and events.|Surfaces workflow outcomes and alerts.|Yes|
|Org|Manages org structure (groups/users).|Enables ownership, routing, and accountability.|Yes|
|API Docs|Displays API docs (OpenAPI/AsyncAPI).|Improves discoverability of service interfaces.|Yes|
