---
id: RB-0003-iam-audit
title: IAM Audit (Runbook)
type: runbook
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: medium
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
  maturity: 1
relates_to:
  - 33_IAM_ROLES_AND_POLICIES
  - ADR-0035-platform-iam-audit-cadence
  - DOCS_RUNBOOKS_README
category: runbooks
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---
# IAM Audit (Runbook)

This runbook captures how to audit IAM usage for CI roles and reduce unused
permissions over time.

Use this when:

- CI has stabilized and you want to tighten role permissions.
- You need evidence of which actions were actually used.

## Inputs

- Role ARN(s) to audit
- Time window (e.g., last 7/30/90 days)

## Step 1: CloudTrail (exact actions used)

Why: CloudTrail is the source of truth for AWS API calls.

Example CLI query (last 90 days):

```sh
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=<ROLE_NAME> \
  --start-time <START_TIME> \
  --end-time <END_TIME> \
  --query 'Events[].{Time:EventTime,Name:EventName,Service:EventSource}' \
  --output table
```

## Step 2: IAM Access Analyzer (service last accessed)

Why: Quickly see which services a role has actually used.

```sh
aws iam generate-service-last-accessed-details \
  --arn <ROLE_ARN>

aws iam get-service-last-accessed-details \
  --job-id <JOB_ID>
```

## Step 3: Optional Athena query (if CloudTrail logs in S3)

Why: Faster aggregation and reporting at scale.

Example pattern (replace dataset/table names):

```sql
SELECT eventSource, eventName, count(*) AS calls
FROM cloudtrail_logs
WHERE userIdentity.sessionContext.sessionIssuer.arn = '<ROLE_ARN>'
  AND eventTime BETWEEN timestamp '<START_TIME>' AND timestamp '<END_TIME>'
GROUP BY eventSource, eventName
ORDER BY calls DESC;
```

## Step 4: Tighten IAM policy

Why: Remove unused actions while keeping required permissions.

- Remove actions not seen in CloudTrail or Access Analyzer.
- Keep a small buffer for near-term changes if needed.

## Output

- A PR that removes unused IAM actions.
- A short summary of actions removed and evidence links.

## Related docs

- `docs/60-security/33_IAM_ROLES_AND_POLICIES.md`
- `docs/adrs/ADR-0035-platform-iam-audit-cadence.md`
