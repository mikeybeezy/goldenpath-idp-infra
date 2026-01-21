# Golden Path IDP - Quick Reference

A quick-access command reference for common operations.

---

## Table of Contents

1. [Cluster Discovery](#1-cluster-discovery)
2. [Ephemeral Cluster Lifecycle](#2-ephemeral-cluster-lifecycle)
3. [Persistent Cluster Lifecycle](#3-persistent-cluster-lifecycle)
4. [Cluster Access](#4-cluster-access)
5. [ArgoCD Access](#5-argocd-access)
6. [Troubleshooting](#6-troubleshooting)
7. [Kubernetes Operations](#7-kubernetes-operations)
8. [ECR Operations](#8-ecr-operations)
9. [Terraform State Management](#9-terraform-state-management)
10. [Parameter Reference](#10-parameter-reference)

---

## 1. Cluster Discovery

### List Clusters

```bash
aws eks list-clusters --region eu-west-2 --output table
```

### Find Instances by BuildId (Ephemeral)

```bash
aws ec2 describe-instances --region eu-west-2 \
  --filters "Name=tag:BuildId,Values=<build-id>"
```

### Resolve Cluster Name from tfvars

```bash
ENV=dev scripts/resolve-cluster-name.sh
```

### Naming Convention

| Type       | Pattern                           | Example                            |
|------------|-----------------------------------|------------------------------------|
| Ephemeral  | `goldenpath-dev-eks-<build-id>`   | `goldenpath-dev-eks-20-01-26-01`   |
| Persistent | `goldenpath-dev-eks`              | `goldenpath-dev-eks`               |

---

## 2. Ephemeral Cluster Lifecycle

### Phase 1: Infrastructure Build

Initialize Terraform (first time):

```bash
terraform -chdir=envs/dev init
```

Option A - Timed build (recommended):

```bash
make timed-apply ENV=dev BUILD_ID=<build-id>
```

Option B - With CI overrides:

```bash
TF_VAR_cluster_lifecycle=ephemeral \
TF_VAR_build_id=<build-id> \
TF_VAR_owner_team=platform-team \
make timed-apply ENV=dev
```

Option C - Direct terraform:

```bash
terraform -chdir=envs/dev apply
```

### Phase 2: Bootstrap

Standard:

```bash
make bootstrap ENV=dev BUILD_ID=<build-id>
```

Full options:

```bash
make bootstrap ENV=dev BUILD_ID=<build-id> \
  ENV_NAME=dev \
  NODE_INSTANCE_TYPE=t3.small \
  SKIP_ARGO_SYNC_WAIT=true \
  SKIP_CERT_MANAGER_VALIDATION=true \
  COMPACT_OUTPUT=false \
  ENABLE_TF_K8S_RESOURCES=true \
  SCALE_DOWN_AFTER_BOOTSTRAP=false \
  TF_DIR=envs/dev \
  CLUSTER=goldenpath-dev-eks-<build-id> \
  REGION=eu-west-2
```

### Phase 3: Teardown

Timed (recommended):

```bash
TF_DIR=envs/dev \
make timed-teardown ENV=dev BUILD_ID=<build-id> \
  CLUSTER=goldenpath-dev-eks-<build-id> \
  REGION=eu-west-2
```

Non-timed:

```bash
make teardown ENV=dev BUILD_ID=<build-id> \
  CLUSTER=goldenpath-dev-eks-<build-id> \
  REGION=eu-west-2 \
  TF_DIR=envs/dev
```

---

## 3. Persistent Cluster Lifecycle

### Deploy (Seamless)

```bash
make deploy-persistent ENV=dev
```

This runs: apply-persistent + rds-deploy + bootstrap-persistent + verify

To skip RDS creation:

```bash
make deploy-persistent ENV=dev CREATE_RDS=false
```

### Persistent RDS (Standalone State)

Platform RDS can be managed in its own Terraform state (`envs/<env>-rds/`).
This keeps RDS intact when the cluster is torn down.

```bash
make rds-init ENV=dev
make rds-plan ENV=dev
make rds-apply ENV=dev
make rds-provision-auto ENV=dev
```

Single-command wrapper:

```bash
make rds-deploy ENV=dev
```

Skip the secrets preflight (restore + adopt):

```bash
make rds-deploy ENV=dev RESTORE_SECRETS=false
```

Disable RDS deletion protection (break-glass):

```bash
make rds-allow-delete ENV=dev CONFIRM_RDS_DELETE=yes
```

Break-glass destroy (confirmation-gated):

```bash
make rds-destroy-break-glass ENV=dev CONFIRM_DESTROY_DATABASE_PERMANENTLY=YES
```

Important:
- If `rds_config.enabled=true` in `envs/<env>/terraform.tfvars`, RDS is coupled to the
  cluster state and **will** be destroyed by `terraform destroy`, regardless of safety flags.
- To preserve RDS across cluster rebuilds, set `rds_config.enabled=false` and use
  `envs/<env>-rds/` for RDS instead.
- There is no standard `rds-destroy` target; use `rds-destroy-break-glass` (see `docs/70-operations/runbooks/RB-0030-rds-break-glass-deletion.md`).

### Teardown

Persistent clusters use name patterns instead of BuildId tags.

Via teardown script (v4):

```bash
TEARDOWN_CONFIRM=true \
TF_DIR=envs/dev \
TF_AUTO_APPROVE=true \
SECRETS_NAME_PATTERN="goldenpath/dev/" \
bash bootstrap/60_tear_down_clean_up/goldenpath-idp-teardown-v4.sh \
  goldenpath-dev-eks eu-west-2
```

Via Makefile:

```bash
make teardown ENV=dev CLUSTER=goldenpath-dev-eks REGION=eu-west-2 TEARDOWN_VERSION=v4
```

Note: If RDS is coupled in `envs/<env>` (via `rds_config.enabled=true`), it will be
destroyed with the cluster. Safety flags only affect extra cleanup steps, not the
core Terraform destroy.

### Ephemeral vs Persistent Comparison

| Attribute       | Ephemeral                      | Persistent                        |
|-----------------|--------------------------------|-----------------------------------|
| BUILD_ID        | `20-01-26-01` (timestamped)    | `persistent`                      |
| Cluster name    | `...-<build-id>` suffix        | No suffix                         |
| Secrets cleanup | BuildId tag                    | Name pattern                      |
| RDS cleanup     | BuildId tag                    | ClusterName tag / name pattern    |
| Teardown method | By BuildId                     | By name pattern                   |
| RDS state       | Coupled or standalone          | Prefer standalone (`envs/<env>-rds`) |

---

## 4. Cluster Access

### Grant Admin Access (after bootstrap or restore)

Step 1 - List clusters:

```bash
aws eks list-clusters --region eu-west-2 --output table
```

Step 2 - Create access entry:

```bash
aws eks create-access-entry \
  --cluster-name <cluster-name> \
  --principal-arn "arn:aws:iam::<account-id>:user/<username>" \
  --region eu-west-2
```

Step 3 - Associate admin policy:

```bash
aws eks associate-access-policy \
  --cluster-name <cluster-name> \
  --principal-arn "arn:aws:iam::<account-id>:user/<username>" \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
  --access-scope type=cluster \
  --region eu-west-2
```

Step 4 - Update kubeconfig:

```bash
aws eks update-kubeconfig --name <cluster-name> --region eu-west-2
```

Step 5 - Verify:

```bash
kubectl get ns
kubectl get pods -A
```

---

## 5. ArgoCD Access

### Get Initial Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

---

## 6. Troubleshooting

### Terraform State Lock

Use CI Workflow: Force Unlock

| Input           | Value           |
|-----------------|-----------------|
| env             | dev             |
| lifecycle       | ephemeral       |
| build_id        | `<build-id>`    |
| lock_id         | `<uuid>`        |
| confirm_unlock  | true            |

### LB/VPC Cleanup Blocked

Use CI Workflow: Managed LB Cleanup

| Input                      | Value           |
|----------------------------|-----------------|
| env                        | dev             |
| lifecycle                  | ephemeral       |
| build_id                   | `<build-id>`    |
| dry_run                    | false           |
| delete_cluster_tagged_sgs  | true            |

### Restart Backstage

```bash
kubectl rollout restart deployment/backstage -n backstage
```

---

## 7. Kubernetes Operations

### Create Backstage Namespace with CNPG Database

```bash
kubectl apply -f - << 'EOF'
---
apiVersion: v1
kind: Namespace
metadata:
  name: backstage
---
apiVersion: v1
kind: Secret
type: kubernetes.io/basic-auth
metadata:
  name: app-secret
  namespace: backstage
data:
  username: YXBw
  password: cGFzc3dvcmQ=
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: backstage
  namespace: backstage
spec:
  instances: 1
  primaryUpdateStrategy: unsupervised
  storage:
    size: 1Gi
  bootstrap:
    initdb:
      secret:
        name: app-secret
      postInitSQL:
        - ALTER ROLE app CREATEDB
EOF
```

---

## 8. ECR Operations

### Create Repository

```bash
aws ecr create-repository \
  --repository-name <repo-name> \
  --region eu-west-2 \
  --encryption-configuration encryptionType=AES256 \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE
```

---

## 9. Terraform State Management

### Initialize with New Backend Key

For fresh builds with separate state:

```bash
terraform -chdir=envs/dev init \
  -reconfigure \
  -backend-config="bucket=goldenpath-idp-dev-bucket" \
  -backend-config="key=envs/dev/<build-id>/terraform.tfstate" \
  -backend-config="region=eu-west-2" \
  -backend-config="dynamodb_table=goldenpath-idp-dev-locks"
```

Then deploy:

```bash
make deploy ENV=dev BUILD_ID=<build-id>
```

---

## 10. Parameter Reference

### Bootstrap Parameters

| Parameter                      | Default      | Description                              |
|--------------------------------|--------------|------------------------------------------|
| `ENV_NAME`                     | dev          | Environment name for Argo app files      |
| `NODE_INSTANCE_TYPE`           | -            | Required for preflight capacity checks   |
| `SKIP_ARGO_SYNC_WAIT`          | true         | Skip waiting for autoscaler app sync     |
| `SKIP_CERT_MANAGER_VALIDATION` | true         | Skip cert-manager validation             |
| `COMPACT_OUTPUT`               | false        | Suppress command output                  |
| `ENABLE_TF_K8S_RESOURCES`      | true         | Run Terraform for service accounts       |
| `SCALE_DOWN_AFTER_BOOTSTRAP`   | false        | Re-apply TF with bootstrap_mode=false    |
| `TF_DIR`                       | -            | Terraform directory (required for TF ops)|
| `CLUSTER`                      | from tfvars  | Cluster name                             |
| `REGION`                       | from tfvars  | AWS region                               |

### Teardown Parameters (v4)

| Parameter                | Default              | Description                              |
|--------------------------|----------------------|------------------------------------------|
| `TEARDOWN_CONFIRM`       | false                | Must be `true` to run                    |
| `TF_DIR`                 | -                    | Terraform directory                      |
| `TF_AUTO_APPROVE`        | false                | Auto-approve terraform destroy           |
| `SECRETS_NAME_PATTERN`   | `goldenpath/<env>/`  | Pattern for persistent secrets cleanup   |
| `DELETE_RDS_INSTANCES`   | true                 | Delete RDS instances                     |
| `RDS_SKIP_FINAL_SNAPSHOT`| true                 | Skip final snapshot (ephemeral)          |

---

Last updated: 2026-01-20


Fixed. The correct commands are:

Cluster Type	Deploy Command
```
Persistent	make deploy-persistent ENV=dev
Ephemeral	make deploy ENV=dev BUILD_ID=20-01-26-01
```
