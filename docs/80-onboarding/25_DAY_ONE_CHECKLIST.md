---
id: 25_DAY_ONE_CHECKLIST
title: Day-One Onboarding Checklist
type: runbook
relates_to:
  - 00_DOC_INDEX
  - 23_NEW_JOINERS
  - 24_PR_GATES
status: active
version: '1.0'
supported_until: 2028-01-01
breaking_change: false
---

# Day-One Onboarding Checklist

Doc contract:

- Purpose: Provide the minimum inputs and artifacts to get productive fast.
- Owner: platform
- Status: living
- Review cadence: 90d
- Related: docs/80-onboarding/23_NEW_JOINERS.md, docs/80-onboarding/24_PR_GATES.md, docs/90-doc-system/00_DOC_INDEX.md

This checklist is the shortest path to productive work. It focuses on inputs,
documents, and artifacts you need before you start making changes.

## Inputs to request

- Access scope (AWS roles, regions, and Terraform backend details).
- GitHub access to Actions logs and required secrets (or a list of them).
- Current priority list and expected outcomes for the week.
- One known-good run and one known-bad run (URLs + SHAs + build_id).
- Primary communication channel for the platform team.
- **Critical**: Create PR permissions enabled for Actions (see [GITHUB_WORKFLOW_PERMISSIONS.md](GITHUB_WORKFLOW_PERMISSIONS.md)).

## Read first (fast context)

- docs/adrs/01_adr_index.md
- docs/product/VQ_PRINCIPLES.md (**Read this first**)
- docs/product/VQ_TAGGING_GUIDE.md
- docs/80-onboarding/23_NEW_JOINERS.md
- docs/80-onboarding/24_PR_GATES.md
- docs/40-delivery/38_BRANCHING_STRATEGY.md
- docs/40-delivery/12_GITOPS_AND_CICD.md
- docs/70-operations/32_TERRAFORM_STATE_AND_LOCKING.md
- docs/90-doc-system/00_DOC_INDEX.md

## Operational touchpoints

- Workflows: `.github/workflows/ci-bootstrap.yml`
- Bootstrap scripts: `bootstrap/`
- Terraform entry points: `Makefile`, `envs/dev/`, `modules/`
- Pre-commit rules: `.pre-commit-config.yaml`

## Starter artifacts to have on hand

- A sanitized `terraform.tfvars` example or template.
- A recent build/boot/teardown log entry:
  - docs/40-delivery/41_BUILD_RUN_LOG.md
  - docs/build-run-logs/

## First-day validation steps

1. Initialize your environment: `bin/governance setup`.
2. Confirm branch flow: create a feature branch from `development`.
3. Open a draft PR into `development` to validate guardrails and labels (use `.github/pull_request_template.md`).
4. Capture any missing access or missing config as issues.
