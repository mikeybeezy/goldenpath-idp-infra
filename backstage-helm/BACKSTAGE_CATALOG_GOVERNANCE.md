---
id: BACKSTAGE_CATALOG_GOVERNANCE
title: metadata
type: documentation
---

## 🛡️ Catalog Governance & Intake Rules

This document captures the security configuration and ingestion logic for the GoldenPath IDP Catalog.

## 1. The "Zoned Defense" Security Model

We utilize a two-tier permission system in `values-local.yaml` to ensure referential integrity.

### Tier 1: Per-Location Trust

Full permissions (`Domain`, `Group`, `User`, `System`, `Resource`) are granted **only** to the official GoldenPath repository.

### 🔒 Tier 2: Global Sandbox

The global `catalog.rules` are restricted to `Component` and `API`. This prevents developers from inadvertently (or maliciously) defining organizational structures from their own service repositories.

---

## Parity & Consistency Timings

|Setting|Value|Description|
|:---|:---|:---|
|**Processing Interval**|30s|Internal heartbeat for entity validation.|
|**Refresh Interval**|60s|Network heartbeat for GitHub polling.|
|**Consistency Target**|~3m|Expected "Time to Parity" for dynamic resource generation.|

---

## Related Documentation

- [Security Decision (ADR-0130)](../docs/adrs/ADR-0130-platform-catalog-zoned-defense-security.md)
- [Consistency Model (ADR-0129)](../docs/adrs/ADR-0129-platform-eventual-consistency-ecr-governance.md)
