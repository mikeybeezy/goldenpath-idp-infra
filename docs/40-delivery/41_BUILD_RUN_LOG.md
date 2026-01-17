---
id: 41_BUILD_RUN_LOG
title: Build Run Log (Living)
type: documentation
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - 17_BUILD_RUN_FLAGS
  - 26_AI_AGENT_PROTOCOLS
  - DOCS_BUILD-RUN-LOGS_README
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# Build Run Log (Living)

Doc contract:

- Purpose: Record build, bootstrap, and teardown run summaries with links for deeper detail.
- Owner: platform
- Status: living
- Review cadence: 30d
- Related: docs/40-delivery/17_BUILD_RUN_FLAGS.md, docs/build-timings.csv

This log is a human-readable companion to `docs/build-timings.csv` and the
per-run entries in `docs/build-run-logs/`.
Use it to capture the context that does not fit in the CSV (commit SHA,
workflow run links, scripts, and observations).

## Best-practice capture (fast scan + deep dive)

- Keep a short summary table for scanning; include date, Build ID, SHA, status,
  and durations.
- Link to the GitHub Actions run and the `logs/build-timings/*.log` artifacts.
- Record the exact bootstrap script version (v1/v2/v3) and workflow used.
- Copy durations from `docs/build-timings.csv` to avoid manual timing errors.
- Add a short "Ad hoc notes/observations" line for anomalies or context.

If more detail is needed, use the workflow run link and log file paths.

## Summary table

| Date (UTC) | Build ID | SHA | Build (s) | Bootstrap (s) | Teardown (s) | Status | Entry | Run URL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | 02-01-26-06 | cd190568def5677508a5804e82e73c3f1a3802b2 (build) / 4be3d33a7118b86457727b8cfd026da3f8deea38 (bootstrap) | 905 | 215 | - | success | docs/build-run-logs/BR-0001-02-01-26-06.md | build: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20662142526> / bootstrap: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20664240754> |
| 2026-01-03 | 03-01-26-02 | 2e60175f2215f5883bfd3c5afc7a1154e1b7f73e | 938 | - | - | failure | docs/build-run-logs/BR-0003-03-01-26-02.md | build: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20683109446> |
| 2026-01-03 | 11-11-11-11 | 2e60175f2215f5883bfd3c5afc7a1154e1b7f73e | 2576 | - | - | failure | docs/build-run-logs/BR-0004-11-11-11-11.md | build: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20683824002> |
| 2026-01-03 | 03-01-26-02 | 2e60175f2215f5883bfd3c5afc7a1154e1b7f73e | - | - | 451 | success | docs/build-run-logs/TD-0003-03-01-26-02.md | teardown: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20684378611> |
| 2026-01-03 | 11-11-11-11 | 2e60175f2215f5883bfd3c5afc7a1154e1b7f73e | - | - | 493 | success | docs/build-run-logs/TD-0004-11-11-11-11.md | teardown: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20684384284> |

## Entry template

```
Date (UTC):
Build ID:
Branch/Commit:
Workflow:
Jobs:
Workflow run URL (build):
Workflow run URL (bootstrap):
Scripts:
Config source:
Storage add-ons:
IRSA strategy:
Build duration (seconds):
Bootstrap duration (seconds):
Teardown duration (seconds):
Outcome:
Artifacts:
Ad hoc notes/observations:
```

## Entry: 2026-01-02 (BR-0001-02-01-26-06)

Detailed entry: docs/build-run-logs/BR-0001-02-01-26-06.md

Teardown URL: <https://github.com/mikeybeezy/goldenpath-idp-infra/actions/runs/20665012721/job/59335320116>

SHA: 4be3d33a7118b86457727b8cfd026da3f8deea38

Script Used = V2

Notes: Clean Teardown,
AWS orphans:
TG = several but could have accumulated across several builds, Target groups but we can try and capture them because use tags KEY= elbv2.k8s.aws/cluster VALUE=goldenpath-dev-eks-30-12-25-01
0 = ENI
0 = VPC
0 = NAT
0 = SG
0 = LB
0 = NG
0 = EC2
0 = SUBNET
0 = RT
0 = Volumes Need more data
0 = SNAP SHOTS need more data
0 = IGW
0 = IAM roles
0 = EKS
