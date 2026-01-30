---
id: ADR-0187-minio-rag-data-persistence
title: MinIO for Local RAG Vector Database Persistence
type: adr
domain: platform-core
owner: platform-team
lifecycle: active
exempt: false
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
schema_version: 1
relates_to:
  - ADR-0184-rag-markdown-header-chunking
  - ADR-0185-graphiti-agent-memory-framework
  - ADR-0186-llamaindex-retrieval-layer
  - PRD-0008-governance-rag-pipeline
supersedes: []
superseded_by: []
tags:
  - rag
  - storage
  - minio
  - s3
  - chromadb
inheritance: {}
supported_until: '2028-01-01'
effective_date: 2026-01-30
review_date: 2026-07-30
---

# ADR-0187: MinIO for Local RAG Vector Database Persistence

## Status

**Accepted** (2026-01-30)

## Context

The RAG pipeline uses ChromaDB as the vector database for storing document embeddings. During development, ChromaDB creates a local `.chroma/` directory containing:

- SQLite database (~72MB for current governance corpus)
- Collection metadata
- Embedding vectors

### The Problem

| Constraint | Impact |
|------------|--------|
| Large binary files | Git is not designed for 72MB+ databases |
| Rebuild time | Re-indexing 200+ governance docs takes significant time |
| Team collaboration | Fresh clones have no index, must rebuild |
| CI/CD pipelines | Each run would need to rebuild or pull index |

### Requirements

1. **Persistence**: Vector database survives container restarts and fresh clones
2. **Team sharing**: Multiple developers can share the same index
3. **Production parity**: Local development mirrors production storage patterns
4. **No git bloat**: Binary database files excluded from version control
5. **Reproducibility**: Index can be rebuilt from source documents if needed

## Decision

**Use MinIO (Docker-based S3-compatible storage) for local RAG data persistence.**

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workstation                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     push/pull     ┌──────────────────┐   │
│  │   .chroma/   │ ◄───────────────► │      MinIO       │   │
│  │  (72MB DB)   │                   │  (Docker Volume) │   │
│  └──────────────┘                   │                  │   │
│         │                           │  localhost:9000  │   │
│         ▼                           │  (S3 API)        │   │
│  ┌──────────────┐                   │                  │   │
│  │  RAG Scripts │                   │  localhost:9001  │   │
│  │  - indexer   │                   │  (Web Console)   │   │
│  │  - retriever │                   └──────────────────┘   │
│  └──────────────┘                            │              │
│                                              ▼              │
│                                    ┌──────────────────┐    │
│                                    │   minio_data     │    │
│                                    │  (Docker Volume) │    │
│                                    │   Persistent!    │    │
│                                    └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

```bash
# 1. Start MinIO (one-time or after reboot)
docker compose -f docker-compose.minio.yml up -d

# 2. After building/updating RAG index
./scripts/rag-data-sync.sh push

# 3. On fresh clone or to restore
./scripts/rag-data-sync.sh pull

# 4. Check sync status
./scripts/rag-data-sync.sh status
```

## Alternatives Considered

### 1. Git LFS (Large File Storage)

Track large binary files in Git using LFS pointers.

| Aspect | Assessment |
|--------|------------|
| Setup | Requires LFS server or GitHub LFS quota |
| Versioning | Full version history of database |
| Bandwidth | Downloads on every clone |
| Cost | GitHub LFS has storage/bandwidth limits |

**Rejected because:** Still requires downloading 72MB+ on every clone. GitHub LFS has storage limits (1GB free). Database changes frequently during development, creating version bloat.

### 2. DVC (Data Version Control)

ML-focused tool for versioning data artifacts with remote storage.

| Aspect | Assessment |
|--------|------------|
| Design | Purpose-built for ML data artifacts |
| Integration | Git-like workflow (`dvc push`, `dvc pull`) |
| Backends | Supports S3, GCS, Azure, SSH, local |
| Complexity | Additional tooling, `.dvc` files in repo |

**Rejected because:** Adds another tool to the stack. Team would need to learn DVC. For a single vector database, simpler sync script is sufficient. Could revisit if we have more ML artifacts.

### 3. AWS S3 (Real Cloud Storage)

Use actual S3 bucket for persistence.

| Aspect | Assessment |
|--------|------------|
| Production parity | Highest - same as production |
| Availability | Always accessible |
| Cost | ~$0.023/GB/month storage + transfer |
| Network dependency | Requires internet connection |

**Rejected for local dev because:** Requires internet connectivity for local development. Incurs AWS costs. Sync latency impacts development speed. However, **S3 remains the production target** - MinIO provides API compatibility.

### 4. ChromaDB Server Mode

Run ChromaDB as a persistent service instead of file-based.

| Aspect | Assessment |
|--------|------------|
| Architecture | Client-server instead of embedded |
| Persistence | Server manages its own storage |
| Sharing | Multiple clients can connect |
| Complexity | Additional service to manage |

