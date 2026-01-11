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
1. SecretRequest Protocol
2. Global Abstraction Strategy (PLATFORM_CONTRACT_RATIONALE.md)
