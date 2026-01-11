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
spec:
  service: payments                 # Service namespace
  environment: dev                  # Enum: environments
  provider: aws-secrets-manager      # Enum: providers
  secretType: database-credentials   # Enum: security.secret_types
  riskTier: medium                  # Enum: security.risk_tiers
  rotationClass: standard           # Enum: security.rotation_classes
  lifecycleStatus: active           # Enum: security.lifecycle_status
  ttlDays: 30                       # Lifecycle Bind
  notes: "Optional context"         # Optional human-readable context
```

2. **Global Abstraction Strategy** ([PLATFORM_CONTRACT_RATIONALE.md](PLATFORM_CONTRACT_RATIONALE.md))
