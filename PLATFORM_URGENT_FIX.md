<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: PLATFORM_URGENT_FIX
title: Platform Urgent Fix Matrix (V1-Aligned)
type: documentation
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0120-metadata-inheritance-and-active-governance
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
---
## Platform Urgent Fix Matrix (V1-Aligned)

This matrix extends the prioritized fix list with issue descriptions and the
expected result of each resolution. It is intentionally focused on V1 safety,
accuracy, and determinism.

|ID|Area|Issue|Description|Impact|Effort|V1 Alignment|Priority|Resolution Result|
|---|---|---|---|---|---|---|---|---|
|S1|Scripts|backfill_metadata.py missing imports|Script fails at runtime due to missing imports and a mismatched usage name, blocking metadata backfill automation.|High|Low|Direct|P0|Backfill runs reliably and matches documented usage.|
|S2|Scripts|generate_workflow_index.py misreads on:|YAML parser treats on: as boolean, so workflow triggers are misparsed and CI workflow index is inaccurate.|High|Low-Med|Direct|P0|CI workflow index becomes accurate and stable.|
|S3|V1 Scope|Auth requirement conflict|V1 scope says auth enabled while Backstage MVP allows auth disabled; V1 expectations are contradictory.|High|Low|Direct|P0|Single, coherent V1 auth stance and scope clarity.|
|S4|V1 Readiness|Readiness score mismatch|Health score claims ~95% V1 readiness while checklists/capability matrix show multiple unmet items.|High|Med|Direct|P0|Readiness signals align with gate artifacts and reality.|
|S5|Scripts|platform_health.py catalog assumptions|~~Script scans non-existent docs/catalogs~~ **RESOLVED**: Now scans `docs/20-contracts/resource-catalogs/` and `docs/20-contracts/secret-requests/`.|Med|Low|Direct|P1|Platform health metrics reflect actual catalogs.|
|S6|Scripts|ECR to Backstage generation split|Three scripts produce overlapping ECR entities with different outputs and paths; risk of drift.|Med|Med|Indirect|P1|Single source of truth for ECR entities and catalog output.|
|S7|Scripts|sync_ecr_catalog.py dry-run ignored|Script writes outputs even in dry-run and prints incorrect orphan data; safety expectation violated.|Med|Low|Indirect|P1|Dry-run becomes safe and reporting is correct.|
|S8|Scripts|check_compliance.py diverges from MetadataConfig|Legacy validator enforces hardcoded fields, ignoring inheritance/exempt rules used elsewhere.|Med|Med|Indirect|P2|Governance validators are consistent and predictable.|
|S9|Docs|Duplicate ADR-0120|Two ADR files share the same ID, confusing indexing and traceability.|Med|Low|Direct|P1|ADR index is unambiguous and automation-safe.|
|S10|Docs|Duplicate CI workflow index location|Two CI workflow index files exist, creating source-of-truth ambiguity.|Low|Low|Indirect|P2|One canonical workflow index with consistent references.|
|S11|V1 Scope|Build ID format ambiguity|Docs use dd-mm-yy-NN while roadmap suggests also YYYYMMDD-NN; spec is unclear.|Low|Low|Indirect|P2|Build ID contract is consistent and enforced.|

Notes:

- P0 items should be addressed before any new V1 scope work.
- P1 items remove drift and reduce operational ambiguity.
- P2 items are hygiene improvements that prevent future inconsistencies.
