---
id: BR-TEMPLATE
title: Build Run Log Template
type: template
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
lifecycle: active
category: platform
version: '1.0'
dependencies: []
relates_to:
  - TD-TEMPLATE
supported_until: 2028-01-01
breaking_change: false
---

# BR-XXXX-<build-id>

Date (UTC): YYYY-MM-DD
Build ID: <build-id>
Branch/Commit: <branch> @ <sha>
Workflow: <workflow-name>
Jobs: <job-list>
Workflow run URL (build): <url>
Workflow run URL (bootstrap): <url>

## Configuration

Scripts: bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
TF Flags: <flags>
Bootstrap Flags: <flags>
Config source: <config-source>
Storage add-ons: <storage-addons>
IRSA strategy: <irsa-strategy>

## Metrics

Plan Delta: <plan-delta>
Build duration (seconds): <build-seconds>
Bootstrap duration (seconds): <bootstrap-seconds>
Teardown duration (seconds): <teardown-seconds>

## Outcome

Outcome: <Success/Failure>
Artifacts: <artifacts>
Ad hoc notes/observations: <notes>
