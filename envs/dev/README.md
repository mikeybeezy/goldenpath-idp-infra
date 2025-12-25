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
  -var='enable_storage_addons=false'
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
