---
id: 17_BUILD_RUN_FLAGS
title: Build/Bootstrap/Teardown Flags (One‑Pager)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 04_REPO_STRUCTURE
  - 12_GITOPS_AND_CICD
  - 16_INFRA_Build_ID_Strategy_Decision
  - ADR-0051-platform-reliability-metrics-contract-minimums
  - BOOTSTRAP_10_BOOTSTRAP_README
  - BOOTSTRAP_README
  - TEARDOWN_README
category: delivery
supported_until: 2028-01-01
version: 1.0
dependencies:
  - module:terraform
  - module:kubernetes
breaking_change: false
---

# Build/Bootstrap/Teardown Flags (One‑Pager)

This page lists the runtime flags we use to drive automation. It is grouped by
phase so CI and operators can see what is available at a glance.

## Terraform build inputs (apply/destroy)

These are passed to `terraform apply` or `terraform destroy`.

- `cluster_lifecycle` – `ephemeral` or `persistent`
- `build_id` – build identifier for ephemeral runs
- `owner_team` – owning team tag (e.g., `platform-team`)

If you do not pass these on the CLI, Terraform will read them from
`envs/<env>/terraform.tfvars`. For ephemeral runs, `build_id` must be set.

Example:

```bash
terraform -chdir=envs/dev apply \
  -var='cluster_lifecycle=ephemeral' \
  -var='build_id=20250115-02' \
  -var='owner_team=platform-team'

```

## Timing helpers (Makefile)

These targets stream to the terminal, log full output to `logs/build-timings/*.log`,
and append a row to `docs/build-timings.csv`.

- `make timed-apply ENV=dev BUILD_ID=20250115-02`
- `make build ENV=dev CLUSTER=... REGION=...`
- `make timed-build ENV=dev BUILD_ID=20250115-02 CLUSTER=... REGION=...`
- `make timed-bootstrap ENV=dev BUILD_ID=20250115-02 CLUSTER=... REGION=...`
- `make timed-teardown ENV=dev BUILD_ID=20250115-02 CLUSTER=... REGION=...`

`BUILD_ID` is required for timed targets. If you omit it, the Makefile will
read `build_id` from `envs/<env>/terraform.tfvars` and fail if it is empty.

Use `make reliability-metrics` to summarize build/teardown counts and durations
from `docs/build-timings.csv`.

Output logs are written to `logs/build-timings/*.log` and include the cluster
name in the filename. The non‑timed `make apply`, `make bootstrap`, and
`make teardown` targets also stream and write logs, but they do not add CSV rows.

Use `make build`/`make timed-build` when you want Terraform apply and the
bootstrap runner in a single step.

Use `make bootstrap-only` when you want the runner without Terraform apply.

## Bootstrap runner (goldenpath-idp-bootstrap.sh)

- `ENV_NAME` – env key used by Argo apps (e.g., `dev`)
- `NODE_INSTANCE_TYPE` – instance type for preflight capacity checks
- `MIN_READY_NODES` – minimum Ready nodes required (default: 3)
- `SKIP_ARGO_SYNC_WAIT` – do not wait for Argo apps to sync
- `SKIP_CERT_MANAGER_VALIDATION` – skip cert‑manager rollout check
- `COMPACT_OUTPUT` – reduce output noise
- `ENABLE_TF_K8S_RESOURCES` – run the targeted Terraform K8s service-account apply
- `CONFIRM_TF_APPLY` – set `true` to skip the interactive confirmation prompt for the IRSA apply
- `SCALE_DOWN_AFTER_BOOTSTRAP` – scale nodegroup down after bootstrap
- `TF_DIR` – when set, the runner reads `cluster_name` and `region` from

  `TF_DIR/terraform.tfvars` if positional args are omitted

- `TF_AUTO_APPROVE` – when `true`, pass `-auto-approve` during the optional

  scale-down Terraform apply

Helper:

