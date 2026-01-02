# Build Run Log (Living)

Doc contract:
- Purpose: Record build, bootstrap, and teardown run summaries with links for deeper detail.
- Owner: platform
- Status: living
- Review cadence: 30d
- Related: docs/40-delivery/17_BUILD_RUN_FLAGS.md, docs/build-timings.csv

This log is a human-readable companion to `docs/build-timings.csv`.
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

| Date (UTC) | Build ID | SHA | Build (s) | Bootstrap (s) | Teardown (s) | Status | Run URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | 02-01-26-06 | cd190568def5677508a5804e82e73c3f1a3802b2 | <fill> | <fill> | <fill> | success | <link> |

## Entry template

```
Date (UTC):
Build ID:
Branch/Commit:
Workflow:
Jobs:
Workflow run URL:
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

## Entry: 2026-01-02 (draft)

Date (UTC): 2026-01-02
Build ID: 02-01-26-06
Branch/Commit: development @ cd190568def5677508a5804e82e73c3f1a3802b2
Workflow: Bootstrap - CI Bootstrap (Stub)
Jobs: Dev apply (build) -> Bootstrap (v3)
Workflow run URL: <link>
Scripts: bootstrap/10_bootstrap/goldenpath-idp-bootstrap-v3.sh
Config source: envs/dev/terraform.tfvars
Storage add-ons: enabled (EBS/EFS/snapshot-controller)
IRSA strategy: validated existing service accounts; no Terraform apply in Stage 3B
Build duration (seconds): <from docs/build-timings.csv>
Bootstrap duration (seconds): <from docs/build-timings.csv>
Teardown duration (seconds): <if run>
Outcome: build completed with AWS + Kubernetes resources
Artifacts: logs/build-timings/<build-log>.log; logs/build-timings/<bootstrap-log>.log
Ad hoc notes/observations: <fill>
