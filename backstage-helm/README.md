---
id: APPS_BACKSTAGE_HELM
title: metadata
type: documentation
---

# Backstage Helm Charts

This directory contains the Helm charts and local overrides for the GoldenPath IDP Backstage instance.

## 📖 Governance & Operations
- **[Catalog Governance & Intake Rules](./BACKSTAGE_CATALOG_GOVERNANCE.md)**: Details on security rules and sync timings.
- **[Catalog Troubleshooting](./CATALOG_TROUBLESHOOTING.md)**: Guide for resolving visibility issues.

## 🚀 Deployment
Usage with local overrides:
```bash
helm upgrade backstage ./charts/backstage -f values-local.yaml
```
