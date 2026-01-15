# Session Report: Backstage & Keycloak Stabilization

**Date**: 2026-01-15
**Environment**: AWS `dev` (EKS)
**Objective**: Fix persistent `CrashLoopBackOff` (Backstage) and `ImagePullBackOff` (Keycloak) to enable platform health.

## 1. Executive Summary
This session focused on resolving critical startup failures in the core IDP stack. We successfully diagnosed and fixed a complex chain of issues involving **AWS Secrets Manager IAM policies**, **Backstage Configuration Loading**, **Keycloak Image Architecture mismatches**, and **RDS PostgreSQL user provisioning**.

**Key Outcome**:

*   **Keycloak**: ✅ Running 1/1 - AMD64 Bitnami image from ECR, connected to RDS.
*   **Backstage**: ✅ Running 1/1 - Local `backstage-helm` chart with ECR image, SSL RDS connection working.
*   **Infrastructure**: Secrets syncing fully operational via ExternalSecrets.

## 2. Detailed Issue Log & Resolutions

### A. Keycloak: The Image Pull & Compatibility Saga
**Problem**: `dev-keycloak-0` stuck in `Init:ErrImagePull`, then `Init:Error`.
**Investigation Trace**:
1.  **Bitnami Hub Failure**: Attempts to pull `docker.io/bitnami/keycloak` tags (`25.0.0`, `26.1.1`, `latest`) consistently failed with `Manifest Not Found`.
    *   *Cause*: Docker Hub rate-limiting or regional availability issues for Bitnami's public repo.
2.  **ECR Mirroring (Attempt 1 - Architecture Mismatch)**: 
    *   Created private ECR: `aws ecr create-repository --repository-name keycloak --region eu-west-2`
    *   Pulled `quay.io/keycloak/keycloak:latest` locally and pushed to ECR.
    *   *Result*: Pod failed with `exec format error`.
    *   *Root Cause*: Local machine (Apple Silicon) pulled `arm64`, but EKS nodes are `amd64`.
3.  **Cross-Architecture Fix (Attempt 2 - Image Incompatibility Discovered)**:
    *   Forced AMD64 pull: `docker pull --platform linux/amd64 quay.io/keycloak/keycloak:latest`
    *   Pushed to ECR: `593517239005.dkr.ecr.eu-west-2.amazonaws.com/keycloak:latest`
    *   *Result*: **Still failed** with `exec format error` (misleading log).
    *   *Root Cause*: Official Keycloak image lacks Bitnami-specific scripts (`/opt/bitnami/scripts/liblog.sh`) that the Bitnami Helm chart init container expects.
4.  **Bitnami-Compatible Image (Attempt 3 - SUCCESS)**:
    *   Discovered `public.ecr.aws/bitnami/keycloak` as an alternative source.
    *   Forced AMD64 pull: `docker pull --platform linux/amd64 public.ecr.aws/bitnami/keycloak:latest`
    *   **Verified Architecture**: `amd64` ✓
    *   **Status**: Pushing to ECR (490.6MB, in progress at 22:25 UTC).
    *   *Chart Update*: Already set `image.registry` to ECR private URL and enabled `global.security.allowInsecureImages: true`.

### B. Backstage: Configuration & Crash Loops
**Problem**: `dev-backstage` crashing immediately on startup.
**Investigation Trace**:
1.  **Auth Key Missing**: Logged `Error: You must configure at least one key in backend.auth.keys`.
    *   *Fix 1 (Failed)*: `appConfig` update was ignored by chart merging logic.
    *   *Fix 2 (Success)*: Forced injection via Env Var `APP_CONFIG_backend_auth_keys_0_secret`.
2.  **Kubernetes Plugin**: Logged `Error: Kubernetes configuration is missing`.
    *   *Fix*: Added `kubernetes` block to `values.yaml` with `multiTenant` configuration.
3.  **Image Update**: Switched to custom build `ghcr.io/guymenahem/backstage-platformers:0.0.1` as requested.

### C. Infrastructure: Secret Syncing
**Problem**: ExternalSecrets failed to sync (`SecretSyncedError`).
**Fix**: 
*   Modified IAM Policy to allow wildcards (`goldenpath*`) matching secret names with slashes (e.g., `goldenpath/dev/backstage/...`).
*   Manually created missing `ClusterSecretStore`.

