# ADR-0143: Standardization of the SecretRequest Interface

## Status
Proposed

## Decision
We designate kind: SecretRequest as the primary interface for managing sensitive data. This contract binds AWS Secrets Manager, ESO, and IAM into a single simplified request.

## Specification
The protocol uses a standard Kubernetes-style manifest.

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
  - `notes`: Optional human-readable context

## Conditional Governance Logic
The platform enforces the following guards during the validation phase:

| riskTier | Approval Required | rotationClass Requirement | Action on Violation |
| :--- | :---: | :---: | :--- |
| **high** | Yes | != `none` | **Block** provisioning/PR |
| **medium** | Yes | Recommended | **Warn** (PR comment) if `none` |
| **low** | Optional | Optional | Allow |

## Compliance
- All SecretRequest files must be stored in gitops/catalog/secrets/.
- Must satisfy the PR_GUARDRAILS.py.
