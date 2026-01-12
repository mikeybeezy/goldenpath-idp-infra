---
id: PLATFORM_PR_GATES_FIX
title: 'Handled automatically by pre-commit, or run manually:'
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

# Handled automatically by pre-commit, or run manually:
python3 scripts/generate_script_index.py
python3 scripts/generate_workflow_index.py

Run the pre-commit suite locally to catch errors before they hit CI.
python3 -m pre_commit run --all-files

4. Push with Confidence
git add .
git commit -m "feat: my change"
git push origin <branch>

4. Push with Confidence
git add .
git commit -m "feat: my change"
git push origin <branch>
