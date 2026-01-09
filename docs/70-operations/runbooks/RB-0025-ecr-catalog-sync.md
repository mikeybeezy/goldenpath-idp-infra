---
id: RB-0025-ecr-catalog-sync
title: ECR Catalog Sync (AWS Source of Truth)
type: runbook
domain: delivery
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0128-automated-ecr-catalog-sync
  - ADR-0129-platform-eventual-consistency-ecr-governance
supersedes: []
superseded_by: []
tags: [ecr, catalog, backstage, sync]
inheritance: {}
value_quantification:
  vq_class: 🟡 MV/HQ
  impact_tier: medium
  potential_savings_hours: 1.0
category: runbooks
status: active
version: '1.0'
dependencies: [aws, python3]
supported_until: 2028-01-01
breaking_change: false
---

# ECR Catalog Sync (AWS Source of Truth)

This runbook keeps Backstage aligned to the physical AWS ECR state by generating
`backstage-helm/catalog/resources/ecr-registry.yaml` from AWS. The catalog file
`docs/20-contracts/catalogs/ecr-catalog.yaml` is used only for optional metadata
enrichment (e.g., environment), not as the source of truth.

Use this when:

- Backstage shows the wrong number of ECR repositories.
- A new registry exists in AWS but is missing in Backstage.
- A registry was removed in AWS but still appears in Backstage.

## Prerequisites

- AWS CLI configured with credentials.
- Region is set via `AWS_REGION` or `AWS_DEFAULT_REGION`, or passed with
  `--region`.
- `python3` available.

## Why the Region Must Be Set

ECR is regional. The sync script relies on AWS CLI context to know which region
to query. To keep the script portable across regions, we avoid hardcoding a
region in the script and instead supply it at runtime.

Portable region options (preferred):

- Environment variables (shell or CI):
  - `AWS_REGION=eu-west-2`
  - `AWS_DEFAULT_REGION=eu-west-2`
- CLI parameter:
  - `--region eu-west-2`
- AWS config profile (default region in `~/.aws/config`)

## Procedure

## Automation (post-merge)

This sync runs automatically after an ECR registry PR merges and the apply
workflow completes successfully. The automation opens a PR with the updated
Backstage registry entity for human review.

Workflow: `.github/workflows/ecr-backstage-sync.yml`

Manual runs are still supported for debugging or recovery.

1. Ensure region and credentials are set.

   ```bash
   export AWS_REGION=eu-west-2
   export AWS_PROFILE=platform-dev
   ```

2. Run the sync script.

   ```bash
   python3 scripts/sync_ecr_catalog.py --region "$AWS_REGION"
   ```

3. Verify the generated Backstage entity.

   ```bash
   rg -n "Master AWS ECR Registry" backstage-helm/catalog/resources/ecr-registry.yaml
   ```

4. Commit the updated Backstage entity file when the output is correct.

## Expected Output

- The Backstage resource lists the same repository count as AWS.
- `platform/repo-count` matches the physical AWS count.
- `platform/last-sync` updates to the current timestamp.

## Troubleshooting

### "Could not connect to the endpoint URL"

- Confirm `AWS_REGION` is set.
- Confirm network access to the regional ECR endpoint.
- Try running with `--region` explicitly.

### "AccessDeniedException"

- Ensure the AWS principal has `ecr:DescribeRepositories`.
- Confirm the correct AWS profile is active.

## Notes

- The script is single-region per run. For multi-region reporting, run once per
  region and merge or extend the script with region-aware output files.
