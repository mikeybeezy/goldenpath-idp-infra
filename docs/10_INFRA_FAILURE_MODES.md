# Infra Failure Modes and Recovery

This document captures common infrastructure build failures, how we recover,
and the options we considered.

## Common failure modes

- IAM role collisions (`EntityAlreadyExists`) from previous builds.
- EKS node groups failing to join (no NAT for private subnets).
- Orphaned load balancers/ENIs preventing VPC teardown.
- Terraform state drift (resources created outside the current state).

## Chosen approach (V1)

1) Require a unique `name_prefix` per build (CLI-driven).
2) Tag all resources with a unique `BuildId`.
3) Use a cleanup script to delete orphaned resources by `BuildId`.

This combination avoids name collisions, makes cleanup deterministic, and
reduces manual imports.

## Operational flow when a build fails

1) Stop the failed apply.
2) Run the cleanup script for that `BuildId` (dry-run first).
3) Re-run `terraform apply` with a new `BuildId` if needed.
4) Import resources only if you intend to keep them.

## Automation note

We do not auto-run cleanup on failure because it can break Terraform
idempotency. If you want automation, wire `cleanup-orphans.sh` behind an
explicit flag in CI (e.g., only when you intend to abandon a build).

Cleanup script:

```
bootstrap-scripts/cleanup-orphans.sh <build-id> <region>
```

Set `DRY_RUN=false` to execute deletions.

## Example CLI invocation (recommended)

```
TF_VAR_name_prefix=goldenpath-dev-20240115-abc123 \
TF_VAR_build_id=dev-20240115-abc123 \
terraform -chdir=envs/dev apply
```

## BuildId format (recommended)

Use a consistent BuildId format so cleanup is predictable:

- `<env>-<YYYYMMDD>-<shortid>` (example: `dev-20240115-abc123`)
- `name_prefix` should include the same suffix to avoid collisions.

## Other options we can adopt later

- Separate AWS accounts per environment (best isolation, higher overhead).
- Workspace-per-build for state isolation (does not prevent name collisions).
- Random suffixes for all names (prevents collisions, harder to read).
- Scheduled sweeper job to purge expired BuildIds.
