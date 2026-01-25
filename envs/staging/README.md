---
id: ENVS_STAGING_README
title: Staging Environment
type: documentation
relates_to:
  - DEV_ENV_README
  - PROD_ENV_README
version: '1.0'
dependencies:
  - MODULE_VPC
  - MODULE_AWS_EKS
  - MODULE_AWS_IAM
supported_until: 2028-01-01
breaking_change: false
---

# Staging Environment

This folder contains the Terraform stack for the staging environment.

## Common commands

```bash
terraform -chdir=envs/staging init
terraform -chdir=envs/staging plan
terraform -chdir=envs/staging apply
terraform -chdir=envs/staging destroy
```

## Set the cluster name once (best practice)

Set `cluster_name` in `envs/staging/terraform.tfvars` before the first build. On
future updates, Terraform will reuse it without prompting.

Optional helper (prompts only if missing):

```bash
make set-cluster-name ENV=staging
```

In CI, prefer environment variables:

```bash
TF_VAR_cluster_name=goldenpath-staging-eks
```

## Common toggles (CLI examples)

```bash
terraform -chdir=envs/staging apply \
  -var='bootstrap_mode=true' \
  -var='enable_ssh_break_glass=false' \
  -var='enable_storage_addons=true'
```

## Build ID mode (ephemeral vs persistent)

Ephemeral build (suffixes names/tags):

```bash
terraform -chdir=envs/staging plan \
  -var='cluster_lifecycle=ephemeral' \
  -var='build_id=20250115-01' \
  -var='owner_team=platform-team'
```

Persistent build (stable names):

```bash
terraform -chdir=envs/staging plan \
  -var='cluster_lifecycle=persistent'
```

## SSH break-glass example

```bash
terraform -chdir=envs/staging apply \
  -var='enable_ssh_break_glass=true' \
  -var='ssh_key_name=<your-keypair>' \
  -var='ssh_source_security_group_ids=["sg-abc123"]'
```

## Notes

- `terraform.tfvars` is the default place for staging values.
- You can also use `TF_VAR_*` env vars to avoid committing secrets.
