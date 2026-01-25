<!-- AGENT_CONTEXT: Read .agent/README.md for rules -->
---
id: CONTRACT_REGISTRY
title: Platform Contract Registry
type: contract
domain: governance
risk_profile:
  production_impact: none
  security_risk: none
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
relates_to:
  - ADR-0143
---

# Platform Contract Registry

This registry tracks the maturity and implementation status of all Golden Path declarative interfaces.

## Contract Creation Matrix

| Kind | Description | Category | Todo | Done | Documentation |
| :--- | :--- | :--- | :---: | :---: | :--- |
| SecretRequest | Managed with AWS Secrets Manager + ESO. | Security | [ ] | [x] | [ADR-0143](../../adrs/ADR-0143-secret-request-contract.md) |
| StorageRequest | Managed with S3 Buckets or EFS. | Storage | [ ] | [ ] | TBD |
| DatabaseRequest | Managed with RDS (Postgres/MySQL). | Data | [ ] | [ ] | TBD |
| RoutingRequest | Managed with Kong/Ingress. | Network | [ ] | [ ] | TBD |

## Index
1. **SecretRequest Protocol**
```yaml
apiVersion: goldenpath.io/v1
kind: SecretRequest
metadata:
  id: SEC-0007                      # Format: SEC-XXXX
  name: payments-db-credentials     # Intent name
  owner: team-payments              # Enum: owners
  service: payments                 # Service namespace
  environment: dev                  # Enum: environments
spec:
  provider: aws-secrets-manager      # Enum: providers
  secretType: database-credentials   # Enum: security.secret_types
  risk:
    tier: medium                     # Enum: security.risk_tiers
  rotation:
    rotationClass: standard           # Enum: security.rotation_classes
  lifecycle:
    status: active                   # Enum: security.lifecycle_status
  access:
    namespace: payments              # K8s Namespace
    k8sSecretName: payments-db-creds # Projected Secret Name
  ttlDays: 30                       # Lifecycle Bind
  notes: "Optional human context"    # Optional context
```

2. **Global Abstraction Strategy** ([PLATFORM_CONTRACT_RATIONALE.md](PLATFORM_CONTRACT_RATIONALE.md))
