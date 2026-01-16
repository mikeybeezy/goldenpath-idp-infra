---
id: CONTRACT_DRIVEN_ARCHITECTURE
title: Contract-Driven Architecture for Self-Service Requests
type: how-it-works
owner: platform-team
status: active
relates_to:
  - schemas/requests/rds.schema.yaml
  - scripts/rds_request_parser.py
  - scripts/secret_request_parser.py
---

## Contract-Driven Architecture for Self-Service Requests

This document explains the contract-driven self-service architecture used by Golden Path IDP, including the "thin template" pattern where parsers generate all artifacts.

## Architecture Philosophy

```text
Schema = The Contract (strict, machine-readable, single source of truth)
Backstage = Thin UI (collect inputs, validate, open PR - nothing else)
Parser = The Brain (reads contracts, generates all artifacts)
Terraform = Dumb Executor (no logic, just applies what parser generates)
```

## Current Request Flow

```text
User fills Backstage form
       |
       v
Backstage dispatches workflow OR opens PR directly
       |
       v
Workflow/CI calls parser with request YAML
       |
       v
Parser validates against schema + enums
       |
       v
Parser generates:
  - Terraform tfvars (.auto.tfvars.json)
  - ExternalSecret manifest (.yaml)
       |
       v
PR created with generated artifacts
       |
       v
PR Review/Merge
       |
       v
Terraform apply workflow provisions resource
```

## What "Thin Template" Means

The Backstage template is "thin" - it only collects user input. All generation logic lives in the parser scripts.

### Thin Template Pattern

```yaml
steps:
  - id: fetch-template
    name: Generate Request YAML
    action: fetch:template
    input:
      url: ./skeleton
      targetPath: requests/rds
      values:
        id: ${{ parameters.id }}
        environment: ${{ parameters.environment }}
        database_name: ${{ parameters.database_name }}
        # ... other values

  - id: publish-pr
    name: Open Pull Request
    action: publish:github:pull-request
    input:
      repoUrl: github.com?owner=mikeybeezy&repo=goldenpath-idp-infra
      branchName: rds-request/${{ parameters.id }}
      title: "RDS Request: ${{ parameters.id }}"
```

### Benefits

1. PR is visible immediately - user can track status
2. CI validates against schema before merge
3. All generation logic lives in the parser (single place)
4. Changes to logic only require updating the parser, not the template
5. Template changes are cosmetic (UI/UX) only

## Parser Scripts

### Secret Request Parser

**Script**: `scripts/secret_request_parser.py` (SCRIPT-0033)

**Input**: `docs/20-contracts/secret-requests/<service>/<env>/<secret-id>.yaml`

**Outputs**:

- `envs/<env>/secrets/generated/<service>/<secret-id>.auto.tfvars.json`
- `gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/<secret-id>.yaml`

### RDS Request Parser

**Script**: `scripts/rds_request_parser.py` (SCRIPT-0034)

**Input**: `docs/20-contracts/rds-requests/<env>/<rds-id>.yaml`

**Outputs**:

- `envs/<env>-rds/generated/<rds-id>.auto.tfvars.json`
- `gitops/kustomize/overlays/<env>/apps/<service>/externalsecrets/<rds-id>.yaml`

## Schema Location and Structure

```text
schemas/
  requests/
    rds.schema.yaml       # RDS database request contract
    secret.schema.yaml    # Secret request contract (future)
  metadata/
    enums.yaml            # Shared enumerations
```

Each request schema defines:

- **properties**: Field definitions with types, patterns, enums
- **required**: Mandatory fields
- **conditional_rules**: Environment-specific constraints
- **generates**: Output artifacts the parser creates
- **approval_routing**: Who reviews based on risk/environment

## Case Convention

The codebase follows consistent case conventions:

|Context|Convention|Example|
|---------|------------|---------|
|YAML contracts|camelCase|`databaseName`, `storageGb`, `multiAz`|
|Python internals|snake_case|`rds_id`, `database_name`|
|Terraform|snake_case|`allocated_storage`, `multi_az`|
|K8s labels|kebab-case|`platform.idp/service`, `goldenpath.idp/id`|

## Running Parsers

### Validate Mode

```bash
python3 scripts/rds_request_parser.py \
  --mode validate \
  --enums schemas/metadata/enums.yaml \
  --input-files docs/20-contracts/rds-requests/dev/RDS-0001.yaml
```

### Generate Mode (Dry Run)

```bash
python3 scripts/rds_request_parser.py \
  --mode generate \
  --enums schemas/metadata/enums.yaml \
  --input-files docs/20-contracts/rds-requests/dev/RDS-0001.yaml \
  --dry-run
```

### Generate Mode (Write Files)

```bash
python3 scripts/rds_request_parser.py \
  --mode generate \
  --enums schemas/metadata/enums.yaml \
  --input-files docs/20-contracts/rds-requests/dev/RDS-0001.yaml \
  --tfvars-out-root envs \
  --externalsecret-out-root gitops
```

## Generated Artifacts

When a request is processed, the parser generates:

### Terraform Variables

```json
{
  "rds_databases": {
    "backstage_db": {
      "identifier": "dev-backstage_db",
      "database_name": "backstage_db",
      "username": "backstage_app",
      "instance_class": "db.t3.micro",
      "allocated_storage": 20,
      "metadata": {
        "id": "RDS-0001",
        "owner": "platform-team"
      }
    }
  }
}
```

### ExternalSecret Manifest

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: backstage_db-credentials-sync
  namespace: backstage_db
  labels:
    goldenpath.idp/id: RDS-0001
    platform.idp/service: backstage_db
    platform.idp/env: dev
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  target:
    name: backstage_db-db-credentials
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: goldenpath/dev/rds/backstage_db
```

## References

- [ADR-0158](../../adrs/ADR-0158-platform-standalone-rds-bounded-context.md): Platform Standalone RDS Bounded Context
- [RDS Schema](../../../schemas/requests/rds.schema.yaml): Request contract definition
- [Enums](../../../schemas/metadata/enums.yaml): Shared enumeration values
- [RDS Request Flow](./RDS_REQUEST_FLOW.md): End-to-end RDS provisioning flow

---

**Last Updated**: 2026-01-15
**Contact**: @platform-team for questions
