---
id: CL-0145
title: Persistent Cluster Teardown Runbook
type: changelog
status: active
owner: platform-team
date: 2026-01-17
author: platform-team
category: runbooks
relates_to:
  - RB-0033-persistent-cluster-teardown
  - 32_TERRAFORM_STATE_AND_LOCKING
  - ADR-0040-platform-lifecycle-aware-state-keys
---

# CL-0145: Persistent Cluster Teardown Runbook

## Summary

Documented the teardown process for persistent clusters that use the root state
key (`envs/<env>/terraform.tfstate`). This closes the operational gap where
ephemeral and persistent teardown paths diverge.

## Changes

### Added

- Runbook: `docs/70-operations/runbooks/RB-0033-persistent-cluster-teardown.md`
- Runbooks index entry in `docs/70-operations/runbooks/README.md`

## Notes

- Persistent teardown requires `CONFIRM_DESTROY=yes`.
- Ephemeral builds still use `make teardown` with `BUILD_ID`.
