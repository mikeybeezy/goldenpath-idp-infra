---
id: RB-0030-break-glass-protocol
title: 'RB-0030: Break-Glass Protocol for Infrastructure'
type: runbook
category: runbooks
---

# RB-0030: Break-Glass Protocol for Infrastructure

## Metadata
*   **ID**: RB-0030
*   **Title**: Break-Glass Protocol for Terraform
*   **Type**: Operational
*   **Status**: Active
*   **Owner**: Platform Team

## Overview
The Golden Path platform requires all infrastructure changes to be initiated via the `Makefile` (e.g., `make deploy`). This ensures telemetry capture, policy validation, and standardized configuration.

However, in **Emergency Scenarios** (e.g., CI is down, Makefile logic is broken, or deep debugging is required), engineers may need to run raw Terraform commands. This Runbook details the "Break-Glass" procedure.

## Triggers
*   **Severity 1 Incident**: Production outage requiring immediate undocumented patching.
*   **CI Failure**: GitHub Actions is unavailable.
*   **Development**: Advanced debugging of Terraform state or provider issues where the Makefile abstraction hides necessary details.

## Procedure

### 1. The Guardrail
If you attempt to run `terraform apply` directly, you will see this error:

```text
Error: local-exec provisioner error
...
message: "❌ ERROR: Direct terraform apply is FORBIDDEN. Use `make deploy` or see RB-0030."
```

### 2. Breaking Glass
To bypass this check, append the `break_glass` variable to your command.

**Command**:
```bash
# Example: Surgical apply during an outage
terraform -chdir=envs/dev apply -var="break_glass=true" -target=module.critical_fix
```

### 3. Reporting
Usage of the break-glass protocol implies that **Telemetry is LOST** for that run.
*   **Requirement**: You MUST manually log your action in the `#platform-ops` channel or the Incident Ticket.
*   **Post-Mortem**: If a Break-Glass was used to fix a production issue, the fix MUST be backported to the standard `main.tf` and `Makefile` workflow immediately.
