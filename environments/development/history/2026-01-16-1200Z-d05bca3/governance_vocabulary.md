---
type: governance-report
env: development
generated_at: 2026-01-16T12:00:45Z
source:
  branch: development
  sha: d05bca347b352b926640ed25c1e50aaa74cb447e
pipeline:
  workflow: Governance Registry Writer
  run_id: 21065920121
integrity:
  derived_only: true
---
# Governance Vocabulary & Allowed Values

This document is auto-generated from `schemas/metadata/enums.yaml`. These are the canonical values allowed in `metadata.yaml` sidecars.

## Domains
| Value | Description |
| :--- | :--- |
| `platform-core` | Allowed value |
| `delivery` | Allowed value |
| `identity` | Allowed value |
| `catalog` | Allowed value |
| `observability` | Allowed value |
| `governance` | Allowed value |
| `security` | Allowed value |
| `cost` | Allowed value |
| `governance-routing` | Allowed value |
| `platform-governance` | Allowed value |

## Components
| Value | Description |
| :--- | :--- |
| `infra` | Allowed value |
| `ci` | Allowed value |
| `gitops` | Allowed value |
| `argo` | Allowed value |
| `backstage` | Allowed value |
| `kong` | Allowed value |
| `agents` | Allowed value |
| `metadata-graph` | Allowed value |
| `policies` | Allowed value |
| `ecr` | Allowed value |
| `github` | Allowed value |
| `keycloak` | Allowed value |

## Adr Status
| Value | Description |
| :--- | :--- |
| `proposed` | Allowed value |
| `accepted` | Allowed value |
| `active` | Allowed value |
| `deprecated` | Allowed value |
| `superseded` | Allowed value |

## Owners
| Value | Description |
| :--- | :--- |
| `platform-team` | Allowed value |
| `security-team` | Allowed value |
| `operations-team` | Allowed value |
| `sre-team` | Allowed value |
| `unknown` | Allowed value |
| `app-team` | Allowed value |
| `database-team` | Allowed value |

## Lifecycle
| Value | Description |
| :--- | :--- |
| `draft` | Allowed value |
| `active` | Allowed value |
| `deprecated` | Allowed value |
| `archived` | Allowed value |
| `released` | Allowed value |
| `planned` | Allowed value |
| `approved` | Allowed value |
| `accepted` | Allowed value |
| `superseded` | Allowed value |
| `proposed` | Allowed value |

## Status
| Value | Description |
| :--- | :--- |
| `proposed` | Allowed value |
| `accepted` | Allowed value |
| `active` | Allowed value |
| `deprecated` | Allowed value |
| `superseded` | Allowed value |
| `approved` | Allowed value |
| `planned` | Allowed value |
| `released` | Allowed value |

## Artifact Type
| Value | Description |
| :--- | :--- |
| `adr` | Allowed value |
| `policy` | Allowed value |
| `governance` | Allowed value |
| `contract` | Allowed value |
| `runbook` | Allowed value |
| `changelog` | Allowed value |
| `catalog` | Allowed value |
| `template` | Allowed value |
| `report` | Allowed value |
| `documentation` | Allowed value |
| `guide` | Allowed value |
| `strategy` | Allowed value |
| `runlog` | Allowed value |
| `operational-log` | Allowed value |
| `implementation-plan` | Allowed value |

## Adr Categories
| Value | Description |
| :--- | :--- |
| `platform` | Allowed value |
| `delivery` | Allowed value |
| `identity` | Allowed value |
| `catalog` | Allowed value |
| `observability` | Allowed value |
| `governance` | Allowed value |
| `security` | Allowed value |
| `finance` | Allowed value |
| `runtime` | Allowed value |
| `architecture` | Allowed value |
| `infrastructure` | Allowed value |
| `onboarding` | Allowed value |
| `compliance` | Allowed value |
| `changelog` | Allowed value |
| `testing` | Allowed value |
| `app-team` | Allowed value |
| `runbooks` | Allowed value |

## Risk Profile Coupling Risk
| Value | Description |
| :--- | :--- |
| `low` | Allowed value |
| `medium` | Allowed value |
| `high` | Allowed value |

## Rollback Strategy
| Value | Description |
| :--- | :--- |
| `git-revert` | Allowed value |
| `redeploy` | Allowed value |
| `manual` | Allowed value |

## Observability Tier
| Value | Description |
| :--- | :--- |
| `bronze` | Allowed value |
| `silver` | Allowed value |
| `gold` | Allowed value |

## Risk Profile Production Impact
| Value | Description |
| :--- | :--- |
| `none` | Allowed value |
| `low` | Allowed value |
| `medium` | Allowed value |
| `high` | Allowed value |

## Risk Profile Security Risk
| Value | Description |
| :--- | :--- |
| `none` | Allowed value |
| `low` | Allowed value |
| `medium` | Allowed value |
| `high` | Allowed value |
| `access` | Allowed value |

## Environments
| Value | Description |
| :--- | :--- |
| `dev` | Allowed value |
| `test` | Allowed value |
| `staging` | Allowed value |
| `prod` | Allowed value |
| `ephemeral` | Allowed value |

