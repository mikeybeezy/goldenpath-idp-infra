---
id: PLATFORM_PR_GATES_FIX
title: PLATFORM_PR_GATES_FIX
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
relates_to: []
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

Analysie the PR Blocakage issues and provide a diagnosis.
Do not attempt to resolve.

Sripts to run.

Local pre-commit checks have been

Run document auto heal

Run Yaml lint and formatting

markdownlint-cli2 not found. Install it for full CI parity.

Sync Indices: Run bin/governance heal . locally one last time to synchronize the workflow and script indices.
Strict Commit: Use git commit -am "chore(hygiene): final index and annotation sync".
Validate Locally: Run python3 -m pre_commit run --all-files locally and ensure it returns 100% Passed.
Final Push: Once local is 100% green, push. Since our new scripts are now idempotent, the CI will find the files exactly as it expects them.
