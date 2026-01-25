<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: RB-0007-tf-state-force-unlock
title: Terraform State Force Unlock (Runbook)
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
  maturity: 1
schema_version: 1
relates_to:
  - 32_TERRAFORM_STATE_AND_LOCKING
  - CI_WORKFLOWS
  - DOCS_RUNBOOKS_README
  - RB-0033-persistent-cluster-teardown
  - RB-0035-s3-request
supersedes: []
superseded_by: []
tags: []
inheritance: {}
status: active
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:terraform
  - module:dynamodb
breaking_change: false
---

# Terraform State Force Unlock (Runbook)

Use this only when a Terraform run left a stale lock and no other Terraform
jobs are active for the same state.

## Steps

1) Confirm no Terraform runs are active for the target environment/build.

2) Find the lock in DynamoDB (example for dev):

```bash
aws dynamodb scan \
  --table-name goldenpath-idp-dev-db-key \
  --filter-expression "contains(LockID, :id)" \
  --expression-attribute-values '{":id":{"S":"<build_id>"}}' \
  --region eu-west-2
```

3) Capture the `LockID` UUID from the `Info` field.

4) Run the **CI Force Unlock** workflow with:

- `env`
- `lifecycle`
- `build_id` (if ephemeral)
- `lock_id` (UUID)
- `confirm_unlock=true`

## Notes

- Force unlock is destructive; do not use while a Terraform run is active.
- If you cannot find a lock, the failure is not caused by DynamoDB locking.
