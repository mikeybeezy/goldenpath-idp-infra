---
id: 10_REPO_DECOMMISSIONING
title: Repo Decommissioning Runbook
type: runbook
category: runbooks
version: 1.0
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: high
  security_risk: access
  coupling_risk: high
reliability:
  rollback_strategy: not-applicable
  observability_tier: gold
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
  - TEARDOWN_README
  - ORPHAN_CLEANUP
  - 01_LIFECYCLE_POLICY
---

# Repo Decommissioning Runbook

Purpose: safely archive or delete a repo and its associated resources with an
auditable trail.

## Inputs

- Repo: `org/name`
- Owner team
- Deprecation decision (ADR or ticket)
- Environments and lifecycle (ephemeral/persistent)

## Preconditions

- Deprecation decision is approved and linked.
- Owner team acknowledges the decommission plan.

## Steps

1) Mark deprecated
- Update `catalog-info.yaml` lifecycle to `deprecated`.
- Add a note to README pointing to the replacement service (if any).

2) Freeze changes
- Disable CI triggers if needed (or block merges via branch protection).
- Communicate a change freeze to the owning team.

3) Remove runtime resources
- Remove GitOps app definitions (Argo CD) for the service.
- Run teardown for infra resources tied to the service.
- Confirm no cloud resources remain (tag scans or runbooks).

4) Remove secrets and tokens
- Delete repo secrets:
  - `gh secret list -R org/name`
  - `gh secret delete <secret> -R org/name`

5) Archive or delete repo
- Archive (preferred for retention):
  - `gh repo archive org/name`
- Delete (if policy allows):
  - `gh repo delete org/name --confirm`

6) Record a tombstone
- Record: repo name, owner, date, approver, teardown evidence.
- Attach links to workflow runs and teardown logs.

## Evidence checklist

- [ ] Deprecation decision link
- [ ] Teardown run link(s)
- [ ] Secrets removal confirmation
- [ ] Archive/delete confirmation

## Tombstone template

```
Repo: org/name
Owner: team
Date: YYYY-MM-DD
Decision: <ADR or ticket>
Teardown: <workflow/runbook links>
Approver: <name>
Notes: <optional>
```
