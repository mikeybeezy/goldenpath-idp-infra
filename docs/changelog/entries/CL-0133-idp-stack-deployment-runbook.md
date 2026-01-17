---
id: CL-0133-idp-stack-deployment-runbook
title: IDP Stack Deployment Runbook (RB-0031)
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - backstage
  - keycloak
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to:
  - ADR-0159-backstage-catalog-registry-sync
  - ADR-0160
  - CL-0133-idp-stack-deployment-runbook
  - CL-0135-kong-ingress-for-tooling-apps
  - RB-0031-idp-stack-deployment
  - agent_session_summary
supersedes: []
superseded_by: []
tags:
  - runbook
  - backstage
  - keycloak
  - idp
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 4.0
supported_until: 2028-01-16
version: '1.0'
breaking_change: false
---

## CL-0133: IDP Stack Deployment Runbook

**Type**: Documentation
**Component**: Operations / Runbooks
**Date**: 2026-01-16
**Related**: RB-0031, ADR-0159, ADR-0160

## Summary

Added comprehensive runbook RB-0031 for deploying the IDP core stack (Keycloak and Backstage) on EKS clusters.

## Changes

### New Runbook: RB-0031-idp-stack-deployment.md

Six-phase deployment guide covering:

1. **Phase 1: ECR Repository and Image Preparation**
   - ECR repository creation
   - AMD64 image pulling (critical for Apple Silicon users)
   - Bitnami Keycloak image requirements

2. **Phase 2: RDS User Provisioning**
   - Manual PostgreSQL user creation via psql pod
   - Database and privilege setup for Keycloak and Backstage

3. **Phase 3: External Secrets Verification**
   - ClusterSecretStore validation
   - ExternalSecret sync status checks

4. **Phase 3.5: GitHub Token Configuration (NEW)**
   - PAT scope requirements (classic and fine-grained)
   - AWS Secrets Manager update procedure
   - ExternalSecret sync and verification

5. **Phase 4-5: Keycloak and Backstage Deployment**
   - ArgoCD application verification
   - Common issues and troubleshooting

6. **Phase 6: Verification Checklist**
   - Pod health checks
   - Service endpoint validation

### Key Highlights

- Documents the **pre-baked vs custom images** distinction
- Includes **troubleshooting decision tree** for common failures
- Covers **ArgoCD multi-source pattern** for Backstage values
- Adds **GitHub token setup** as bootstrap prerequisite

## Impact

- Reduces mean time to deploy IDP stack from hours to minutes
- Provides single source of truth for IDP deployment procedures
- Eliminates tribal knowledge dependency for new platform engineers

## References

- Runbook: `docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md`
- Related ADR: ADR-0159 (Backstage Catalog Registry Sync)
- Related ADR: ADR-0160 (RDS Optional Toggle Integration)
