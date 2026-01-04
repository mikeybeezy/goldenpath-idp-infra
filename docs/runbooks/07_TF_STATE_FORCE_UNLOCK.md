---
id: 07_TF_STATE_FORCE_UNLOCK
title: Terraform State Force Unlock (Runbook)
type: runbook
owner: platform-team
status: active
risk_profile:
  production_impact: medium
  security_risk: access
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
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
