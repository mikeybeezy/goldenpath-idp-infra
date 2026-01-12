---
id: HIW_DOC_AUTO_HEALING
title: 'How It Works: Documentation Auto-Healing'
type: documentation
relates_to:
  - scripts/platform_health.py
  - scripts/generate_adr_index.py
  - .github/workflows/ci-index-auto-heal.yml
---

# How It Works: Documentation Auto-Healing

This document explains how the platform ensures that documentation indices, relationship maps, and health dashboards never drift from the actual repository state.

## 0. The Auto-Healing Loop
The platform maintains "Queryable Intelligence" by automatically regenerating indices whenever files are added or moved.

```text
+---------------+       +-----------------------+
|   File Change | ----> |   GitHub Actions (CI) |
+---------------+       +-----------------------+
                                    |
                        ( 1. Run Index Generators )
                                    |
            +-----------------------+-------+-----------------------+
            |                               |                       |
+-----------------------+       +-----------------------+   +-----------------------+
|   ADR Index Update    |       |  Script Index Update  |   |  Workflow Index Update|
+-----------------------+       +-----------------------+   +-----------------------+
            |                               |                       |
            +-----------------------+-------+-----------------------+
                                    |
                        ( 2. Health Consolidation )
                                    |
                        +-----------------------+
                        |  PLATFORM_HEALTH.md   |
                        +-----------------------+
```

## 1. Index Generation
Instead of manual lists, the platform uses dedicated scripts (`generate_adr_index.py`, etc.) to scan the directory structure and frontmatter metadata.
- **Single Source of Truth**: Document metadata (Status, Owner, Version) is the source; indices are merely a "View" of that source.
- **Drift Detection**: CI runs these generators with a `--validate` flag. If a file is added but the index isn't updated, the PR is blocked.

## 2. Governance Commands
Developers can "Heal" their own branch locally using the governance CLI:
```bash
bin/governance heal indexes
```
This command runs all generator scripts in sequence, synchronizing the documentation with the new files.

## 3. The Health Command Center (`PLATFORM_HEALTH.md`)
The `platform_health.py` script aggregates all metadata into a single dashboard. 
- **Readiness Score**: Calculates a % score for V1 Production rollout.
- **Asset Inventory**: Counts ADRs, Scripts, and Workflows.
- **Risk Visibility**: Surfaces "Orphaned" files (no owner) or "Stale" files (past their lifecycle end-date).