- `scripts/resolve-cluster-name.sh` prints the effective cluster name that

  Terraform will use (adds `-<build_id>` for ephemeral runs).
  It honors `BUILD_ID` and `CLUSTER_LIFECYCLE` env overrides if set.

Example:

```bash
SKIP_ARGO_SYNC_WAIT=false \
NODE_INSTANCE_TYPE=t3.small \
ENV_NAME=dev \
SKIP_CERT_MANAGER_VALIDATION=true \
COMPACT_OUTPUT=false \
ENABLE_TF_K8S_RESOURCES=true \
SCALE_DOWN_AFTER_BOOTSTRAP=false \
bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh goldenpath-dev-eks-20250115-02 eu-west-2

```

TF_DIR-only usage (omit positional args):

```bash
TF_DIR=envs/dev \
NODE_INSTANCE_TYPE=t3.small \
ENABLE_TF_K8S_RESOURCES=true \
bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh

```

Resolve the effective cluster name:

```bash
ENV=dev scripts/resolve-cluster-name.sh

```

Recommendation:

- Default `SCALE_DOWN_AFTER_BOOTSTRAP=false` so bootstrap can finish syncing

  platform apps before you reduce capacity. Scale down only after confirming
  pods are stable and observability checks are green.

## Teardown runner (goldenpath-idp-teardown.sh)

Safety + flow:

- `TEARDOWN_VERSION` – select teardown runner (`v5` default, `v4|v3|v2|v1` optional)
- `TEARDOWN_CONFIRM` – must be `true` to run destructive steps
- `TF_DIR` – run `terraform destroy` instead of `aws eks delete-cluster`
- `REQUIRE_KUBE_FOR_TF_DESTROY` – require kube access before Terraform destroy
- `REMOVE_K8S_SA_FROM_STATE` – remove k8s service accounts from state before

  Terraform destroy (default `true`)

- `TF_DESTROY_FALLBACK_AWS` – fall back to AWS deletion if Terraform fails
- `TF_AUTO_APPROVE` – pass `-auto-approve` to Terraform destroy (Makefile

  teardown targets set this to `true`)

Drain + heartbeat:

- `RELAX_PDB` – relax CoreDNS PDB if drain is blocked
- `DRAIN_TIMEOUT` – drain timeout (default `300s`)
- `HEARTBEAT_INTERVAL` – progress heartbeat cadence (default `30`)

Load balancer cleanup:

- `LB_CLEANUP_ATTEMPTS` – retry loops for LB Service deletion (default `5`)
- `LB_CLEANUP_INTERVAL` – delay between retries (default `20`)
- `KUBECTL_REQUEST_TIMEOUT` – request timeout for kubectl LB cleanup calls (default `10s`)
- `LB_CLEANUP_MAX_WAIT` – max wait for LB Services to disappear (default `900`)

Argo CD application cleanup:

- `DELETE_ARGO_APP` – delete Argo Application before LB cleanup (default `true`)
- `ARGO_APP_NAMESPACE` – Argo Application namespace (default `kong-system`)
- `ARGO_APP_NAME` – Argo Application name (default `dev-kong`)

Optional cleanup:

- `CLEANUP_ORPHANS` – run tag‑based orphan cleanup
- `ORPHAN_CLEANUP_MODE` – `delete`, `dry_run`, or `none` (default `delete`)
- `BUILD_ID` – required when `CLEANUP_ORPHANS=true`

Example:

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s HEARTBEAT_INTERVAL=30 \
  TF_DIR=envs/dev REQUIRE_KUBE_FOR_TF_DESTROY=true REMOVE_K8S_SA_FROM_STATE=true \
  TF_DESTROY_FALLBACK_AWS=false CLEANUP_ORPHANS=true ORPHAN_CLEANUP_MODE=delete BUILD_ID=20250115-02 \
  bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh goldenpath-dev-eks-20250115-02 eu-west-2

```
