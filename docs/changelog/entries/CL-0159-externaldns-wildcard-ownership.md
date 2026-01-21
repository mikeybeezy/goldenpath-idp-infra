---
id: CL-0159
title: ExternalDNS ownership for wildcard DNS records
type: changelog
status: active
owner: platform-team
domain: platform-core
applies_to:
  - gitops/argocd/apps/*/external-dns.yaml
  - gitops/helm/external-dns/
  - gitops/helm/kong/values/*.yaml
  - modules/aws_iam/
  - envs/*/main.tf
  - envs/*/variables.tf
  - envs/dev/terraform.tfvars
lifecycle: active
exempt: false
risk_profile:
  production_impact: medium
  security_risk: low
  coupling_risk: medium
schema_version: 1
relates_to:
  - ADR-0175-externaldns-wildcard-ownership
  - PRD-0002-route53-externaldns
  - session_capture/2026-01-20-persistent-cluster-deployment
supersedes: []
superseded_by: []
tags:
  - route53
  - dns
  - external-dns
  - kong
  - gitops
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: medium
  potential_savings_hours: 0.0
supported_until: 2028-01-21
date: 2026-01-21
author: platform-team
---

# ExternalDNS ownership for wildcard DNS records

## Summary

ExternalDNS now owns wildcard DNS records per environment so `*.{env}.goldenpathidp.io`
tracks Kong LoadBalancer changes without manual Terraform re-applies.

## What changed

- Added ExternalDNS Helm values and Argo CD applications for all environments.
- Annotated Kong proxy Services with wildcard hostnames.
- Added ExternalDNS IRSA role + service account wiring in Terraform.
- Disabled Terraform wildcard record creation by default.

## Notes

- Ensure `iam_config.enable_external_dns_role = true` and
  `route53_config.zone_id` is set when enabling ExternalDNS for an env.
- Terraform-managed wildcard records should remain disabled to avoid conflicts.
