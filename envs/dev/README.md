<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: ENVS_DEV_README
title: Dev Environment
type: documentation
relates_to:
  - STAGING_ENV_README
  - PROD_ENV_README
version: 1.0
dependencies:
  - MODULE_VPC
  - MODULE_AWS_EKS
  - MODULE_AWS_IAM
supported_until: 2028-01-01
breaking_change: false
---

# Dev Environment

This folder contains the Terraform stack for the dev environment.

## Common commands

```bash
terraform -chdir=envs/dev init
terraform -chdir=envs/dev plan
terraform -chdir=envs/dev apply
terraform -chdir=envs/dev destroy
```

## Set the cluster name once (best practice)

Set `cluster_name` in `envs/dev/terraform.tfvars` before the first build. On
future updates, Terraform will reuse it without prompting.

Optional helper (prompts only if missing):

```bash
make set-cluster-name ENV=dev
```

In CI, prefer environment variables:

```bash
TF_VAR_cluster_name=goldenpath-dev-eks
```

## Common toggles (CLI examples)

```bash
terraform -chdir=envs/dev apply \
  -var='bootstrap_mode=true' \
  -var='enable_ssh_break_glass=false' \
  -var='enable_storage_addons=true'
```

## Build ID mode (ephemeral vs persistent)

Ephemeral build (suffixes names/tags):

```bash
terraform -chdir=envs/dev plan \
  -var='cluster_lifecycle=ephemeral' \
  -var='build_id=20250115-01' \
  -var='owner_team=platform-team'
```

Persistent build (stable names):

```bash
terraform -chdir=envs/dev plan \
  -var='cluster_lifecycle=persistent'
```

## Backend init examples (S3 + DynamoDB)

Ephemeral build (state per Build ID):

```bash
terraform -chdir=envs/dev init \
  -reconfigure \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/builds/<build_id>/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-locks"
```

Persistent build (shared state):

```bash
terraform -chdir=envs/dev init \
  -reconfigure \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-locks"
```

## SSH break-glass example

```bash
terraform -chdir=envs/dev apply \
  -var='enable_ssh_break_glass=true' \
  -var='ssh_key_name=mikeybeezy' \
  -var='ssh_source_security_group_ids=["sg-abc123"]'
```

## Notes

- `terraform.tfvars` is the default place for dev values.
- You can also use `TF_VAR_*` env vars to avoid committing secrets.
