---
id: RB-0026
title: Local Secret Generation & Targeting
type: runbook
status: active
version: "1.0"
relates_to:
  - how-it-works/SECRET_REQUEST_FLOW.md
  - ADR-0144-intent-to-projection-parser.md
---

# RB-0026: Local Secret Generation & Targeting

This runbook explains how to execute the **Secret Request Parser** locally. This is useful for dry-running new secret requests, validating intent YAMLs, or surgically generating infrastructure variables without waiting for a full CI cycle.

## 🧭 Context

The [Secret Request Parser](file:///Users/mikesablaze/goldenpath-idp-infra/scripts/secret_request_parser.py) is the intelligence layer that translates developer YAMLs into Terraform and Kubernetes configurations. Running it locally allows you to verify that your "Intent" will produce the expected "Implementation."

---

## 🛠️ Prerequisites

1.  **Python 3.10+** installed.
2.  **PyYAML** library: `pip install PyYAML`.
3.  Working directory must be the project root.

---

## ⚡ Execution Steps

### 1. Validate Intent (Dry Run)
Before generating any files, you can validate that your `SecretRequest` YAML satisfies the platform's schema and governance rules (e.g., rotation requirements).

```bash
python3 scripts/secret_request_parser.py \
  --mode validate \
  --enums schemas/metadata/enums.yaml \
  --input-files docs/catalogs/secrets/payments/dev/SEC-0007.yaml
```

### 2. Generate Implementation (Targeting)
To generate the Terraform `.tfvars` and Kubernetes `ExternalSecret` manifests for a specific resource, use the `generate` mode and target the file explicitly.

```bash
python3 scripts/secret_request_parser.py \
  --mode generate \
  --enums schemas/metadata/enums.yaml \
  --input-files docs/catalogs/secrets/payments/dev/SEC-0007.yaml
```

> [!TIP]
> **Surgical Targeting**: You can pass multiple files to `--input-files` to generate a batch, or a single file to isolate just one resource.

---

## 🔍 Verification & Mapping

Once execution succeeds, the parser will emit files to deterministic locations:

| Target | Output Location | Purpose |
| :--- | :--- | :--- |
| **Terraform** | `envs/<env>/secrets/generated/<service>/SEC-XXXX.auto.tfvars.json` | Cloud resource provisioning |
| **GitOps** | `gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/SEC-XXXX.yaml` | Cluster-side projection |

---

## 🏗️ The "Dual-Projection" Model

A common question is: **Why can't I just run `terraform apply`?**

In our platform, a secret isn't functional until it exists in both AWS and Kubernetes. Running `terraform apply` in isolation only completes the **infrastructure** half. The Parser script is the only component that bridges the two worlds:

1.  **Infrastructure (AWS)**: The generated `*.auto.tfvars.json` tells Terraform to create the secret and the IAM policy in AWS Secrets Manager.
2.  **Projection (K8s)**: The generated `ExternalSecret` manifest tells the **External Secrets Operator (ESO)** in your cluster *which* AWS secret to fetch and *where* to put it in Kubernetes.

> [!IMPORTANT]
> **Without the Parser**, you have a secret in the cloud but no way for your application to see it. **Without Terraform**, you have a request in the cluster that will fail because the cloud resource doesn't exist.

---

---

## 🚀 Next Steps (Closing the Loop)

After the parser generates the implementation artifacts, you must follow these steps to bring the secret to life:

### 1. Provision the AWS Resource
Navigate to the Terraform environment and apply the changes. 

> [!IMPORTANT]
> **Subdirectory Discovery**: Terraform only automatically loads `*.auto.tfvars.json` from the **current directory**. Since the parser organizes files into `secrets/generated/`, you must explicitly pass the file using the `-var-file` flag.

```bash
cd envs/dev
# Target the specific secret and pass the generated var-file
terraform plan \
  -target='module.app_secrets["payments-payments-db-credentials"]' \
  -var-file='secrets/generated/payments/SEC-0007.auto.tfvars.json'
```

### 2. Commit and Sync (GitOps)
The `ExternalSecret` manifest must be committed to the repository for ArgoCD to pick it up.

```bash
git add gitops/kustomize/overlays/dev/apps/payments/externalsecrets/
git commit -m "feat(secrets): add ESO projection for SEC-0007"
git push origin <your-branch>
```

### 3. Reconcile in Cluster
*   **Automatic**: ArgoCD will sync the new manifest within its next refresh cycle (usually 3-5 minutes).
*   **Surgical Sync**: You can trigger a manual sync in the ArgoCD UI or via CLI to prioritize this change.

---

### Linking to Terraform

---

## 🚑 Troubleshooting

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `missing required fields` | The YAML is incomplete. | Check [ADR-0143](file:///Users/mikesablaze/goldenpath-idp-infra/docs/adrs/ADR-0143-secret-request-contract.md) for required fields. |
| `invalid rotationClass` | Governance violation. | Ensure `risk: high` secrets have a non-none rotation class. |
| `ModuleNotFoundError` | Missing Python dependency. | Run `pip install PyYAML`. |

---

## 🤝 Support
For complex policy violations or parser logic changes, contact the **@platform-team**.
