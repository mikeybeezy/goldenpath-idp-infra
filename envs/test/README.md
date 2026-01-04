---
id: README
title: Test Environment
type: documentation
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: []
---

# Test Environment

This folder contains the Terraform stack for the test environment.

## Common commands

```bash
terraform -chdir=envs/test init
terraform -chdir=envs/test plan
terraform -chdir=envs/test apply
terraform -chdir=envs/test destroy
```

## Set the cluster name once (best practice)

Set `cluster_name` in `envs/test/terraform.tfvars` before the first build. On
future updates, Terraform will reuse it without prompting.

Optional helper (prompts only if missing):

```bash
make set-cluster-name ENV=test
```

In CI, prefer environment variables:

```bash
TF_VAR_cluster_name=goldenpath-test-eks
```

## Common toggles (CLI examples)

```bash
terraform -chdir=envs/test apply \
  -var='bootstrap_mode=true' \
  -var='enable_ssh_break_glass=false' \
  -var='enable_storage_addons=true'
```

## Build ID mode (ephemeral vs persistent)

Ephemeral build (suffixes names/tags):

```bash
terraform -chdir=envs/test plan \
  -var='cluster_lifecycle=ephemeral' \
  -var='build_id=20250115-01' \
  -var='owner_team=platform-team'
```

Persistent build (stable names):

```bash
terraform -chdir=envs/test plan \
  -var='cluster_lifecycle=persistent'
```

## SSH break-glass example

```bash
terraform -chdir=envs/test apply \
  -var='enable_ssh_break_glass=true' \
  -var='ssh_key_name=<your-keypair>' \
  -var='ssh_source_security_group_ids=["sg-abc123"]'
```

## Notes

- `terraform.tfvars` is the default place for test values.
- You can also use `TF_VAR_*` env vars to avoid committing secrets.
