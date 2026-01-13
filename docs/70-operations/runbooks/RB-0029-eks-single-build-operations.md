---
id: RB-0029-eks-single-build-operations
title: EKS Single-Build Operations (Runbook)
type: runbook
risk_profile:
  production_impact: high
  security_risk: medium
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: silver
  maturity: 2
relates_to:
  - ADR-0148
  - ADR-0063
  - CL-0121
category: runbooks
supported_until: 2028-01-13
version: '1.0'
breaking_change: false
---

# RB-0029: EKS Single-Build Operations

This runbook provides step-by-step procedures for operating the EKS single-build
deployment system, including initial installation, verification, image updates,
troubleshooting, and teardown.

**Scope:** kubernetes_addons module, ArgoCD Image Updater, Metrics Server, bootstrap applications

**Related:**
- ADR-0148 (EKS Single-Build Refactor)
- EKS_SINGLE_BUILD_REFACTOR.md (Implementation Guide)
- CL-0121 (Changelog)

---

## Prerequisites

Before using this runbook, ensure you have:

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0 installed
- kubectl installed
- Helm >= 3.12 installed (optional, for debugging)
- Git access to the repository
- IAM permissions:
  - EKS cluster admin access
  - IAM role management
  - ECR repository access (for Image Updater)

---

## Table of Contents

