---
id: HIW_SECRET_FLOW
title: "How It Works: Secret Request Flow"
status: active
version: "1.0"
---

# How It Works: Secret Request Flow

This document explains the technical lifecycle of a platform secret, following the Golden Path "Intent vs. Projection" model.

## 0. High-Level Architecture
This diagram shows how a single developer intent is transformed into cloud infrastructure and cluster hydration.

```text
+---------------+       +-----------------------+
|   Developer   | ----> |    Git Repository     |
+---------------+       +-----------------------+
                                    |
                          ( CI / Schema Validation )
                                    |
+-----------------------+           |
|  Platform Automation  | <---------+ (PR Merged)
+-----------------------+
        |
        |       +-------------------------------+
        +-----> |      AWS Secrets Manager      |
        |       +-------------------------------+
        |       (path: goldenpath/service/env)
        |
        |       +-------------------------------+
        +-----> |   GitOps Repo / ArgoCD Sync   |
                +-------------------------------+
                                |
                        ( Remote Reconcile )
                                |
                +-------------------------------+
                |      Target K8s Cluster       |
                +-------------------------------+
                                |
                        +---------------+
                        |    ESO Pod    |
                        +---------------+
                                |
                        ( Secret Sync )
                                |
                        +---------------+       +-------------------+
                        |  K8s Secret   | ----> |   App Container   |
                        +---------------+       +-------------------+
```

## 1. Developer Intent (The "What")
The process starts when a developer defines their requirement in a standard, low-entropy manifest. They declare their **Intent** without needing to understand the underlying infrastructure.

**Manifest Location**: `catalogs/secrets/<service>/<env>/<id>.yaml`

### Example: Intent
```yaml
apiVersion: goldenpath.io/v1
kind: SecretRequest
metadata:
  id: SEC-0007                      # Mandatory: Audit ID (SEC-XXXX)
  name: payments-db-credentials     # Mandatory: Intent Name
  owner: team-payments              # Mandatory: Accountability
  service: payments                 # Mandatory: Service namespace
  environment: dev                  # Mandatory: Environment
spec:
  provider: aws-secrets-manager      # Mandatory: Provider
  secretType: database-credentials   # Mandatory: Type
  risk:
    tier: medium                     # Mandatory: Governance
  rotation:
    rotationClass: standard          # Mandatory: Security
  lifecycle:
    status: active                   # Mandatory: Lifecycle
  access:
    namespace: payments              # Mandatory: K8s Namespace
    k8sSecretName: payments-db-creds # Mandatory: K8s Secret Name
  ttlDays: 30                       # Mandatory: Cleanup (Days)
```

## 2. Platform Processing (The "Logic")
When the PR is opened, the platform automation executes validation and governance logic.

### Validation & Governance
- **Schema & Enum Check**: Ensures all fields align with `schemas/metadata/enums.yaml`.
- **Governance Logic**: Enforces rules based on `risk.tier`. For example, `high` risk requires `rotationClass != none`.

## 3. Infrastructure Projection (The "Implementation")
Once the PR is merged, the platform 프로젝트 the intent into implementation manifests.

### The ExternalSecret (The "What")
This manifest is auto-generated and pushed to the GitOps repository. It translates the high-level intent into specific AWS paths.

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

## 4. Consumption
The application consumes the secret as a standard Kubernetes `Secret` object. The application code remains decoupled from the infrastructure provider (AWS), allowing for future portability.

## 5. Decommissioning
Decommissioning is intent-based to avoid accidental deletion and ensure auditability:

**Lifecycle Progression**:
`active → deprecated → decommission_requested → decommissioned`

**Sequencing**:
1. Change `lifecycle.status` to `decommission_requested`.
2. Automation removes the `ExternalSecret` (stop cluster projection).
3. Best-effort checks confirm no active consumers.
4. Final deletion of the AWS secret and transition to `decommissioned`.
5. Record an audit entry.
