---
id: CL-0108
title: Governance Stability and Automated Remediation
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to: []
lifecycle: active
exempt: false
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: none
schema_version: 1
relates_to:
  - ADR-0014
  - CL-0107
supersedes: []
superseded_by: []
tags:
  - governance
  - automation
  - ci
  - yaml
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 1.0
supported_until: '2028-01-01'
---
# CL-0108: Governance Stability and Automated Remediation

## Summary
Established a permanent resolution for CI "dialect" mismatches and index drift errors. By centralizing YAML formatting and empowering CI to self-correct, we have removed the friction between local automation and remote enforcement gates.

## Details
- **Centralized PlatformYamlDumper**: Introduced a unified YAML dumper in `scripts/lib/metadata_config.py`. This ensures high-fidelity, consistent YAML output across all 20+ platform scripts, matching the exact requirements of `yamllint`.
- **Pre-commit Index Healing**: Integrated ADR, Script, and Workflow index generation directly into the local `pre-commit` workflow. This prevents "Index Drift" from ever reaching the remote repository.
- **Self-Healing CI Pipeline**: Upgraded the `Quality - Documentation Auto-Healing` workflow. The pipeline now automatically commits and pushes index corrections back to PR branches, eliminating the need for manual developer intervention.
- **Technical Debt Reduction**: Removed redundant `IndentDumper` logic from 6 core scripts (`standardize_metadata.py`, `scaffold_doc.py`, `sync_ecr_catalog.py`, etc.) in favor of the central platform utility.
- **Workflow Optimization**: Aligned automated indexing with the modernized `stages: [pre-commit]` syntax.

## Related
- ADR-0014: Platform CI Local Preflight Checks
- CL-0107: Hygiene Dialect Alignment
- bin/governance