## Approval Tiers
| Value | Description |
| :--- | :--- |
| `self-serve` | Allowed value |
| `platform-approval` | Allowed value |
| `security-approval` | Allowed value |
| `platform-and-security` | Allowed value |
| `change-advisory` | Allowed value |

## Reviewer Groups
| Value | Description |
| :--- | :--- |
| `platform-team` | Allowed value |
| `security-team` | Allowed value |
| `operations-team` | Allowed value |
| `sre-team` | Allowed value |
| `unknown` | Allowed value |
| `app-team` | Allowed value |
| `database-team` | Allowed value |

## Service Classes
| Value | Description |
| :--- | :--- |
| `kubernetes-clusters` | Allowed value |
| `container-registries` | Allowed value |
| `storage-s3` | Allowed value |
| `storage-efs` | Allowed value |
| `storage-ebs` | Allowed value |
| `databases-dynamodb` | Allowed value |
| `databases-rds` | Allowed value |
| `networking-vpc` | Allowed value |
| `compute-vms` | Allowed value |
| `secrets-management` | Allowed value |

## Vq Class
| Value | Description |
| :--- | :--- |
| `🔴 HV/HQ` | Allowed value |
| `🟡 HV/LQ` | Allowed value |
| `🔵 MV/HQ` | Allowed value |
| `⚫ LV/LQ` | Allowed value |

## User Types
| Value | Description |
| :--- | :--- |
| `regular-user` | Allowed value |
| `service-account` | Allowed value |
| `system-admin` | Allowed value |

## System Types
| Value | Description |
| :--- | :--- |
| `service-ecosystem` | Allowed value |
| `data-pipeline` | Allowed value |
| `platform-infrastructure` | Allowed value |

## Backstage Kinds
| Value | Description |
| :--- | :--- |
| `Component` | Allowed value |
| `System` | Allowed value |
| `API` | Allowed value |
| `Resource` | Allowed value |
| `Location` | Allowed value |
| `Template` | Allowed value |
| `Domain` | Allowed value |
| `Group` | Allowed value |
| `User` | Allowed value |

## Resource Types
| Value | Description |
| :--- | :--- |
| `cloud-storage` | Allowed value |
| `compute-instance` | Allowed value |
| `database-cluster` | Allowed value |
| `container-registry` | Allowed value |

## Api Types
| Value | Description |
| :--- | :--- |
| `openapi` | Allowed value |
| `graphql` | Allowed value |
| `grpc` | Allowed value |
| `asyncapi` | Allowed value |

## Ai Authority Tier
| Value | Description |
| :--- | :--- |
| `tier0-read-reason` | Allowed value |
| `tier1-write-isolated` | Allowed value |
| `tier2-safe-execute` | Allowed value |
| `tier3-human-only` | Allowed value |

## Ai Delegation Mode
| Value | Description |
| :--- | :--- |
| `full-delegation` | Allowed value |
| `copilot` | Allowed value |
| `human-only` | Allowed value |

## Ai Execution Role
| Value | Description |
| :--- | :--- |
| `junior-engineer` | Allowed value |
| `refactorer` | Allowed value |
| `auditor` | Allowed value |
| `automation-agent` | Allowed value |
| `advisor` | Allowed value |
| `triager` | Allowed value |
| `documentarian` | Allowed value |
| `compliance-checker` | Allowed value |
| `release-scribe` | Allowed value |
| `threat-modeler` | Allowed value |

## Ai Context Tier
| Value | Description |
| :--- | :--- |
| `execution` | Allowed value |
| `refinement` | Allowed value |
| `judgment` | Allowed value |

## Ai Task Domain
| Value | Description |
| :--- | :--- |
| `docs` | Allowed value |
| `code` | Allowed value |
| `infra` | Allowed value |
| `governance` | Allowed value |
| `security` | Allowed value |
| `observability` | Allowed value |
| `ci-cd` | Allowed value |

## Ai Validation Level
| Value | Description |
| :--- | :--- |
| `not-run` | Allowed value |
| `local-checks` | Allowed value |
| `ci-green` | Allowed value |
| `prod-verified` | Allowed value |

## Value Intent
| Value | Description |
| :--- | :--- |
| `cost_reduction` | Allowed value |
| `risk_reduction` | Allowed value |
| `speed_enablement` | Allowed value |
| `reliability` | Allowed value |
| `compliance` | Allowed value |
| `developer_experience` | Allowed value |
| `revenue_enablement` | Allowed value |

## Automation Confidence
| Value | Description |
| :--- | :--- |
| `manual` | Allowed value |
| `assisted` | Allowed value |
| `supervised` | Allowed value |
| `autonomous` | Allowed value |

## Decision Weight
| Value | Description |
| :--- | :--- |
| `reversible` | Allowed value |
| `costly_to_reverse` | Allowed value |
| `foundational` | Allowed value |

## Security
| Value | Description |
| :--- | :--- |
| `secret_types` | Allowed value |
| `risk_tiers` | Allowed value |
| `rotation_classes` | Allowed value |
| `lifecycle_status` | Allowed value |

## Rds
| Value | Description |
| :--- | :--- |
| `instance_sizes` | Allowed value |
| `engines` | Allowed value |
| `request_status` | Allowed value |