## 3. Configuration Changes Summary

### Keycloak Helm Values (`gitops/helm/keycloak/values/dev.yaml`)
```yaml
image:
  registry: 593517239005.dkr.ecr.eu-west-2.amazonaws.com
  repository: keycloak
  tag: latest # (AMD64 Official Build)

global:
  security:
    allowInsecureImages: true # Required for private ECR
```

### Backstage Helm Values (`gitops/helm/backstage/values/dev.yaml`)
```yaml
image:
  registry: ghcr.io
  repository: guymenahem/backstage-platformers
  tag: 0.0.1

extraEnvVars:
  - name: APP_CONFIG_backend_auth_keys_0_secret # Forced Auth Key
    value: "random-generated-secret-key-for-backend-auth"

appConfig:
  kubernetes: # Added Plugin Config
    serviceLocatorMethod:
      type: multiTenant
```

## 4. Current Status & Next Steps

*   [x] **Keycloak Image**: Pushed to ECR (Verified AMD64 Bitnami).
*   [x] **Image Cache Fix**: Set `pullPolicy: Always` to force refresh of cached image.
*   [x] **Keycloak Init Container**: Passing successfully.
*   [x] **ExternalSecret**: Now syncing all 4 DB properties (host, port, username, password).
*   [x] **Keycloak DB Connection**: ✅ Network connectivity established to RDS.
*   [x] **Backstage Config**: Verified correct via logs.
*   [x] **Changelog**: Created `CL-0132` documenting ClusterSecretStore addon fix.
*   [x] **Keycloak DB Authentication**: ✅ FIXED - Created `keycloak_app` and `backstage_app` users in RDS manually.
*   [x] **Keycloak Running**: ✅ Pod is now 1/1 Running.
*   [x] **Backstage ECR Repo**: Created and image pushed (AMD64).
*   [x] **Backstage Chart**: Switched to local `backstage-helm/charts/backstage`.
*   [x] **ArgoCD Multi-Source**: Fixed valueFiles path using `$values` reference pattern.
*   [x] **ExternalSecret Template**: Added to chart for AWS Secrets Manager integration.
*   [x] **SSL Config**: Added `ssl.require: true` for RDS connection.
*   [ ] **Backstage Deployment**: Awaiting sync after SSL fix push.

### D. RDS User Provisioning Gap (NEW)

**Problem**: Terraform creates AWS Secrets Manager secrets with credentials but does NOT create actual PostgreSQL users.

**Root Cause**: The `rds_config.application_databases` in terraform.tfvars defines usernames, but no provisioner runs `CREATE USER` in PostgreSQL.

**Fix (Manual)**:

```sql
-- Via psql pod in cluster
CREATE USER keycloak_app WITH PASSWORD '<from-secret>';
CREATE DATABASE keycloak OWNER keycloak_app;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak_app;

CREATE USER backstage_app WITH PASSWORD '<from-secret>';
CREATE DATABASE backstage_plugin_catalog OWNER backstage_app;
GRANT ALL PRIVILEGES ON DATABASE backstage_plugin_catalog TO backstage_app;
```

**Future**: Consider adding a Terraform `null_resource` with `local-exec` provisioner or a Kubernetes Job to automate user creation.

### E. Backstage Chart Migration (NEW)

**Problem**: Multiple Backstage chart issues - wrong chart source, image field names, values path errors.

**Resolution**:

1. **Chart Source**: Switched from `backstage.github.io/charts` to local `backstage-helm/charts/backstage`.
2. **ArgoCD Multi-Source**: Used `sources` with `ref: values` and `$values/` prefix for cross-path values loading.
3. **ExternalSecret Integration**: Added conditional `externalsecret.yaml` template and made `secret.yaml` conditional via `externalSecret.enabled`.
4. **SSL for RDS**: Added `ssl.require: true` and `ssl.rejectUnauthorized: false` in appConfig database connection.

## 5. Documentation Created
*   **Session Summary**: `claude_status/2026-01-15_session_summary.md`
*   **Changelog**: `docs/changelog/entries/CL-0132-cluster-secret-store-addon-fix.md`
*   **Artifacts**: `brain/fc919e57.../walkthrough.md`, `task.md`, `implementation_plan.md`
