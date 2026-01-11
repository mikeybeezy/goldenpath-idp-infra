# How It Works: Secret Request Flow

This document explains the technical lifecycle of a platform secret, following the Golden Path "Intent vs. Projection" model.

## 1. Developer Intent (The "What")
The process starts when a developer defines their requirement in a standard, low-entropy manifest. They do not specify AWS details or ESO configuration; they declare their **Intent**.

**Manifest Location**: `catalogs/secrets/<service>/<env>/<id>.yaml`

**Standard Fields**:
- **id**: Unique SEC-XXXX identifier.
- **owner**: The team responsible for the secret.
- **risk.tier**: Drives the approval and rotation posture.
- **access**: Defines the target Kubernetes coordinate.

## 2. Platform Processing (The "Logic")
When the PR is opened, the platform automation executes the following logic:

### Validation
- **Schema Check**: Ensures all required fields are present.
- **Enum Check**: Ensures `risk.tier`, `rotationClass`, and `lifecycle.status` match `schemas/metadata/enums.yaml`.
- **Governance Gate**: If `risk.tier` is `high`, the automation verifies that `rotationClass` is not `none`.

### Transformation
The platform "unpacks" the developer manifest into the specific implementation requirements for the selected cloud provider.

## 3. Infrastructure Projection (The "Implementation")
Once the PR is merged, the platform 프로젝트 the intent into two domains:

### Cloud Domain: AWS Secrets Manager
- The automation creates or updates a secret in AWS Secrets Manager.
- The path is standardized: `goldenpath/<service>/<env>/<name>`.
- Rotation lambdas are attached based on the `rotationClass`.

### Cluster Domain: External Secrets Operator (ESO)
- The platform generates an `ExternalSecret` manifest.
- This manifest tells the cluster's ESO controller to pull the value from the standardized AWS path.
- The secret is then "hydrated" into the developer's requested Kubernetes Namespace.

## 4. Consumption
The application consumes the secret as a standard Kubernetes `Secret` object. The app code remains decoupled from the infrastructure provider (AWS), allowing for future portability.

## Summary: Abstraction Layer
By using this "SecretRequest" flow, the developer manages a 15-line YAML file, while the platform handles:
- **Security**: IAM IRSA identities and AWS path isolation.
- **Governance**: Approval workflows based on risk.
- **Operations**: Automated rotation and decommissioning.
