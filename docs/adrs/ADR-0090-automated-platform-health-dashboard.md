---
id: ADR-0090-automated-platform-health-dashboard
title: 'ADR-0090: Automated Platform Health Dashboard'
type: adr
status: active
lifecycle: active
version: '1.0'
supported_until: 2027-01-03
breaking_change: false
---

# ADR-0090: Automated Platform Health Dashboard

## Status
Accepted

## Context
As the GoldenPath IDP grows, manual auditing of metadata compliance, risk profiles, and "Dark Infrastructure" becomes unsustainable. We have a reporter script (`platform_health.py`), but its output was ephemeral and only visible in terminal logs or CI artifacts. To provide transparency and operational intelligence, we need a persistent, automated dashboard.

## Decision
We will implement an automated "Platform Health Dashboard" that is programmatically generated and persisted to the repository root.

1. **Persistence**: `platform_health.py` will be updated to write its output directly to `PLATFORM_HEALTH.md` in the repository root.
2. **Standard Schema**: The generated `PLATFORM_HEALTH.md` will itself carry the mandatory platform metadata schema to ensure it is auditable.
3. **Automated Updates**: A GitHub Action (`quality-platform-health.yaml`) will run on every push to `development` and daily at midnight.
4. **Git Persistence**: The GitHub Action will use `git-auto-commit-action` to commit the updated dashboard back to the repository, ensuring a historical record of platform health.

## Consequences
- **Positive**: High visibility of "Injection Coverage" and "Dark Infrastructure" gaps for leadership.
- **Positive**: Zero manual overhead for maintaining the health dashboard.
- **Positive**: Enables Backstage and other portals to consume the health state directly from the repository.
- **Neutral**: Adds automated "chore" commits to the repository history.
