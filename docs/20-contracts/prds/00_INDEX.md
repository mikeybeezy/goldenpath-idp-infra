<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: 00_INDEX
title: PRD Index
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - DOCS_USER-STORIES_README
  - PRD-0000-template
  - PRD-0001-rds-user-db-provisioning
  - PRD-0002-route53-externaldns
  - PRD-0003-backstage-plugin-scaffold
  - PRD-0004-backstage-repo-structure-alignment
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD Index

| ID | Title | Status | Date | Related |
| --- | --- | --- | --- | --- |
| PRD-0000 | Template | template | 2026-01-16 | docs/20-contracts/prds/PRD-0000-template.md |
| PRD-0001 | Automated RDS user and database provisioning | draft | 2026-01-16 | docs/20-contracts/prds/PRD-0001-rds-user-db-provisioning.md |
| PRD-0002 | Route53 + ExternalDNS management | draft | 2026-01-20 | docs/20-contracts/prds/PRD-0002-route53-externaldns.md |
| PRD-0003 | Backstage Plugin Scaffold (Vanilla Template) | draft | 2026-01-21 | docs/20-contracts/prds/PRD-0003-backstage-plugin-scaffold.md |
| PRD-0004 | Backstage Repo Structure Alignment (Spotify-style) | draft | 2026-01-22 | docs/20-contracts/prds/PRD-0004-backstage-repo-structure-alignment.md |
