---
id: GOVERNANCE_VOCABULARY
title: Governance Vocabulary & Allowed Values
type: policy
domain: platform-core
applies_to: []
owner: platform-team
lifecycle: active
exempt: false
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
schema_version: 1
relates_to: []
supersedes: []
superseded_by: []
tags: []
inheritance: {}
value_quantification:
  vq_class: ⚫ LV/LQ
  impact_tier: low
  potential_savings_hours: 0.0
category: platform
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
