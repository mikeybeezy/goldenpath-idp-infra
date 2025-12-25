# Build/Bootstrap/Teardown Flags (One‑Pager)

This page lists the runtime flags we use to drive automation. It is grouped by
phase so CI and operators can see what is available at a glance.

## Terraform build inputs (apply/destroy)

These are passed to `terraform apply` or `terraform destroy`.

- `cluster_lifecycle` – `ephemeral` or `persistent`
- `build_id` – build identifier for ephemeral runs
- `owner_team` – owning team tag (e.g., `platform-team`)

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
- `make timed-bootstrap ENV=dev BUILD_ID=20250115-02 CLUSTER=... REGION=...`
- `make timed-teardown ENV=dev BUILD_ID=20250115-02 CLUSTER=... REGION=...`

Output logs are written to `logs/build-timings/*.log` and include the cluster
name in the filename. The non‑timed `make apply`, `make bootstrap`, and
`make teardown` targets also stream and write logs, but they do not add CSV rows.

## Bootstrap runner (goldenpath-idp-bootstrap.sh)

- `ENV_NAME` – env key used by Argo apps (e.g., `dev`)
- `NODE_INSTANCE_TYPE` – instance type for preflight capacity checks
- `SKIP_ARGO_SYNC_WAIT` – do not wait for Argo apps to sync
- `SKIP_CERT_MANAGER_VALIDATION` – skip cert‑manager rollout check
- `COMPACT_OUTPUT` – reduce output noise
- `ENABLE_TF_K8S_RESOURCES` – run the Terraform K8s resources phase
- `SCALE_DOWN_AFTER_BOOTSTRAP` – scale nodegroup down after bootstrap

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

## Teardown runner (goldenpath-idp-teardown.sh)

Safety + flow:

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

Optional cleanup:

- `CLEANUP_ORPHANS` – run tag‑based orphan cleanup
- `BUILD_ID` – required when `CLEANUP_ORPHANS=true`

Example:

```bash
TEARDOWN_CONFIRM=true RELAX_PDB=true DRAIN_TIMEOUT=300s HEARTBEAT_INTERVAL=30 \
  TF_DIR=envs/dev REQUIRE_KUBE_FOR_TF_DESTROY=true REMOVE_K8S_SA_FROM_STATE=true \
  TF_DESTROY_FALLBACK_AWS=false CLEANUP_ORPHANS=true BUILD_ID=20250115-02 \
  bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown.sh goldenpath-dev-eks-20250115-02 eu-west-2
```
