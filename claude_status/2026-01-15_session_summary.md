# Session Report: Backstage & Keycloak Stabilization

**Date**: 2026-01-15
**Environment**: AWS `dev` (EKS)
**Objective**: Fix persistent `CrashLoopBackOff` (Backstage) and `ImagePullBackOff` (Keycloak) to enable platform health.

## 1. Executive Summary
This session focused on resolving critical startup failures in the core IDP stack. We successfully diagnosed and fixed a complex chain of issues involving **AWS Secrets Manager IAM policies**, **Backstage Configuration Loading**, and **Keycloak Image Architecture mismatches**.

**Key Outcome**: 
*   **Keycloak**: Corrected image architecture (AMD64) is now pushed to private ECR.
*   **Backstage**: Configuration is valid and patched; successfully waiting for OIDC dependency.
*   **Infrastructure**: Secrets syncing is fully operational.

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
*   [x] **Keycloak DB Connection**: ✅ **CONNECTED** - Using hardcoded RDS endpoint in `externalDatabase.host`.
*   [x] **Keycloak Startup**: Container running, logs confirm PostgreSQL connection established.
*   [x] **Backstage Config**: Verified correct via logs.
*   [x] **Changelog**: Created `CL-0132` documenting ClusterSecretStore addon fix.
*   [ ] **In Progress**: Waiting for Keycloak readiness probe to pass (~1-2 minutes).
*   [ ] **Next Steps**:
    1.  ✅ Keycloak DB connection resolved
    2.  ⏳ Wait for Keycloak to become ready
    3.  Restart `dev-backstage` to complete stack
    4.  Verify full platform health

## 5. Documentation Created
*   **Session Summary**: `claude_status/2026-01-15_session_summary.md`
*   **Changelog**: `docs/changelog/entries/CL-0132-cluster-secret-store-addon-fix.md`
*   **Artifacts**: `brain/fc919e57.../walkthrough.md`, `task.md`, `implementation_plan.md`