**Rejected because:** Adds operational complexity for local development. Embedded mode is simpler for single-developer workflows. Server mode better suited for production deployment (separate decision).

### 5. Local .gitignore Only (Rebuild Each Time)

Simply exclude `.chroma/` and rebuild on fresh clone.

| Aspect | Assessment |
|--------|------------|
| Simplicity | No additional infrastructure |
| Reproducibility | Always rebuilds from source |
| Time cost | 5-10 minutes to reindex corpus |
| CI/CD | Every pipeline run rebuilds |

**Rejected because:** Rebuild time impacts developer productivity. CI/CD would be slower. Index consistency not guaranteed if source documents differ.

## Decision Matrix

| Criterion | Git LFS | DVC | AWS S3 | Chroma Server | MinIO |
|-----------|---------|-----|--------|---------------|-------|
| No internet required | ❌ | ⚠️ | ❌ | ✅ | ✅ |
| No cost | ⚠️ | ✅ | ❌ | ✅ | ✅ |
| S3 API compatible | ❌ | ✅ | ✅ | ❌ | ✅ |
| Simple setup | ⚠️ | ⚠️ | ✅ | ⚠️ | ✅ |
| Production parity | ❌ | ✅ | ✅ | ⚠️ | ✅ |
| Team sharing | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| No git bloat | ⚠️ | ✅ | ✅ | ✅ | ✅ |

**MinIO selected** for best balance of: local-first development, S3 API compatibility (production parity), zero cost, and minimal complexity.

## Consequences

### Positive

- **No git bloat**: `.chroma/` excluded from repository
- **Fast local access**: No network latency for reads/writes
- **S3 API compatibility**: Same code works with production S3
- **Web console**: Visual inspection of stored data at `localhost:9001`
- **Docker volume persistence**: Survives container restarts
- **Zero cloud cost**: Runs entirely locally

### Negative

- **Not automatically shared**: Team members maintain separate MinIO instances
- **Docker dependency**: Requires Docker for MinIO service
- **Manual sync**: Developer must run push/pull scripts
- **Local storage**: Uses disk space on developer machine

### Mitigations

| Negative | Mitigation |
|----------|------------|
| Not shared | Document rebuild process; provide seed data script |
| Docker dependency | Docker already required for other services |
| Manual sync | Add sync reminders to development workflow docs |
| Local storage | MinIO data can be pruned; ~100MB is acceptable |

## Implementation

### Files Created

| File | Purpose |
|------|---------|
| `docker-compose.minio.yml` | MinIO service configuration |
| `scripts/rag-data-sync.sh` | Push/pull sync script |
| `.gitignore` (updated) | Excludes `.chroma/` and `reports/usage_log.jsonl` |

### MinIO Configuration

```yaml
services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"   # S3 API
      - "9001:9001"   # Web Console
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
```

### Sync Script Interface

```bash
# Push local .chroma to MinIO
./scripts/rag-data-sync.sh push

# Pull from MinIO to local .chroma
./scripts/rag-data-sync.sh pull

# Check sync status
./scripts/rag-data-sync.sh status
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIO_ENDPOINT` | `http://localhost:9000` | MinIO S3 API endpoint |
| `MINIO_BUCKET` | `chroma-backups` | Bucket for ChromaDB backups |
| `CHROMA_DIR` | `.chroma` | Local ChromaDB directory |
| `AWS_ACCESS_KEY_ID` | `minioadmin` | MinIO access key |
| `AWS_SECRET_ACCESS_KEY` | `minioadmin` | MinIO secret key |

## Production Considerations

For production deployment, replace MinIO with:

```bash
# Production environment variables
export MINIO_ENDPOINT="https://s3.eu-west-2.amazonaws.com"
export MINIO_BUCKET="goldenpath-rag-data"
export AWS_ACCESS_KEY_ID="<from-secrets-manager>"
export AWS_SECRET_ACCESS_KEY="<from-secrets-manager>"
```

The same sync script works with real S3 - no code changes required.

## Future Enhancements

1. **CI/CD caching**: Cache ChromaDB in GitHub Actions for faster pipeline runs
2. **Team MinIO server**: Shared MinIO instance for team collaboration
3. **Automatic sync hooks**: Git hooks to remind/automate sync on pull
4. **Index versioning**: Tag MinIO objects with source document hashes

## References

- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [MinIO Docker Quickstart](https://min.io/docs/minio/container/index.html)
- [ChromaDB Persistence](https://docs.trychroma.com/usage-guide#persistence)
- [ADR-0186: LlamaIndex Retrieval Layer](./ADR-0186-llamaindex-retrieval-layer.md)
- [PRD-0008: Governance RAG Pipeline](../20-contracts/prds/PRD-0008-governance-rag-pipeline.md)
