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
| **GitOps** | `gitops/environments/<env>/secrets/SEC-XXXX-external-secret.yaml` | Cluster-side projection |

### Linking to Terraform
To verify the generated variables against the live environment:

```bash
cd envs/dev
terraform plan
```
*Terraform will automatically pick up any `*.auto.tfvars.json` file in the directory.*

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
