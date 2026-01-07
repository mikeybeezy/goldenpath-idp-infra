---
id: request-registry
title: 'App Team Runbook: Request ECR Registry'
type: runbook
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0092
  - ADR-0096
  - ADR-0100
  - CL-0055
  - CL-0061
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: runbooks
status: active
version: '1.0'
dependencies:
  - github-actions
  - aws-ecr
supported_until: 2028-01-05
breaking_change: false
---

# App Team Runbook: Request ECR Registry

**Audience:** Application Teams
**Purpose:** How to request a new ECR container registry

---

## Quick Start

1. Go to [GitHub Actions → Create ECR Registry](../../.github/workflows/create-ecr-registry.yml)
2. Click "Run workflow"
3. Fill out the form
4. Submit
5. Review the PR
6. Wait for platform team approval
7. Registry created automatically!

---

## Risk Levels

**Choose the appropriate risk level for your application:**

### 🟢 Low Risk (Development/Testing)

**Use for:**
- Development environments
- Experiments and prototypes
- Testing and QA
- Non-production workloads

**You get:**
- ✅ AES256 encryption (AWS-managed)
- ✅ Mutable tags (can overwrite `latest`)
- ✅ 20 image retention
- ✅ Standard scanning on push

**Example:** `my-app-dev`, `experiment-feature-x`

---

### 🟡 Medium Risk (Staging/Internal)

**Use for:**
- Staging environments
- Internal tools
- Non-critical production services
- Backend services with no direct customer data

**You get:**
- ✅ AES256 encryption (AWS-managed)
- ✅ Mutable tags (can overwrite `latest`)
- ✅ 30 image retention
- ✅ Standard scanning on push

**Example:** `my-app-staging`, `internal-dashboard`

---

### High Risk (Production/Sensitive)

**Use for:**
- Production customer-facing services
- Services handling sensitive data
- PCI/HIPAA compliance workloads
- Critical infrastructure

**You get:**
- ✅ KMS encryption (customer-managed keys)
- ✅ Immutable tags (cannot overwrite - prevents accidents)
- ✅ 50 image retention
- ✅ Enhanced scanning on push

**Example:** `payment-api`, `customer-portal`, `auth-service`

---

## How to Request

### Step 1: Prepare Information

You'll need:
- **Registry name:** Lowercase with hyphens (e.g., `wordpress-platform`)
- **Owner:** Your team name (e.g., `app-team-wordpress`)
- **Risk level:** Choose from low/medium/high (see above)
- **Environment:** dev/test/staging/prod

> [!NOTE]
> The **Registry ID** is now **auto-generated** from the registry name. You no longer need to provide it manually.

### Step 2: Run the Workflow

1. Go to **Actions** tab in GitHub
2. Select **"Create ECR Registry"** workflow
3. Click **"Run workflow"**
4. Fill out the form:
   ```
   Environment: dev
   Registry name: wordpress-platform
   Owner: app-team-wordpress
   Risk: high
   ```
   > The ID (`REGISTRY_WORDPRESS_PLATFORM`) is calculated automatically.
5. Click **"Run workflow"**

### Step 3: Review the PR

The workflow creates a PR showing:
- ✅ What registry will be created
- ✅ What security controls will be applied
- ✅ What changes will be made
- ✅ **Day Zero Guidance** links to push images immediately
- ✅ **Auto-updated catalog documentation**

**Review the PR carefully** - it shows exactly what you're getting!

### Step 4: Wait for Approval

Platform team will:
- Review the request
- Verify risk level is appropriate
- Approve and merge

### Step 5: Registry Created

After merge:
- Terraform automatically provisions the registry
- You'll be notified when ready
- IAM permissions will be granted

---

## What You Get

After approval, you'll have:
- ✅ ECR registry in AWS
- ✅ Automatic security controls (based on risk)
- ✅ Image scanning enabled
- ✅ Lifecycle policy configured
- ✅ IAM permissions for your team

---

## Next Steps

After your registry is created:
1. **Push images:** See [Push Image Guide](./push-image-guide.md)
2. **Pull images:** See [Pull Image Guide](./pull-image-guide.md)
3. **Fix CVEs:** See [Fix CVE Guide](./fix-cve-guide.md)

---

## FAQ

**Q: How long does it take?**
A: Usually 1-2 hours (depends on platform team availability)

**Q: Can I change the risk level later?**
A: Yes, create another PR to update the catalog

**Q: What if I chose the wrong risk level?**
A: Platform team will catch it during review and suggest the correct level

**Q: Can I have multiple registries?**
A: Yes! One per product/service is recommended

**Q: What's the naming convention?**
A: `product-name` or `service-name` (lowercase with hyphens)

---

## Troubleshooting

**Workflow fails with validation error:**
- Check registry name is lowercase with hyphens only
- Check ID is uppercase with underscores only
- Check owner starts with `app-team-`

**PR not created:**
- Check GitHub Actions logs
- Contact #platform-team on Slack

---

## Support

**Questions?** Contact #platform-team on Slack

**Related Documentation:**
- [ADR-0092: ECR Registry Product Strategy](../adrs/ADR-0092-ecr-registry-product-strategy.md)
- [ADR-0096: Risk-Based ECR Controls](../adrs/ADR-0096-risk-based-ecr-controls.md)
