---
id: RB-0036
title: GitHub App Setup for ArgoCD Image Updater
type: runbook
relates_to:
  - ADR-0170-build-pipeline-architecture
  - GOV-0012-build-pipeline-standards
  - argocd_image_updater
tags:
  - github-app
  - image-updater
  - gitops
  - authentication
category: runbooks
---

# RB-0036: GitHub App Setup for ArgoCD Image Updater

## Purpose

Configure a GitHub App for ArgoCD Image Updater to write back image tag changes
to Git repositories. This replaces deploy keys with a more secure, org-wide
authentication method with automatic token rotation.

## Prerequisites

- GitHub organization admin access
- AWS Secrets Manager access
- kubectl access to target cluster

## Why GitHub App over Deploy Keys?

| Aspect | Deploy Key | GitHub App |
|--------|------------|------------|
| Scope | Single repo only | Org-wide or multi-repo |
| Token rotation | Manual | Automatic (1-hour expiry) |
| Audit trail | Limited | Rich (app name, installation ID) |
| Setup effort | Low per repo | Medium once, then zero |
| Multi-repo | One key per repo | One app covers all |

## Step 1: Create GitHub App

1. Navigate to **GitHub Organization Settings** → **Developer Settings** → **GitHub Apps**

2. Click **New GitHub App**

3. Configure the app:

   **Basic Information:**
   ```
   App name: goldenpath-image-updater
   Homepage URL: https://github.com/mikeybeezy/goldenpath-idp-infra
   ```

   **Webhook:**
   - Uncheck "Active" (not needed for write-back)

   **Permissions:**
   ```
   Repository permissions:
   - Contents: Read and write
   - Metadata: Read-only

   Organization permissions:
   - None required
   ```

   **Where can this GitHub App be installed?**
   - Select "Only on this account"

4. Click **Create GitHub App**

5. Note the **App ID** (displayed on the app page)

## Step 2: Generate Private Key

1. On the GitHub App page, scroll to **Private keys**

2. Click **Generate a private key**

3. A `.pem` file will download - save this securely

## Step 3: Install the App

1. On the GitHub App page, click **Install App** (left sidebar)

2. Select your organization

3. Choose repositories:
   - **Selected repositories** (recommended)
   - Add: `hello-goldenpath-idp` and any other app repos

4. Click **Install**

5. Note the **Installation ID** from the URL:
   ```
   https://github.com/organizations/ORG/settings/installations/INSTALLATION_ID
   ```

## Step 4: Store Credentials in AWS Secrets Manager

Store the GitHub App credentials for each environment:

```bash
# Create the secret
aws secretsmanager create-secret \
  --name "goldenpath/dev/github-app/image-updater" \
  --secret-string '{
    "appID": "YOUR_APP_ID",
    "installationID": "YOUR_INSTALLATION_ID",
    "privateKey": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
  }' \
  --region eu-west-2

# For staging/prod, create separate secrets (may use same app with different installs)
aws secretsmanager create-secret \
  --name "goldenpath/staging/github-app/image-updater" \
  --secret-string '...' \
  --region eu-west-2

aws secretsmanager create-secret \
  --name "goldenpath/prod/github-app/image-updater" \
  --secret-string '...' \
  --region eu-west-2
```

## Step 5: Create Kubernetes Secret

Create the secret in the cluster for image-updater to use:

```bash
# Fetch from Secrets Manager
SECRET_JSON=$(aws secretsmanager get-secret-value \
  --secret-id "goldenpath/dev/github-app/image-updater" \
  --query SecretString --output text)

APP_ID=$(echo "$SECRET_JSON" | jq -r '.appID')
INSTALLATION_ID=$(echo "$SECRET_JSON" | jq -r '.installationID')
PRIVATE_KEY=$(echo "$SECRET_JSON" | jq -r '.privateKey')

# Create Kubernetes secret
kubectl create secret generic github-app-image-updater \
  --namespace argocd \
  --from-literal=github-app-id="$APP_ID" \
  --from-literal=github-app-installation-id="$INSTALLATION_ID" \
  --from-literal=github-app-private-key="$PRIVATE_KEY"
```

## Step 6: Update Image Updater Configuration

Update the image-updater values to use GitHub App authentication:

**`gitops/helm/argocd-image-updater/values/dev.yaml`:**

```yaml
config:
  # ... existing config ...

  # GitHub App authentication for git write-back
  gitCommitUser: goldenpath-image-updater[bot]
  gitCommitMail: goldenpath-image-updater[bot]@users.noreply.github.com

# Mount GitHub App credentials
extraEnv:
  - name: ARGOCD_IMAGE_UPDATER_GIT_WRITE_BACK_TARGET
    value: "git"
  - name: GIT_AUTH_METHOD
    value: "github-app"

extraVolumes:
  - name: github-app-creds
    secret:
      secretName: github-app-image-updater

extraVolumeMounts:
  - name: github-app-creds
    mountPath: /app/config/github-app
    readOnly: true
```

## Step 7: Update Application Annotations

Update ArgoCD Application manifests to use GitHub App:

```yaml
metadata:
  annotations:
    # Write-back with GitHub App
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
    argocd-image-updater.argoproj.io/git-credentials: secret:argocd/github-app-image-updater
```

## Step 8: Verify Configuration

1. Trigger an image update by pushing a new image:
   ```bash
   docker push 593517239005.dkr.ecr.eu-west-2.amazonaws.com/hello-goldenpath-idp:latest
   ```

2. Check image-updater logs:
   ```bash
   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
   ```

3. Verify git commit appears in the app repo

## Troubleshooting

### Issue: Authentication Failed

**Symptom:**
```
error authenticating to git repository: authentication required
```

**Resolution:**
1. Verify App ID and Installation ID are correct
2. Check private key format (must include header/footer)
3. Verify app is installed on the target repository

### Issue: Permission Denied

**Symptom:**
```
error pushing to git repository: permission denied
```

**Resolution:**
1. Verify GitHub App has "Contents: Read and write" permission
2. Re-install the app if permissions were changed after installation

### Issue: Rate Limited

**Symptom:**
```
error: API rate limit exceeded
```

**Resolution:**
- GitHub App has higher rate limits than personal tokens
- If hitting limits, reduce image-updater interval

## Secret Rotation

GitHub App private keys can be rotated without downtime:

1. Generate new private key in GitHub App settings
2. Update Secrets Manager
3. Recreate Kubernetes secret
4. Restart image-updater pod
5. Delete old key from GitHub App settings

## Related Documentation

- [ADR-0170: Build Pipeline Architecture](../../adrs/ADR-0170-build-pipeline-architecture.md)
- [GOV-0012: Build Pipeline Standards](../../10-governance/policies/GOV-0012-build-pipeline-standards.md)
- [ArgoCD Image Updater Docs](https://argocd-image-updater.readthedocs.io/)
