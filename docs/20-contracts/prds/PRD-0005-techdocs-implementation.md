---
id: PRD-0005-techdocs-implementation
title: 'PRD-0005: TechDocs Implementation Path'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: medium
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - PRD-0004-backstage-repo-structure-alignment
  - DOCS_PRDS_README
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0005: TechDocs Implementation Path

Status: draft
Owner: platform-team
Date: 2026-01-22

## Problem Statement

Documentation is scattered across repositories, wikis, and Confluence pages. Developers struggle to find authoritative, up-to-date documentation for services they depend on. TechDocs provides documentation-as-code that lives alongside the source code, ensuring docs stay current and discoverable through Backstage.

## Goals

- Enable documentation-as-code using MkDocs integrated with Backstage TechDocs
- Provide a clear path from basic (local) to production-ready (external/S3) TechDocs
- Ensure all Golden Path templates include TechDocs scaffolding
- Surface documentation in Backstage entity pages

## Non-Goals

- Migrating existing Confluence/wiki content (separate effort)
- Custom TechDocs themes/plugins (use standard techdocs-core)
- TechDocs for non-catalog entities

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Backstage TechDocs plugin configuration | Custom documentation platforms |
| MkDocs + techdocs-core in Docker image | Confluence migration |
| S3 publisher for production | Multi-region doc distribution |
| CI pipeline for doc generation | Custom MkDocs plugins |
| Golden Path template updates | Documentation content authoring |

## Requirements

### Functional

1. **Basic Mode (Phase 1 - Current)**
   - MkDocs installed in Backstage container
   - `runIn: local` generator configuration
   - Local filesystem publisher
   - Entities with `backstage.io/techdocs-ref` annotation render docs

2. **Production Mode (Phase 2)**
   - CI workflow generates docs using `techdocs-cli`
   - Docs published to S3 bucket
   - Backstage reads from S3 (`publisher.type: awsS3`)
   - Cache invalidation on doc updates

3. **Template Integration (Phase 3)**
   - All Golden Path templates include `mkdocs.yml` scaffold
   - Pre-configured `docs/` directory structure
   - TechDocs annotation in `catalog-info.yaml`

### Non-Functional

- Doc generation must complete within 60 seconds for standard repos
- S3 bucket must be in same region as EKS cluster (eu-west-2)
- Docs must be accessible without additional authentication (uses Backstage auth)

## Proposed Approach (High-Level)

### Phase 1: Basic Local Mode (Implemented)

```yaml
# app-config.yaml
techdocs:
  builder: 'local'
  generator:
    runIn: 'local'  # MkDocs in container
  publisher:
    type: 'local'
```

- MkDocs + techdocs-core installed in Dockerfile
- Suitable for development and small deployments
- Limitation: Docs regenerated on each view (slow for large docs)

### Phase 2: External Build with S3 Publisher

```yaml
# app-config.production.yaml
techdocs:
  builder: 'external'
  publisher:
    type: 'awsS3'
    awsS3:
      bucketName: ${TECHDOCS_BUCKET}
      region: eu-west-2
      s3ForcePathStyle: false
```

**CI Workflow Addition:**
```yaml
- name: Generate TechDocs
  run: |
    npx @techdocs/cli generate --source-dir . --output-dir ./site

- name: Publish TechDocs
  run: |
    npx @techdocs/cli publish \
      --publisher-type awsS3 \
      --storage-name ${TECHDOCS_BUCKET} \
      --entity default/component/my-service
```

**Infrastructure Requirements:**
- S3 bucket: `goldenpath-techdocs-{env}`
- IAM role for Backstage pod (IRSA)
- IAM role for CI (GitHub OIDC)

### Phase 3: Template Integration

Update Golden Path templates to include:

```
templates/
  stateless-app/
    skeleton/
      docs/
        index.md
        getting-started.md
        architecture.md
      mkdocs.yml
      catalog-info.yaml  # with techdocs-ref annotation
```

## Guardrails

- TechDocs bucket must have versioning enabled
- No PII or secrets in documentation (CI lint check)
- Maximum doc site size: 50MB per entity
- Required reviewer approval for docs/ changes in Golden Path templates

## Observability / Audit

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Doc generation failures | CI workflow | Any failure |
| Doc publish latency | CloudWatch | > 120s |
| S3 bucket size | CloudWatch | > 10GB |
| TechDocs 404 errors | Backstage logs | > 10/hour |

## Acceptance Criteria

### Phase 1 (Basic)
- [ ] MkDocs installed in Backstage Docker image
- [ ] `runIn: local` configuration applied
- [ ] Example entity has TechDocs annotation
- [ ] Documentation renders in Backstage UI

### Phase 2 (Production)
- [ ] S3 bucket provisioned via Terraform
- [ ] IRSA role configured for Backstage
- [ ] CI workflow publishes docs on merge
- [ ] Backstage reads docs from S3

### Phase 3 (Templates)
- [ ] All Golden Path templates include mkdocs.yml
- [ ] Template scaffolder creates docs/ structure
- [ ] New services have working TechDocs from creation

## Success Metrics

- 80% of catalog services have TechDocs within 6 months
- Average doc generation time < 30 seconds
- Documentation freshness: 90% of docs updated within 30 days of code change
- Developer satisfaction: NPS > 40 for documentation discovery

## Open Questions

1. Should we enforce TechDocs for all new services or make it optional?
2. What's the retention policy for old doc versions in S3?
3. Should we support multiple doc sites per entity (e.g., API docs + user guides)?
4. Integration with ADR tooling (adr-tools) for architecture decisions?

## Implementation Timeline

| Phase | Scope | Target |
|-------|-------|--------|
| Phase 1 | Basic local mode | Done (2026-01-22) |
| Phase 2 | S3 publisher + CI | TBD |
| Phase 3 | Template integration | TBD |

## References

- [Backstage TechDocs Documentation](https://backstage.io/docs/features/techdocs/)
- [TechDocs Configuration](https://backstage.io/docs/features/techdocs/configuration)
- [TechDocs CLI](https://backstage.io/docs/features/techdocs/cli)
- [MkDocs Material Theme](https://squidfunk.github.io/mkdocs-material/)
- PRD-0004: Backstage Repo Structure Alignment

---

## Comments and Feedback

When providing feedback, leave a comment and timestamp your comment.

-
