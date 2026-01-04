---
id: TD-TEMPLATE
title: Teardown Log Template
type: template
owner: platform-team
status: active
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: not-applicable
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to: [BR-TEMPLATE]
---

# TD-XXXX-<build-id>

Date (UTC): YYYY-MM-DD
Build ID: <build-id>
Branch/Commit: <branch> @ <sha>
Workflow: CI Teardown
Workflow run URL: <url>

## Configuration
Script: <script-version>
Flags: <flags>

## Metrics
Teardown duration (seconds): <seconds>
Outcome: <Outcome>

## Orphan Analysis (Resource Counts)
AWS orphans:
- Target groups: <count>
- ENI: <count>
- VPC: <count>
- NAT: <count>
- SG: <count>
- LB: <count>
- NG: <count>
- EC2: <count>
- SUBNET: <count>
- RT: <count>
- Volumes: <count>
- Snapshots: <count>
- IGW: <count>
- IAM roles: <count>
- EKS: <count>

## Ad Hoc Notes
Ad hoc notes/observations: <notes>

## Analysis & Optimization Opportunities
1. **Finding:** <finding>
   - *Impact:* <impact>
   - *Action:* <action>
