---
id: test-plan
title: metadata
type: test-suite
---

# Feature Test Plan: Secret Request Flow

- **ID**: FT-SEC-001
- **Feature**: Secret Request Lifecycle (Backstage -> AWS -> K8s)
- **Status**: [x] Verified
- **Owner**: platform-team
- **Relates-To**: [ADR-0143](../../docs/adrs/ADR-0143-secret-request-contract.md)

---

## 🎯 Objectives
Verify that the `SecretRequest` manifest is correctly parsed, validated (camelCase), and transformed into actionable infrastructure (Terraform) and GitOps (ExternalSecret) assets.

## ✅ Success Criteria
1.  **Validation**: Manifests using `camelCase` properties are accepted.
2.  **Gating**: `riskTier: high` is blocked if `rotationClass: none`.
3.  **TF Generation**: `.auto.tfvars.json` produced with correct module mapping.
4.  **GitOps Generation**: `ExternalSecret` produced with deterministic `goldenpath/` keys.
5.  **Traceability**: All assets are linked via Audit ID (SEC-XXXX).

## 🛠️ Test Setup
- **Source**: `docs/20-contracts/secret-requests/payments/dev/SEC-0007.yaml`
- **Tool**: `scripts/secret_request_parser.py`
- **Enums**: `schemas/metadata/enums.yaml`

## 📖 Execution Steps
1.  Run `scripts/secret_request_parser.py --mode validate --input-files <path>`
2.  Run `scripts/secret_request_parser.py --mode generate --input-files <path>`
3.  Inspect `envs/dev/secrets/generated/` for JSON outputs.
4.  Inspect `gitops/kustomize/overlays/dev/` for YAML outputs.
