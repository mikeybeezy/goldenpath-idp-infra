---
id: ADR-0143
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
relates_to:
  - how-it-works/SECRET_REQUEST_FLOW.md
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
  owner: app-team                   # Mandatory: Accountability (Enum: owners)
  service: payments                 # Mandatory: Service namespace
  environment: dev                  # Mandatory: Environment (Enum: environments)
spec:
  provider: aws-secrets-manager      # Mandatory: Provider
  secretType: database-credentials   # Mandatory: Type (Enum: security.secret_types)
  risk:
    tier: medium                     # Mandatory: Governance (Enum: security.risk_tiers)
  rotation:
    rotationClass: standard          # Mandatory: Security (Enum: security.rotation_classes)
  lifecycle:
    status: active                   # Mandatory: Lifecycle (Enum: security.lifecycle_status)
  access:
    namespace: payments              # Mandatory: K8s Namespace
    k8sSecretName: payments-db-creds # Mandatory: K8s Secret Name
    # NEW: Security principal hooks for resource-level IAM
    readPrincipals: ["arn:aws:iam::...:role/eso-role"]
    writePrincipals: ["arn:aws:iam::...:role/secrets-writer"]
    breakGlassPrincipals: ["arn:aws:iam::...:role/platform-admin"]
  ttlDays: 30                       # Mandatory: Cleanup (Days)
```

### Schema Detail
- **Metadata**:
  - `id`: Unique Audit ID (Format: `SEC-XXXX`)
  - `name`: Intent-based resource name
  - `owner`: Accountability reference (Enum: `owners`)
  - `service`: Target service namespace
  - `environment`: Deployment target (Enum: `environments`)
- **Spec**:
  - `provider`: Infrastructure provider
  - `secretType`: Categorization (Enum: `security.secret_types`)
  - `risk.tier`: Security risk classification (Enum: `security.risk_tiers`)
  - `rotation.rotationClass`: Rotation posture (Enum: `security.rotation_classes`)
  - `lifecycle.status`: Operational state (Enum: `security.lifecycle_status`)
  - `access.namespace`: Target Kubernetes namespace for projection
  - `access.k8sSecretName`: Target name for the projected Kubernetes secret
  - `access.readPrincipals`: List of IAM ARNs with read access to the AWS secret
  - `access.writePrincipals`: List of IAM ARNs with write/update access
  - `access.breakGlassPrincipals`: ARNs for emergency/administrative access
  - `ttlDays`: Time-to-live for the managed resource

## Workflow (High Level)
1. **PR opened** with SecretRequest record.
2. CI validates enums/schema and generates a **preview** (no cloud changes).
3. Platform reviews and approves based on risk tier.
4. On merge, automation:
   - provisions/updates the secret in AWS Secrets Manager
   - generates/commits the `ExternalSecret` manifest (GitOps)
   - generates/commits the `*.auto.tfvars.json` (Terraform)
5. Argo CD reconciles the cluster; ESO hydrates the secret into the namespace.

## Governance & Rotation Policy
The platform enforces the following guards based on the `risk.tier`:

| risk.tier | Approval Required | rotationClass Requirement | Action on Violation |
| :--- | :---: | :---: | :--- |
| **high** | Yes | != `none` | **Block** provisioning/PR |
| **medium** | Yes | Recommended | **Warn** (PR comment) if `none` |
| **low** | Optional | Optional | Allow |

*Note: Not all secret types support automated rotation. If rotation is not enabled, the request must remain explicit about the posture (`rotationClass: none`) and be traceable.*

## Decommissioning
Decommissioning is intent-based to prevent accidental deletion and ensure auditability:

**Lifecycle Progression**:
`active → deprecated → decommission_requested → decommissioned`

**Sequencing**:
1. Change `lifecycle.status` to `decommission_requested`.
2. Automation removes the `ExternalSecret` (stop cluster projection).
3. Best-effort checks confirm no active consumers.
4. Final deletion of the AWS secret and transition to `decommissioned`.
5. Record an audit entry.

## Appendix: Projection Mapping (Intent to Implementation)
This section demonstrates how the high-level `SecretRequest` manifest projects into low-level Kubernetes resources managed by the External Secrets Operator (ESO).

### 1. Developer Intent (Input)
Location: `docs/catalogs/secrets/<service>/<env>/<secret-id>.yaml`

```yaml
apiVersion: goldenpath.io/v1
kind: SecretRequest
metadata:
  id: SEC-0007
  name: payments-db-credentials
  owner: app-team
  service: payments
  environment: dev
spec:
  provider: aws-secrets-manager
  secretType: database-credentials
  risk:
    tier: medium
  rotation:
    rotationClass: standard
  lifecycle:
    status: active
  access:
    namespace: payments
    k8sSecretName: payments-db-creds
    # NEW: Security principal hooks
    readPrincipals: ["arn:aws:iam::593517239005:role/goldenpath-idp-eso-role"]
    writePrincipals: ["arn:aws:iam::593517239005:role/github-actions-secrets-writer"]
    breakGlassPrincipals: ["arn:aws:iam::593517239005:role/platform-admin"]
  ttlDays: 30
```

### 2. Platform Projection (Output)

#### The ExternalSecret (The "What")
This manifest is auto-generated by the platform and pushed to the GitOps repository.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: payments-db-credentials-sync
  namespace: payments
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: payments-db-creds
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: "goldenpath/payments/dev/payments-db-credentials"
```

#### The SecretStore (The "How")
The platform ensures a ClusterSecretStore is available for that environment.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: eso-irsa-sa
            namespace: external-secrets
```

## Source of Truth
- **SecretRequest record**: Git
- **Secret authority/value**: AWS Secrets Manager
- **Runtime projection**: ESO + Kubernetes Secret
- **Deployment/reconciliation**: Argo CD

## Compliance
- All SecretRequest files must be stored in `catalogs/secrets/`.
- Must satisfy the `PR_GUARDRAILS.py` validation engine.
