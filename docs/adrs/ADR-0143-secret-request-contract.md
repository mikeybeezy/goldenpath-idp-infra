---
id: SECRET_REQUEST_CONTRACT
title: Secret Request Contract (V1)
type: documentation
domain: security
applies_to:
  - infra
  - ci
  - gitops
owner: platform-team
status: active
version: "1.0"
---

# ADR-0143: Secret Request Contract (V1)

## Status
Accepted

## Context
This contract defines how teams request application secrets through the platform in a governed, auditable way. It désigne kind: SecretRequest as the primary interface for managing sensitive data, binding AWS Secrets Manager, ESO, and IAM into a single simplified request.

## Principles
- **Backstage is the front door for intent** (request + context).
- **Git is the source of truth** (reviewable, auditable changes).
- **AWS Secrets Manager is the authority** (where secret values live).
- **ESO is the projection mechanism** (secrets are hydrated into clusters).
- **Apps consume secrets**; they do not manage lifecycle.

## Request Format
Secret requests are submitted as YAML records under the governed catalog path:
`catalogs/secrets/<service>/<env>/<secret-id>.yaml`

### Schema Example
```yaml
apiVersion: goldenpath.io/v1
kind: SecretRequest
metadata:
  id: SEC-0007                      # Mandatory: Audit ID (SEC-XXXX)
  name: payments-db-credentials     # Mandatory: Intent Name
  owner: team-payments              # Mandatory: Accountability (Enum: owners)
spec:
  service: payments                 # Mandatory: Service namespace
  environment: dev                  # Mandatory: Environment (Enum: environments)
  provider: aws-secrets-manager      # Mandatory: Portability (Enum: providers)
  secretType: database-credentials   # Mandatory: Type (Enum: security.secret_types)
  riskTier: medium                  # Mandatory: Governance (Enum: security.risk_tiers)
  rotationClass: standard           # Mandatory: Security (Enum: security.rotation_classes)
  lifecycleStatus: active           # Mandatory: Lifecycle (Enum: security.lifecycle_status)
  ttlDays: 30                       # Mandatory: Cleanup (Days)
  notes: "Optional human context"    # Optional Context
```

### Schema Detail
- **Metadata**:
  - `id`: Unique Audit ID (Format: `SEC-XXXX`)
  - `name`: Intent-based resource name
  - `owner`: Accountability reference (Enum: `owners`)
- **Spec**:
  - `service`: Target service namespace
  - `environment`: Deployment target (Enum: `environments`)
  - `provider`: Infrastructure provider (Enum: `providers`)
  - `secretType`: Categorization (Enum: `security.secret_types`)
  - `riskTier`: Security risk classification (Enum: `security.risk_tiers`)
  - `rotationClass`: Rotation posture (Enum: `security.rotation_classes`)
  - `lifecycleStatus`: Operational state (Enum: `security.lifecycle_status`)
  - `ttlDays`: Time-to-live for the managed resource

## Workflow (High Level)
1. **PR opened** with SecretRequest record (and any generated manifests).
2. CI validates enums/schema and runs a **plan** (no cloud changes).
3. Platform reviews and approves based on risk tier.
4. On merge, automation:
   - provisions/updates the secret in AWS Secrets Manager
   - generates or updates the `ExternalSecret` manifest (GitOps)
5. Argo CD reconciles the cluster; ESO hydrates the secret into the namespace.

## Governance & Rotation Policy
The platform enforces the following guards based on the `riskTier`:

| riskTier | Approval Required | rotationClass Requirement | Action on Violation |
| :--- | :---: | :---: | :--- |
| **high** | Yes | != `none` | **Block** provisioning/PR |
| **medium** | Yes | Recommended | **Warn** (PR comment) if `none` |
| **low** | Optional | Optional | Allow |

*Note: Not all secret types support automated rotation. If rotation is not enabled, the request must remain explicit about the posture (`rotationClass: none`) and be traceable.*

## Decommissioning
Decommissioning is intent-based to avoid accidental deletion:
`active → deprecated → decommission_requested → decommissioned`

**Sequencing**:
1. Remove the `ExternalSecret` (stop projection).
2. Confirm no consumers (best-effort checks).
3. Delete the AWS secret.
4. Record an audit entry.

## Source of Truth
- **SecretRequest record**: Git
- **Secret authority/value**: AWS Secrets Manager
- **Runtime projection**: ESO + Kubernetes Secret
- **Deployment/reconciliation**: Argo CD

## Compliance
- All SecretRequest files must be stored in `catalogs/secrets/`.
- Must satisfy the `PR_GUARDRAILS.py` validation engine.