1. [Initial Installation](#1-initial-installation)
2. [Post-Deployment Verification](#2-post-deployment-verification)
3. [Operating ArgoCD Image Updater](#3-operating-argocd-image-updater)
4. [Troubleshooting](#4-troubleshooting)
5. [Updating Components](#5-updating-components)
6. [Teardown and Cleanup](#6-teardown-and-cleanup)
7. [Emergency Procedures](#7-emergency-procedures)

---

## 1. Initial Installation

### Step 1.1: Prepare Environment Configuration

**Why:** Ensure Terraform variables are correctly set for your environment.

```bash
cd envs/dev  # or your target environment

# Review current configuration
cat terraform.tfvars
```

**Verify these key settings:**
```hcl
enable_k8s_resources              = true
enable_image_updater_role         = true
enable_metrics_server             = true
enable_post_deployment_verification = true
```

### Step 1.2: Initialize Terraform

**Why:** Download required providers and initialize backend.

```bash
terraform init
```

**Expected output:**
```
Terraform has been successfully initialized!
```

### Step 1.3: Plan Deployment

**Why:** Preview changes before applying to catch potential issues.

```bash
terraform plan -out=tfplan
```

**What to look for:**
- ArgoCD Helm release creation
- AWS Load Balancer Controller creation
- Metrics Server creation
- ArgoCD Image Updater creation (if enabled)
- Bootstrap applications creation
- IAM role creation (for Image Updater)
- Service account creation (for Image Updater)

**Expected resource count:** ~15-25 resources (varies by configuration)

### Step 1.4: Apply Configuration

**Why:** Deploy the entire platform with a single command.

```bash
terraform apply tfplan
```

**Duration:** ~25-35 minutes

**What happens:**
1. ArgoCD installs (2-3 min)
2. AWS LB Controller installs (parallel)
3. Metrics Server installs (parallel)
4. ArgoCD Image Updater installs (1-2 min)
5. Bootstrap applications deploy (5-10 min)
6. Verification checks run (1-2 min)

**Expected output:**
```
Apply complete! Resources: X added, 0 changed, 0 destroyed.

Outputs:
argocd_namespace = "argocd"
argocd_release_name = "argocd"
image_updater_installed = true
metrics_server_installed = true
...
```

### Step 1.5: Configure Kubernetes Access

**Why:** Update kubeconfig to access the newly created cluster.

```bash
# Get cluster name from Terraform output
CLUSTER_NAME=$(terraform output -raw cluster_name)
AWS_REGION=$(terraform output -raw region)

# Update kubeconfig
aws eks update-kubeconfig --name $CLUSTER_NAME --region $AWS_REGION
```

**Verify access:**
```bash
kubectl get nodes
```

---

## 2. Post-Deployment Verification

### Step 2.1: Run Automated Verification Script

**Why:** Comprehensive health check of all platform components.

```bash
cd ../../bootstrap  # From envs/dev
./verify-deployment.sh
```

**Expected output:**
```
=== Golden Path IDP - Deployment Verification ===

1. Checking Nodes...
    All nodes are Ready (3/3)

2. Checking ArgoCD Installation...
    ArgoCD namespace exists
    ArgoCD pods are ready (7/7)
    ArgoCD server is accessible

3. Checking ArgoCD Applications...
    cert-manager: Synced and Healthy
    external-secrets: Synced and Healthy
    cluster-autoscaler: Synced and Healthy
   ...

4. Checking Platform Components...
    Metrics Server: Deployed
    AWS Load Balancer Controller: Deployed
    ArgoCD Image Updater: Deployed

=== Deployment Health Score: 95% ===
Status: HEALTHY

ArgoCD Admin Credentials:
Username: admin
Password: [retrieved from cluster]

Access ArgoCD UI:
kubectl port-forward svc/argocd-server -n argocd 8080:443
https://localhost:8080
```

**Health Score Interpretation:**
- **90-100%:** Excellent - All systems operational
- **70-89%:** Good - Minor issues, investigate warnings
- **50-69%:** Degraded - Significant issues, troubleshooting required
- **<50%:** Critical - Deployment failed, rollback recommended

### Step 2.2: Manual Verification Checklist

**ArgoCD:**
```bash
# Check ArgoCD pods
kubectl get pods -n argocd
# All pods should be Running

# Check ArgoCD applications
kubectl get applications -n argocd
# All applications should show Synced status
```

**Metrics Server:**
```bash
# Verify metrics-server is working
kubectl top nodes
kubectl top pods -n argocd
# Should show resource usage, not errors
```

**ArgoCD Image Updater:**
```bash
# Check Image Updater pod
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-image-updater

# Check Image Updater logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater --tail=50
# Should show ECR registry detection and update checks
```

**AWS Load Balancer Controller:**
```bash
# Check controller pods
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# Check controller logs
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --tail=50
```

### Step 2.3: Access ArgoCD UI

**Why:** Visual verification of application deployment status.

**Method 1: Port Forward (Development)**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Then open: https://localhost:8080

**Method 2: LoadBalancer (Production - if configured)**
```bash
kubectl get svc argocd-server -n argocd
# Get EXTERNAL-IP
```

**Login:**
- Username: `admin`
- Password: Retrieved from verification script or:
  ```bash
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
  ```

---

## 3. Operating ArgoCD Image Updater

### Step 3.1: Understanding Image Updater

**What it does:**
- Checks ECR every 2 minutes for new image tags
- Updates ArgoCD Application manifests with new image references
- Commits changes to Git (audit trail)
- Triggers ArgoCD sync (automatic deployment)

**How it works:**
```
ECR Push → Image Updater Detects (2 min) → Git Commit → ArgoCD Sync → Deployed
```

### Step 3.2: Configure Application for Auto-Updates

**Why:** Enable automatic deployments for your application.

**Add annotations to your ArgoCD Application:**
```yaml
# gitops/argocd/apps/dev/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
  annotations:
    # Enable Image Updater
    argocd-image-updater.argoproj.io/image-list: myapp=123456789.dkr.ecr.us-east-1.amazonaws.com/my-app

    # Update strategy (latest, semver, digest)
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver:~1.0

    # Optional: Force update to specific parameter
    argocd-image-updater.argoproj.io/myapp.helm.image-name: image.tag
    argocd-image-updater.argoproj.io/myapp.helm.image-tag: image.tag

    # Optional: Write method (git, argocd)
    argocd-image-updater.argoproj.io/write-back-method: git
spec:
  # ... rest of application spec
```

**Update strategies:**
- `latest`: Always use the latest image (ignores tags)
- `semver:~1.0`: Semantic versioning constraint (e.g., 1.x.x)
- `digest`: Track by image digest (immutable)
- `name`: Track by tag name pattern

**Commit and push:**
```bash
git add gitops/argocd/apps/dev/my-app.yaml
git commit -m "feat: enable auto-updates for my-app"
git push
```

### Step 3.3: Verify Image Updater Configuration

**Check application is registered:**
```bash
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater --tail=100 | grep "my-app"
```

**Expected log output:**
```
time="..." level=info msg="Processing application my-app"
time="..." level=info msg="Setting new image to 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.5"
```

### Step 3.4: Test Automated Deployment

**Push a new image to ECR:**
```bash
# Build and tag image
docker build -t my-app:1.0.6 .
docker tag my-app:1.0.6 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.6

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.6
```

**Monitor Image Updater:**
```bash
# Watch logs for detection
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater -f
```

**Expected timeline:**
- T+0: Image pushed to ECR
- T+2min: Image Updater detects new image
- T+2min: Git commit created (if write-back enabled)
- T+3min: ArgoCD syncs application
- T+5min: Application running new version

**Verify deployment:**
```bash
# Check application status
kubectl get application my-app -n argocd

# Check pod image
kubectl get pods -n my-app-namespace -o jsonpath='{.items[0].spec.containers[0].image}'
# Should show: 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.6
```

### Step 3.5: Pause Image Updates (When Needed)

**Why:** Prevent automatic updates during maintenance windows or incident response.

**Method 1: Annotation (Per-Application)**
```bash
kubectl annotate application my-app -n argocd \
  argocd-image-updater.argoproj.io/image-list-
```

**Method 2: Scale Down Image Updater (Global)**
```bash
kubectl scale deployment argocd-image-updater -n argocd --replicas=0
```

**Resume updates:**
```bash
# Method 1: Restore annotation
kubectl annotate application my-app -n argocd \
  argocd-image-updater.argoproj.io/image-list=myapp=123456789.dkr.ecr.us-east-1.amazonaws.com/my-app

# Method 2: Scale up
kubectl scale deployment argocd-image-updater -n argocd --replicas=1
```

---

## 4. Troubleshooting

### Issue 4.1: Terraform Apply Fails

**Symptom:** `terraform apply` exits with error

**Common causes:**

1. **Helm timeout:**
   ```
   Error: timed out waiting for the condition
   ```

   **Solution:** Increase timeout in module
   ```hcl
   # modules/kubernetes_addons/argocd.tf
   timeout = 900  # Increase from 600
   ```

2. **kubeconfig access issue:**
   ```
   Error: Kubernetes cluster unreachable
   ```

   **Solution:** Verify cluster access
   ```bash
   kubectl get nodes
   # If fails, update kubeconfig
   aws eks update-kubeconfig --name <cluster-name> --region <region>
   ```

3. **Resource already exists:**
   ```
   Error: release argocd already exists
   ```

   **Solution:** Import existing release
   ```bash
   terraform import module.kubernetes_addons.helm_release.argocd argocd/argocd
   ```

### Issue 4.2: ArgoCD Applications Not Syncing

**Symptom:** Applications stuck in "OutOfSync" or "Progressing" state

**Diagnosis:**
```bash
# Check application status
kubectl get applications -n argocd

# Describe specific application
kubectl describe application <app-name> -n argocd

# Check ArgoCD logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=100
```

**Common causes:**

1. **Repository access issue:**
   ```
   Error: authentication required
   ```

   **Solution:** Verify ArgoCD can access Git repo
   ```bash
   kubectl get secret -n argocd
   # Ensure repo credentials exist
   ```

2. **Invalid manifest:**
   ```
   Error: error validating data
   ```

   **Solution:** Validate YAML syntax
   ```bash
   kubectl apply --dry-run=client -f gitops/argocd/apps/dev/<app>.yaml
   ```

3. **Namespace doesn't exist:**
   ```
   Error: namespace not found
   ```

   **Solution:** Add CreateNamespace=true
   ```yaml
   syncOptions:
     - CreateNamespace=true
   ```

### Issue 4.3: Image Updater Not Detecting New Images

**Symptom:** New ECR images pushed but not deployed

**Diagnosis:**
```bash
# Check Image Updater logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater --tail=200

# Check Image Updater pod status
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-image-updater

# Check service account annotation
kubectl get sa argocd-image-updater -n argocd -o yaml
```

**Common causes:**

1. **ECR authentication failure:**
   ```
   Error: failed to get credentials
   ```

   **Solution:** Verify IRSA role permissions
   ```bash
   # Check service account annotation
   kubectl get sa argocd-image-updater -n argocd -o jsonpath='{.metadata.annotations.eks\.amazonaws\.com/role-arn}'

   # Should show: arn:aws:iam::123456789:role/goldenpath-idp-image-updater-dev

   # Test IAM role
   aws sts assume-role --role-arn <role-arn> --role-session-name test
   ```

2. **Application annotation missing:**
   ```
   # No logs for application
   ```

   **Solution:** Add Image Updater annotations (see Step 3.2)

3. **Update strategy mismatch:**
   ```
   Info: no new image found
   ```

   **Solution:** Verify image tag matches strategy
   ```bash
   # If using semver:~1.0, ensure tags are semantic (1.0.x)
   # If using latest, ensure tag is "latest"
   ```

### Issue 4.4: Metrics Server Not Working

**Symptom:** `kubectl top` commands fail

**Diagnosis:**
```bash
# Check metrics-server pod
kubectl get pods -n kube-system -l app.kubernetes.io/name=metrics-server

# Check metrics-server logs
kubectl logs -n kube-system -l app.kubernetes.io/name=metrics-server --tail=50

# Test metrics API
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

**Common causes:**

1. **Kubelet TLS certificate issue:**
   ```
   Error: x509: certificate signed by unknown authority
   ```

   **Solution:** Already configured in module with:
   ```hcl
   args[0] = "--kubelet-insecure-tls"
   ```

2. **Conflicting manual installation:**
   ```
   Error: resource already exists
   ```

   **Solution:** Remove manual installation
   ```bash
   kubectl delete deployment metrics-server -n kube-system
   terraform apply
   ```

### Issue 4.5: Verification Script Shows Low Health Score

**Symptom:** `./bootstrap/verify-deployment.sh` shows <90% health

**Diagnosis:**
```bash
# Run verification in verbose mode
./bootstrap/verify-deployment.sh 2>&1 | tee verify.log

# Check failed components
cat verify.log | grep ""
```

**Solutions by component:**

- **Nodes not ready:** Wait 2-5 minutes for node provisioning
- **ArgoCD pods not ready:** Check ArgoCD logs for errors
- **Applications not synced:** See Issue 4.2
- **Metrics Server unavailable:** See Issue 4.4
- **Image Updater unhealthy:** See Issue 4.3

---

## 5. Updating Components

### Step 5.1: Update ArgoCD Version

**Why:** Apply security patches or new features.

```hcl
# envs/dev/terraform.tfvars
argocd_version = "5.55.0"  # Update version
```

```bash
terraform plan
terraform apply
```

**Note:** ArgoCD will perform rolling update. UI may be unavailable briefly.

### Step 5.2: Update Image Updater Version

```hcl
# envs/dev/terraform.tfvars
argocd_image_updater_version = "0.10.0"  # Update version
```

```bash
terraform apply
```

### Step 5.3: Update Metrics Server Version

```hcl
# envs/dev/terraform.tfvars
metrics_server_version = "3.12.0"  # Update version
```

```bash
terraform apply
```

### Step 5.4: Update AWS Load Balancer Controller

```hcl
# modules/kubernetes_addons/aws_lb_controller.tf
# Update chart version
version = "1.7.0"
```

```bash
terraform apply
```

---

## 6. Teardown and Cleanup

### Step 6.1: Graceful Teardown

**Why:** Remove all resources cleanly to avoid orphaned AWS resources.

```bash
cd envs/dev

# Run destroy
terraform destroy
```

**Duration:** ~15-20 minutes

**What gets deleted:**
1. Bootstrap applications (ArgoCD deletes these)
2. Metrics Server
3. AWS Load Balancer Controller (deletes managed LBs)
4. ArgoCD Image Updater
5. ArgoCD
6. Service accounts
7. IAM roles (Image Updater)
8. EKS cluster (if part of same Terraform state)

### Step 6.2: Verify Cleanup

**Check for orphaned AWS resources:**
```bash
# Check for orphaned load balancers
aws elbv2 describe-load-balancers --region <region> | grep <cluster-name>

# Check for orphaned ENIs
aws ec2 describe-network-interfaces --region <region> --filters "Name=tag:kubernetes.io/cluster/<cluster-name>,Values=owned"

# Check for orphaned IAM roles
aws iam list-roles | grep goldenpath-idp
```

**If orphans exist:**
```bash
# Delete load balancers
aws elbv2 delete-load-balancer --load-balancer-arn <arn>

# Delete ENIs (wait 5-10 min for auto-cleanup first)
aws ec2 delete-network-interface --network-interface-id <eni-id>
```

### Step 6.3: Clean Local State (Optional)

**Why:** Start fresh for next deployment.

```bash
# Remove Terraform state (use with caution!)
rm -rf .terraform terraform.tfstate*

# Remove kubeconfig entry
kubectl config delete-context arn:aws:eks:<region>:<account>:cluster/<cluster-name>
```

---

## 7. Emergency Procedures

### Emergency 7.1: Immediate Rollback

**Scenario:** Critical issue after deployment, need to revert quickly.

```bash
# Revert the refactor commit
git revert 45ef8902

# Apply rollback
cd envs/dev
terraform apply

# Restore manual metrics-server (if needed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Emergency 7.2: Disable Image Updater

**Scenario:** Image Updater deploying bad images.

**Immediate:**
```bash
# Scale down to zero
kubectl scale deployment argocd-image-updater -n argocd --replicas=0
```

**Permanent:**
```hcl
# envs/dev/terraform.tfvars
enable_image_updater_role = false
```

```bash
terraform apply
```

### Emergency 7.3: Force ArgoCD Sync Stop

**Scenario:** ArgoCD deploying broken application repeatedly.

```bash
# Disable auto-sync for specific application
kubectl patch application <app-name> -n argocd --type=json \
  -p='[{"op": "replace", "path": "/spec/syncPolicy/automated", "value": null}]'

# Or delete the application (stops sync, keeps resources)
kubectl delete application <app-name> -n argocd
```

### Emergency 7.4: Cluster Unresponsive

**Scenario:** Cannot access cluster via kubectl.

1. **Verify AWS access:**
   ```bash
   aws sts get-caller-identity
   ```

2. **Update kubeconfig:**
   ```bash
   aws eks update-kubeconfig --name <cluster-name> --region <region>
   ```

3. **Check cluster status:**
   ```bash
   aws eks describe-cluster --name <cluster-name> --region <region>
   ```

4. **If cluster is down:** Check AWS console for cluster events and node status.

---

## Quick Reference Commands

### Installation
```bash
cd envs/dev
terraform init
terraform plan -out=tfplan
terraform apply tfplan
./../../bootstrap/verify-deployment.sh
```

### Verification
```bash
kubectl get nodes
kubectl get pods -n argocd
kubectl get applications -n argocd
kubectl top nodes
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater --tail=50
```

### ArgoCD Access
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Username: admin
# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Teardown
```bash
cd envs/dev
terraform destroy
```

---

## Support and Escalation

For issues not covered in this runbook:

1. Check implementation guide: `EKS_SINGLE_BUILD_REFACTOR.md`
2. Review ADR-0148 for architectural context
3. Check changelog CL-0121 for known issues
4. Contact: platform-team
5. GitHub Issues: [Repository issues page]

---

## Document Maintenance

- **Owner:** platform-team
- **Review cadence:** 90 days
- **Last reviewed:** 2026-01-13
- **Next review:** 2026-04-13
