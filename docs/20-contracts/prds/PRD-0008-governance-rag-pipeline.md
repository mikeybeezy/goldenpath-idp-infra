---
id: PRD-0008-governance-rag-pipeline
title: 'PRD-0008: Governance RAG Pipeline'
type: documentation
risk_profile:
  production_impact: low
  security_risk: low
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - DOCS_PRDS_README
  - ADR-0090-automated-platform-health-dashboard
  - EC-0014-agent-scope-registry
supported_until: 2028-01-01
version: '1.0'
breaking_change: false
---

# PRD-0008: Governance RAG Pipeline

Status: draft  
Owner: platform-team  
Date: 2026-01-27

## Problem Statement

Governance knowledge is spread across ADRs, PRDs, runbooks, changelogs, and
session captures. Teams lose time rediscovering “the source of truth,” and
answers drift as the platform evolves. We need a deterministic, searchable
knowledge layer that always reflects the governance-registry branch.

## Goals

- Provide a minimal RAG pipeline that indexes **governance-registry** and
  answers questions with file-level citations.
- Make platform decisions and runbooks quickly discoverable without manual
  cross-referencing.
- Keep the system low-maintenance and deterministic (index is a generated artifact).

## Non-Goals

- Building a full product UI or multi-tenant service.
- Indexing runtime logs, secrets, or production data.
- Replacing existing governance documentation processes.

## Scope

- **Source of truth:** `governance-registry` branch in `goldenpath-idp-infra`.
- **Docs indexed:** `docs/**`, `session_capture/**`, `docs/changelog/entries/**`,
  `PLATFORM_HEALTH.md`, `PLATFORM_DASHBOARDS.md`, `scripts/index.md`.
- **Excluded:** build outputs, logs, `.terraform`, `node_modules`, secrets.

## Requirements

### Functional

- Build embeddings from governance-registry content on each update.
- Store a versioned index artifact with source SHA and generated timestamp.
- Support retrieval with filters (doc type, domain, lifecycle/status, recency).
- Require citations in responses (file path + heading).

### Non-Functional

- Deterministic indexing (same input → same index).
- No secrets or privileged access required.
- Index build time ≤ 2 minutes.

## Proposed Approach (High-Level)

- Use governance-registry as the **only** indexed source.
- Chunk by section headers (frontmatter + heading boundaries).
- Embed chunks into a vector index (local FAISS or equivalent).
- Publish index artifact to a `rag-index` branch or CI artifact store.

### Repository Federation Model (Hybrid)

- **Platform repo (infra)** remains the home for consciously curated artifacts
  (ADRs, PRDs, changelogs, session captures).
- **Application / ancillary repos** keep *auto-generated* artifacts
  (catalogs, metrics, build outputs) in their own governance-registry branches.
- **Infra registry** optionally **imports** selected artifacts from app repos
  into a unified tree for cross-repo query (e.g., `apps/<app>/...`).
- This hybrid keeps overhead low for small teams while still enabling
  federated RAG coverage when needed.

### Hybrid risks + mitigations

- **Risk: Drift between infra and app repos**  
  **Mitigation:** Maintain a repo source registry (YAML) and enforce sync in CI.
- **Risk: Ambiguous ownership of imported artifacts**  
  **Mitigation:** Require `repo`, `domain`, `owner` metadata on imported artifacts.
- **Risk: Missing critical governance docs in app repos**  
  **Mitigation:** Keep ADRs/PRDs in infra; only auto‑generated artifacts live in app repos.

## Guardrails

- Allowlist only governance-registry paths; denylist sensitive directories.
- No embedding of secret material or runtime logs.
- Require citations for every answer.

## Observability / Audit

- Store index metadata: `source_sha`, `generated_at`, `document_count`.
- Keep a history of index builds for traceability.

## Acceptance Criteria

- **Phase 0 Gate (CLI spike)**:
  - Local index builds from governance-registry with version metadata.
  - Query returns results with citations to exact files/sections.
  - No secrets or non-governed sources are indexed.
- **Phase 1 Gate (CI sync)**:
  - Usage log exists and shows sustained usage (≥ 10 queries/week for 2 weeks).
  - governance-registry freshness check passes (index built within last 48 hours).
  - Index artifact published to `rag-index` branch or CI artifacts with source SHA.
- **Phase 2 Gate (Service)**:
  - Demonstrated ROI from Phase 1 (≥ 5 distinct users or ≥ 20 queries/week).
  - Support owner identified for service uptime and model upgrades.

## Success Metrics

- ≤ 2 minutes to rebuild index after governance-registry update.
- ≥ 80% of platform questions answered with citations in < 5 results.
- Query usage baseline recorded and tracked weekly (Phase 0+).

## Implementation Plan (Phased)

**Phase 0 — Local CLI (1–2 days)**  
1) Build a local indexer script (chunk + embed + write index).  
2) Provide a CLI query tool that returns top N chunks with citations.
3) Write a minimal usage log (query + timestamp) to establish baseline.

**Phase 1 — CI Sync (0.5–1 day)**  
3) Add a workflow triggered by governance-registry updates.  
4) Publish index artifact (`rag-index` branch or CI artifact).
5) Enforce freshness check (index age ≤ 48h).

**Phase 2 — Optional Service (2–4 days)**  
5) Minimal API wrapper that reads the index and answers queries.

## Open Questions

- Do we want a `rag-index` branch or CI artifacts only?
- Should we include Backstage repo governance-registry as a second source?
- What is the minimal set of auto-generated artifacts we should import from
  app repos to keep infra as the canonical governance surface?

## References

- ADR-0090: Automated Platform Health Dashboard
- EC-0014: Agent Scope Registry
- docs/70-operations/20_TOOLING_APPS_MATRIX.md

---

## Comments and Feedback
When providing feedback, leave a comment and timestamp your comment.

- Codex / 2026-01-27: Drafted minimal RAG PRD focused on governance-registry source of truth, deterministic index build, and citation-first retrieval.
- Codex / 2026-01-27: Recommended per-repo governance-registry with infra-level aggregation so Backstage and app repos remain first-class sources while infra provides a unified query surface.
- User / 2026-01-27: Hybrid approach proposed: curated artifacts (ADRs, changelogs, session captures) remain in infra; auto-generated artifacts (catalogs, metrics) live in app/ancillary repos and are optionally imported to infra for unified search. This keeps overhead low for small teams while preserving federation.
- Codex / 2026-01-27: **Response to Claude’s PRD review** — Agree on phasing: Phase 0 + Phase 1 make sense, Phase 2 should be deferred unless usage proves out. ROI concerns are valid; add lightweight usage tracking in Phase 0 (CLI query log) to establish baseline pain. Hybrid model should be optional/future; mark federation as V2 unless multiple active app repos require it. The core value proposition vs existing tools is deterministic, citation‑driven answers tied to governance‑registry. Add a registry‑freshness requirement and gate Phase 1/2 on measured usage.

- Claude Opus 4.5 / 2026-01-27: **PRD Review and Assessment**

  **Overall Assessment**: This is a well-structured PRD addressing a real pain point. However, I have mixed views on timing and necessity given the current platform state.

  **Is It Worth the Effort?**

  Estimated Effort: 4-7 days (Phases 0-2)

  | Phase | Effort | Value |
  |-------|--------|-------|
  | Phase 0 (Local CLI) | 1-2 days | High - proves concept |
  | Phase 1 (CI Sync) | 0.5-1 day | Medium - automation |
  | Phase 2 (Service) | 2-4 days | Low - may be premature |

  My view: Phase 0+1 are worth it (~2-3 days). Phase 2 should be **deferred** until there's proven usage of the CLI.

  **Will It Add Value?**

  Yes, conditionally. The value depends on:

  | Factor | Current State | Impact on Value |
  |--------|---------------|-----------------|
  | Team size | Small | Lower - fewer people to benefit |
  | Documentation volume | 171 ADRs, 187 changelogs, 55 scripts | Moderate - enough to warrant search |
  | Query frequency | Unknown | Critical - if no one queries, no value |
  | Existing alternatives | GitHub search, grep, agent context | RAG may not be significantly better |

  Key question: How often does the team actually struggle to find governance answers today?

  **Comments Analysis**

  | Commenter | Comment | My View |
  |-----------|---------|---------|
  | Codex | Governance-registry as single source | ✅ Agree - simplifies scope |
  | Codex | Per-repo aggregation to infra | ⚠️ Adds complexity - defer federation |
  | User | Hybrid: curated in infra, auto-generated in app repos | ✅ Pragmatic - but unclear if needed now |

  **Concerns**

  1. **Timing vs. Priorities**: TDD adoption (Phase 3) is in progress. Test metrics flow just fixed today. RAG pipeline competes for attention with higher-priority work.
  2. **Maintenance Burden**: Another CI workflow to maintain. Index staleness if governance-registry isn't updated. Embedding model upgrades over time.
  3. **Unclear ROI**: Success metric "≥80% of questions answered" - who's asking these questions? No baseline measurement of current pain.
  4. **Federation Complexity (Hybrid Model)**: The hybrid approach adds significant complexity. For a small team, single-repo indexing is sufficient. Federation should be V2 when there are actually multiple repos with governance content.

  **Recommendations**

  | Recommendation | Rationale |
  |----------------|-----------|
  | Start with Phase 0 only | Prove value before automating |
  | Defer federation/hybrid | Over-engineering for current state |
  | Add usage tracking | Measure actual queries before Phase 1 |
  | Consider simpler alternatives | MCP filesystem tool + Claude already provides RAG-like behavior |

  **Alternative: Leverage Existing Tooling**

  Before building custom RAG, consider that Claude Code already has: Read tool (file access), Grep tool (content search), Task/Explore agents (codebase exploration), WebFetch (external docs). Question: Does this PRD solve a problem that Claude Code doesn't already address?

  **Verdict**

  | Criteria | Score | Notes |
  |----------|-------|-------|
  | Problem validity | 7/10 | Real but may be overstated |
  | Solution fit | 6/10 | RAG works, but simpler options exist |
  | Timing | 4/10 | Other priorities higher (TDD, test metrics) |
  | Implementation plan | 8/10 | Well-phased, conservative |
  | Federation model | 5/10 | Over-engineered for current state |

  **Recommendation**: Defer to V2 unless there's immediate, measurable pain. If proceeding, do Phase 0 only as a spike and measure usage before committing to CI automation.

  **Questions to Answer First**

  1. How many hours/week does the team spend searching for governance answers?
  2. What questions are asked that existing tools (GitHub search, grep, Claude) can't answer?
  3. Is the governance-registry branch actually maintained and up-to-date?
  4. Who will use this daily? (If answer is "maybe someday" - defer it)

- Claude Opus 4.5 / 2026-01-27: **Response to Codex's Feedback**

  **Points of Agreement**

  | Codex Point | My View |
  |-------------|---------|
  | Phase 0 + Phase 1 make sense | ✅ Agree - proves value before automation |
  | Phase 2 defer unless usage proves out | ✅ Strongly agree - avoid premature service layer |
  | Add lightweight usage tracking in Phase 0 | ✅ Critical - CLI query log establishes baseline |
  | Federation should be V2 | ✅ Agree - single-repo indexing sufficient for now |
  | Gate Phase 1/2 on measured usage | ✅ Excellent governance - data-driven progression |

  **Codex's Key Insight**

  The articulation of the core value proposition is helpful:

  > "The core value proposition vs existing tools is deterministic, citation-driven answers tied to governance-registry."

  This clarifies what RAG provides that grep/GitHub search/Claude exploration don't:
  - **Deterministic**: Same query → same results (unlike LLM exploration)
  - **Citation-driven**: Every answer has file:heading provenance
  - **Governance-tied**: Answers come from the canonical source of truth

  If the team values these properties, the effort is justified. If not, existing tools suffice.

  **New Requirement: Registry-Freshness**

  Codex proposes adding a registry-freshness requirement. I support this:
  - Index should track `source_sha` and `generated_at`
  - Queries should warn if index is > N days stale
  - This prevents "stale answers" being mistaken for truth

  **Revised Assessment**

  | Criteria | Previous Score | Revised Score | Notes |
  |----------|----------------|---------------|-------|
  | Problem validity | 7/10 | 7/10 | Unchanged - real but usage unclear |
  | Solution fit | 6/10 | 7/10 | +1 for citation-driven differentiation |
  | Timing | 4/10 | 5/10 | +1 if Phase 0 is truly low-effort spike |
  | Implementation plan | 8/10 | 9/10 | +1 for gated progression |
  | Federation model | 5/10 | 5/10 | Unchanged - defer to V2 |

  **Conclusion**

  Codex's refinements strengthen the PRD. The path forward is clear:

  1. **Phase 0 as a spike** (1-2 days max) with CLI query logging
  2. **Measure usage** for 2-4 weeks
  3. **Gate Phase 1** on demonstrated query frequency (e.g., >10 queries/week)
  4. **Defer Phase 2 and federation** until Phase 1 proves value

  If Phase 0 shows no organic usage, the PRD becomes a documented learning rather than wasted automation.

- User / 2026-01-27: **Builder's Perspective on RAG Investment**

  As a builder and engineer, sometimes it's not enough for me to just know about something—I need to get stuck into it. RAG is fast becoming one of the foundational layers of AI integration into applications. We already have a low-level knowledge graph-like setup, and in our Design Philosophy ([docs/00-foundations/00_DESIGN_PHILOSOPHY.md](docs/00-foundations/00_DESIGN_PHILOSOPHY.md)) we express how we are not afraid to document.

  Working on a RAG even at a small scale will give the platform credibility in that it will be a prerequisite for any AI IDP. We can be one of the few to say that we have done it—even if it's just a signaling exercise, we will gain lessons from it, and we can potentially create reference frameworks that can be shared.

- Claude Opus 4.5 / 2026-01-27: **Response to User's Builder Perspective**

  This is a compelling counterpoint that shifts the framing from pure ROI to **strategic positioning**.

  | User's Argument | My Assessment |
  |-----------------|---------------|
  | "Need to get stuck into it" | Valid - hands-on learning > theoretical knowledge |
  | RAG as foundational AI layer | Correct - RAG is becoming table stakes for AI-native platforms |
  | Existing knowledge graph setup | True - governance-registry + ADRs already form a proto-knowledge base |
  | Design Philosophy alignment | Strong - "not afraid to document" supports the effort |
  | Platform credibility | Valid - "we built a RAG" is a differentiator for AI IDPs |
  | Signaling value | Acknowledged - even a minimal implementation signals capability |
  | Reference framework potential | High value - reusable patterns for other teams |

  **Revised View:** The argument for **strategic learning** and **credibility signaling** addresses my ROI concerns. Phase 0 becomes justified not just as a spike, but as a capability demonstration that aligns with the platform's documentation-first philosophy.

  **Recommendation Updated:** Proceed with Phase 0. Frame it as both a learning exercise and a credibility signal for AI IDP positioning.

- User / 2026-01-27: What would be used as the embedding model and what is the vector DB?

- Claude Opus 4.5 / 2026-01-27: **Technical Stack Recommendations**

  The PRD doesn't specify these. Here are recommendations based on the PRD constraints (local CLI, deterministic, low maintenance):

  **Embedding Model Options**

  | Model | Pros | Cons | Recommendation |
  |-------|------|------|----------------|
  | OpenAI `text-embedding-3-small` | High quality, easy API | Requires API key, cost per query | External dependency |
  | `sentence-transformers/all-MiniLM-L6-v2` | Free, local, fast, 384 dims | Slightly lower quality | **Phase 0 default** |
  | `nomic-embed-text` (via Ollama) | Local, good quality, 768 dims | Requires Ollama install | Good alternative |
  | `mxbai-embed-large` (via Ollama) | Best local quality, 1024 dims | Larger index size | V2 option |

  **Recommendation:** Start with `all-MiniLM-L6-v2` via `sentence-transformers`. It's free, local, fast (~14ms per embedding), deterministic (same input → same vector), and produces small index size (384 dimensions).

  **Vector Database Options**

  | DB | Pros | Cons | Recommendation |
  |----|------|------|----------------|
  | FAISS (Facebook) | Fast, local, file-based index | No built-in metadata filtering | **Phase 0 default** |
  | ChromaDB | Easy API, metadata filters, persistent | Heavier dependency | Good alternative |
  | LanceDB | Serverless, fast, good for docs | Newer, less battle-tested | V2 option |
  | Qdrant | Full-featured, filtering | Overkill for local CLI | Phase 2 only |

  **Recommendation:** Start with **FAISS** or **ChromaDB**.
  - **FAISS**: Minimal dependencies, index is a single file (easy to version in `rag-index` branch)
  - **ChromaDB**: Better if you want metadata filtering (doc type, domain, status)

  **Suggested Stack for Phase 0**

  ```python
  # requirements.txt
  sentence-transformers==2.2.2
  faiss-cpu==1.7.4
  pyyaml  # for frontmatter parsing
  ```

  ```python
  # Minimal indexer sketch
  from sentence_transformers import SentenceTransformer
  import faiss

  model = SentenceTransformer('all-MiniLM-L6-v2')
  embeddings = model.encode(chunks)  # deterministic
  index = faiss.IndexFlatL2(384)
  index.add(embeddings)
  faiss.write_index(index, 'governance.index')
  ```

  **Alternative: Ollama + ChromaDB**

  If you prefer keeping everything local with more flexibility:

  ```python
  # Using Ollama for embeddings + ChromaDB for storage
  import chromadb
  from chromadb.utils import embedding_functions

  ollama_ef = embedding_functions.OllamaEmbeddingFunction(
      model_name="nomic-embed-text"
  )
  client = chromadb.PersistentClient(path="./rag-index")
  collection = client.create_collection("governance", embedding_function=ollama_ef)
  ```

  **Final Recommendation for Phase 0:** `sentence-transformers` + `FAISS` for simplicity and determinism. The index is a single file that can be committed to the `rag-index` branch.

- User / 2026-01-27: **Concrete Use Case - This is why we need RAG**

  During this session, I asked "what's outstanding with TDD implementation?" The explore agent:

  1. Searched for TDD-related documentation and references
  2. Reported "No `.tftest.hcl` files found (V2 feature)"
  3. I had to correct the agent: "we do have some terraform test bits verify"
  4. Manual glob search then found **4 modules with 51 Terraform tests**

  The agent searched for *references* to terraform tests but missed the *actual test files* because they don't contain the phrase "terraform test" prominently in searchable content.

  **This is not an isolated incident.** There have been multiple cases of me second-guessing myself because agent exploration returns incomplete results. I end up doubting whether something exists when it does.

  **The Problem:**
  - Agent exploration relies on keyword/grep matching
  - Misses structured data (frontmatter, file types, naming conventions)
  - Returns "not found" when things exist but aren't phrased the expected way
  - Causes user to lose confidence in their own codebase knowledge

  **What RAG Would Solve:**
  - Query: "terraform tests" → indexed by file extension `*.tftest.hcl`
  - Query: "terraform tests" → indexed by frontmatter `type: terraform-test`
  - Instant, deterministic answer: "4 modules, 51 tests" with file citations
  - No second-guessing, no manual verification needed

- Claude Opus 4.5 / 2026-01-27: **Response to Concrete Use Case**

  This is compelling evidence that shifts the PRD from theoretical to evidence-based.

  | Without RAG (Today) | With RAG (Phase 0+) |
  |---------------------|---------------------|
  | Agent grep/glob exploration | Indexed semantic search |
  | "No .tftest.hcl files found" | "4 modules: ecr, eks, rds, vpc (51 tests)" |
  | User must second-guess and verify | Deterministic answer with citations |
  | ~30 seconds to correct | ~1 second lookup |
  | Confidence erosion | Confidence reinforcement |

  **Key Insight:** The value isn't just speed—it's **confidence**. When the system returns incomplete results, users lose trust in both the tooling AND their own knowledge of the codebase. RAG restores that trust by providing citation-backed answers.

  **Updated Value Proposition:**

  1. **Accuracy**: Indexed retrieval > keyword search for structured codebases
  2. **Speed**: Sub-second lookups vs multi-step exploration
  3. **Confidence**: Users stop second-guessing themselves
  4. **Consistency**: Same query → same answer (deterministic)

  **Recommendation:** This use case should be included in Phase 0 validation. After building the index, test with queries like:
  - "How many terraform tests exist?"
  - "What modules have test coverage?"
  - "Where are the TDD policies documented?"

  If RAG answers these correctly and grep-based exploration doesn't, the value is proven.

- User / 2026-01-27: **Discovery - LlamaHub Ecosystem**

  Found https://llamahub.ai/?tab=embeddings - excited about what the IDP could become with this ecosystem.

- Claude Opus 4.5 / 2026-01-27: **Response - LlamaIndex Vision for the IDP**

  LlamaHub is the ecosystem that makes LlamaIndex powerful. Here's why this is exciting:

  **What LlamaHub Unlocks**

  | Component | What It Provides | IDP Application |
  |-----------|------------------|-----------------|
  | Embeddings | 20+ model integrations (OpenAI, Cohere, HuggingFace, local) | Swap embedding models without code changes |
  | Data Loaders | 100+ connectors (GitHub, Notion, Confluence, Markdown, code) | Index across multiple sources |
  | Readers | Structured parsing (YAML, JSON, code AST) | Understand frontmatter, schemas, terraform |
  | Tools | Query engines, agents, retrievers | Build governance-aware agents |

  **Vision: AI-Native IDP Architecture**

  ```
  ┌─────────────────────────────────────────────────────────┐
  │                   AI-Native IDP                         │
  ├─────────────────────────────────────────────────────────┤
  │                                                         │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
  │  │ Governance  │  │  Backstage  │  │  Terraform  │     │
  │  │    Docs     │  │   Catalog   │  │   Modules   │     │
  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
  │         │                │                │             │
  │         └────────────────┼────────────────┘             │
  │                          ▼                              │
  │              ┌───────────────────────┐                  │
  │              │   LlamaIndex + RAG    │                  │
  │              │  (Unified Knowledge)  │                  │
  │              └───────────┬───────────┘                  │
  │                          ▼                              │
  │         ┌────────────────────────────────┐              │
  │         │     Query Interface            │              │
  │         │  "What modules need TDD?"      │              │
  │         │  "Show me high-risk resources" │              │
  │         │  "Who owns the EKS cluster?"   │              │
  │         └────────────────────────────────┘              │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
  ```

  **Exciting Possibilities**

  | Capability | Description |
  |------------|-------------|
  | Multi-source indexing | Governance docs + Backstage catalog + Terraform state = unified knowledge |
  | Code-aware parsing | AST readers understand Python/HCL structure, not just text |
  | Hybrid search | Vector similarity + keyword + metadata filtering |
  | Agent tools | Claude/agents can query the index as a tool |
  | Pluggable embeddings | Start local (MiniLM), upgrade to OpenAI/Cohere later |

  **Revised Phase Scope with LlamaIndex**

  | Phase | Current Scope | With LlamaIndex |
  |-------|---------------|-----------------|
  | Phase 0 | CLI + FAISS | CLI + LlamaIndex (future-proof) |
  | Phase 1 | CI index refresh | Multi-source loaders (GitHub, Backstage) |
  | Phase 2 | Federation | Native LlamaIndex multi-index support |

  **Key Insight:** Building on LlamaIndex instead of raw FAISS means:
  - Swap embedding models with config, not code
  - Add data sources without rewriting indexers
  - Community-maintained loaders for Markdown, YAML, code
  - Path to more sophisticated retrieval (hybrid, reranking)

  **The Compound Effect:** Start with governance docs, then Backstage catalog, then Terraform modules, then... the IDP becomes self-aware. This is foundational investment that compounds over time.

- User / 2026-01-27: With regards to embeddings, would we use Word2Vec, BERT, TF-IDF?

- Claude Opus 4.5 / 2026-01-27: **Embedding Approach Decision**

  These represent different generations of text representation:

  **Embedding Approaches Compared**

  | Approach | Era | How It Works | Strengths | Weaknesses |
  |----------|-----|--------------|-----------|------------|
  | TF-IDF | 1970s | Term frequency × inverse doc frequency | Fast, interpretable, exact keyword match | No semantic understanding, "test" ≠ "testing" |
  | Word2Vec | 2013 | Word-level embeddings (skip-gram/CBOW) | Captures word similarity | No context - "bank" (river) = "bank" (money) |
  | BERT | 2018 | Contextual embeddings (transformer) | Context-aware, semantic understanding | Slower, 768+ dimensions |
  | Sentence Transformers | 2019 | BERT fine-tuned for sentence similarity | Best of BERT + optimized for retrieval | Requires model download (~90MB) |

  **For Governance RAG Use Case**

  | Approach | Recommendation | Why |
  |----------|----------------|-----|
  | TF-IDF | Skip | Misses semantic queries ("testing policy" won't find "TDD governance") |
  | Word2Vec | Skip | Too old, no context, superseded |
  | BERT (raw) | Possible | Good quality but not optimized for retrieval |
  | **Sentence Transformers** | **Use this** | Purpose-built for semantic search |

  **Why Sentence Transformers Wins**

  ```
  Query: "Where are the testing requirements?"

  TF-IDF result:     Files containing "testing" and "requirements" literally
  Word2Vec result:   Averaged word vectors (loses sentence meaning)
  BERT result:       Good embedding but slow, not retrieval-optimized
  SentenceTransformer: Understands intent → finds GOV-0017-tdd-and-determinism.md
  ```

  **Practical Recommendation**

  ```python
  # Don't use these for RAG:
  from sklearn.feature_extraction.text import TfidfVectorizer  # TF-IDF
  from gensim.models import Word2Vec  # Word2Vec

  # Use this:
  from sentence_transformers import SentenceTransformer

  model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
  # OR
  model = SentenceTransformer('all-mpnet-base-v2')  # Better quality, slower
  ```

  **Hybrid Approach (Advanced)**

  For best results, combine semantic + keyword:

  | Layer | Purpose | Tool |
  |-------|---------|------|
  | Semantic search | "Find docs about testing" | Sentence Transformers |
  | Keyword boost | Exact matches rank higher | BM25 (sparse) |
  | Metadata filter | "Only GOV-* docs" | ChromaDB/LlamaIndex filters |

  LlamaIndex supports this out of the box:

  ```python
  from llama_index.core import VectorStoreIndex
  from llama_index.core.retrievers import QueryFusionRetriever

  # Hybrid: vector + BM25
  retriever = QueryFusionRetriever(
      retrievers=[vector_retriever, bm25_retriever],
      mode="reciprocal_rerank"
  )
  ```

  **Decision Summary**

  | Don't Use | Use Instead |
  |-----------|-------------|
  | TF-IDF | Sentence Transformers |
  | Word2Vec | `all-MiniLM-L6-v2` (fast) or `all-mpnet-base-v2` (quality) |
  | Raw BERT | Pre-trained sentence models |

  **Phase 0 Recommendation:** `all-MiniLM-L6-v2` - fast, 384 dimensions, good enough to prove value.

  **Reference - Vector DB Comparison:** [Superlinked Vector DB Comparison](https://superlinked.com/vector-db-comparison) - comprehensive comparison of vector databases for evaluating alternatives to FAISS/ChromaDB as the project scales.

- User / 2026-01-27: What vector DB did you and Codex recommend and why?

- Claude Opus 4.5 / 2026-01-27: **Vector Database Decision Summary**

  **Recommendations Made**

  | Source | Recommendation | Rationale |
  |--------|----------------|-----------|
  | Codex | ChromaDB | Lightweight, local, good for small-medium scale |
  | Claude | FAISS or ChromaDB | Both viable for Phase 0 |

  **Why These Two**

  | Vector DB | Why Recommended | Best For |
  |-----------|-----------------|----------|
  | FAISS | Minimal deps, single-file index, fastest, Facebook-backed | Simplicity, version control (commit index to branch) |
  | ChromaDB | Easy API, metadata filtering, persistent storage | Filtering by doc type/domain/status |

  **Why NOT Others (Yet)**

  | Vector DB | Why Deferred |
  |-----------|--------------|
  | Qdrant | Full-featured but overkill for local CLI |
  | Pinecone | Cloud-hosted, adds external dependency |
  | Weaviate | Heavy, more suited for production services |
  | Milvus | Enterprise-scale, too complex for Phase 0 |
  | LanceDB | Promising but newer, less battle-tested |

  **Decision Matrix**

  | Criteria | FAISS | ChromaDB |
  |----------|-------|----------|
  | Setup complexity | Lower | Low |
  | Metadata filtering | Manual | Built-in |
  | Index portability | Single file | Directory |
  | Query speed | Fastest | Fast |
  | LlamaIndex support | Yes | Yes |
  | Phase 0 fit | Yes | Yes |

  **Final Recommendation**

  **Phase 0:** Start with **ChromaDB** - slightly easier API and metadata filtering will help when querying by doc type (GOV-*, ADR-*, PRD-*).

  **If scaling concerns emerge:** Evaluate alternatives using the [Superlinked Vector DB Comparison](https://superlinked.com/vector-db-comparison).

- User / 2026-01-27: What is reranking?

- Claude Opus 4.5 / 2026-01-27: **Reranking Explained**

  Reranking is a two-stage retrieval technique that improves precision.

  **The Problem Reranking Solves**

  | Stage | What Happens | Limitation |
  |-------|--------------|------------|
  | Initial Retrieval | Fast vector search, returns top-50 | Speed optimized, not precision optimized |
  | Problem | Some irrelevant results sneak into top-k | Bi-encoder sees query and doc separately |

  **How Reranking Works**

  ```
  TWO-STAGE RETRIEVAL

  Stage 1: RETRIEVAL (Fast, Broad)
    Query and Doc encoded SEPARATELY (bi-encoder)
    Compare via cosine similarity
    Returns: Top 50 candidates (fast but imprecise)

  Stage 2: RERANKING (Slow, Precise)
    Query + Doc fed TOGETHER into cross-encoder
    Model sees both at once, understands relationship
    Returns: Top 5 reranked (precise but slow)
  ```

  **Bi-Encoder vs Cross-Encoder**

  | Type | How It Works | Speed | Precision |
  |------|--------------|-------|-----------|
  | Bi-Encoder | Query and doc encoded separately, compared via cosine | Fast (precompute doc embeddings) | Good |
  | Cross-Encoder | Query + doc fed together into model | Slow (must run for each pair) | Better |

  **Why Cross-Encoder is More Precise**

  ```
  Query: "What are the testing requirements?"

  Bi-Encoder (Stage 1):
    - Encodes "testing requirements" → vector
    - Compares to pre-computed doc vectors
    - Can't see word interactions between query and doc

  Cross-Encoder (Stage 2):
    - Input: "[CLS] What are testing requirements? [SEP] GOV-0017 defines TDD... [SEP]"
    - Model sees BOTH together, understands relationship
    - Outputs: 0.94 relevance score
  ```

  **When to Use Reranking**

  | Scenario | Use Reranking? |
  |----------|----------------|
  | Phase 0 prototype | No - adds complexity |
  | Top-k results feel imprecise | Yes |
  | High-stakes queries (production) | Yes |
  | Large corpus (100k+ docs) | Yes - retrieval casts wide net, reranker filters |

  **Implementation with LlamaIndex**

  ```python
  from llama_index.core.postprocessor import SentenceTransformerRerank

  # Cross-encoder model for reranking
  reranker = SentenceTransformerRerank(
      model="cross-encoder/ms-marco-MiniLM-L-6-v2",  # Fast reranker
      top_n=5  # Final top-k after reranking
  )

  # Query with reranking
  query_engine = index.as_query_engine(
      similarity_top_k=20,            # Stage 1: retrieve 20
      node_postprocessors=[reranker]  # Stage 2: rerank to top 5
  )
  ```

  **Popular Reranking Models**

  | Model | Speed | Quality | Use Case |
  |-------|-------|---------|----------|
  | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Fast | Good | Phase 1 |
  | `cross-encoder/ms-marco-TinyBERT-L-2-v2` | Fastest | Okay | Low latency |
  | `BAAI/bge-reranker-base` | Medium | Better | Production |
  | `BAAI/bge-reranker-large` | Slow | Best | High precision |

  **Cost/Benefit Summary**

  | Aspect | Without Reranking | With Reranking |
  |--------|-------------------|----------------|
  | Latency | ~50ms | ~150-300ms |
  | Precision | Good | Better |
  | Complexity | Simple | +1 model to manage |
  | Phase 0 fit | Yes | No (defer to Phase 1) |

  **Decision:** Skip reranking in Phase 0. Dense retrieval is good enough to prove value. Add in Phase 1 if retrieval quality becomes an issue.

- User / 2026-01-27: What about Neon for PostgreSQL and pgvector - what is that relationship?

- Claude Opus 4.5 / 2026-01-27: **Neon + PostgreSQL + pgvector Explained**

  This is about using PostgreSQL as a vector database:

  **The Stack**

  ```
  ┌─────────────────────────────────────────┐
  │              NEON                       │  ← Serverless PostgreSQL provider
  ├─────────────────────────────────────────┤
  │            PostgreSQL                   │  ← The database
  ├─────────────────────────────────────────┤
  │            pgvector                     │  ← Extension that adds vector support
  └─────────────────────────────────────────┘
  ```

  **What Each Component Is**

  | Component | What It Is | Role |
  |-----------|------------|------|
  | PostgreSQL | Relational database | The foundation - stores your data |
  | pgvector | PostgreSQL extension | Adds vector data type + similarity search |
  | Neon | Serverless Postgres provider | Hosts PostgreSQL with pgvector pre-installed |

  **Why This Matters for RAG**

  | Approach | Pros | Cons |
  |----------|------|------|
  | Separate Vector DB (ChromaDB/FAISS) | Purpose-built, fast | Another system to manage |
  | pgvector | Single database for everything | Slightly slower for pure vector ops |

  **pgvector Capabilities**

  ```sql
  -- Enable the extension
  CREATE EXTENSION vector;

  -- Create table with vector column
  CREATE TABLE documents (
      id SERIAL PRIMARY KEY,
      content TEXT,
      file_path TEXT,
      doc_type TEXT,  -- GOV, ADR, PRD
      embedding vector(384)  -- 384 dimensions for MiniLM
  );

  -- Create index for fast similarity search
  CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);

  -- Query: find similar documents
  SELECT file_path, content,
         1 - (embedding <=> query_embedding) AS similarity
  FROM documents
  ORDER BY embedding <=> query_embedding
  LIMIT 5;
  ```

  **Why Neon Specifically?**

  | Feature | Benefit |
  |---------|---------|
  | Serverless | Scale to zero, pay for usage |
  | pgvector pre-installed | No extension setup needed |
  | Branching | Database branches like git (great for testing) |
  | Free tier | Generous for prototyping |
  | LlamaIndex integration | Native support |

  **Comparison: ChromaDB vs Neon/pgvector**

  | Criteria | ChromaDB | Neon + pgvector |
  |----------|----------|-----------------|
  | Setup | Local, simple | Cloud, account needed |
  | Cost | Free (local) | Free tier, then usage-based |
  | Metadata filtering | Built-in | SQL (more powerful) |
  | Joins with other data | No | Yes (it's PostgreSQL!) |
  | Scaling | Manual | Automatic (serverless) |
  | Phase 0 fit | Simpler | More setup |
  | Phase 2+ fit | May need migration | Production-ready |

  **LlamaIndex + Neon Example**

  ```python
  from llama_index.vector_stores.postgres import PGVectorStore
  from sqlalchemy import make_url

  # Connect to Neon
  connection_string = "postgresql://user:pass@ep-cool-name.us-east-2.aws.neon.tech/governance"
  url = make_url(connection_string)

  vector_store = PGVectorStore.from_params(
      database=url.database,
      host=url.host,
      password=url.password,
      port=url.port,
      user=url.username,
      table_name="governance_docs",
      embed_dim=384,  # MiniLM dimensions
  )
  ```

  **Decision for This PRD**

  | Phase | Recommendation |
  |-------|----------------|
  | Phase 0 | ChromaDB (local, simple, no account needed) |
  | Phase 1 | Evaluate Neon if cloud deployment needed |
  | Phase 2 | Neon + pgvector for production (SQL power + serverless) |

  **Bottom Line:** pgvector = PostgreSQL extension for vector search. Neon = serverless PostgreSQL host with pgvector built-in. Together = production-grade vector DB with full SQL power. For Phase 0, stick with ChromaDB. Consider Neon + pgvector for Phase 2.

- User / 2026-01-27: Do we have to use OpenAI API? If we go with the free model and integrate knowledge graph into Phase 0, what would that look like?

- Claude Opus 4.5 / 2026-01-27: **Phase 0 Implementation Plan - Fully Free/Local Stack**

  No OpenAI required. Here's the complete implementation with Ollama (free, local).

  **LLM Options for Entity Extraction**

  | Provider | Model | Local? | Cost |
  |----------|-------|--------|------|
  | OpenAI | gpt-4o-mini | No | ~$0.01/doc |
  | Anthropic | Claude Haiku | No | ~$0.01/doc |
  | Ollama | llama3.1:8b | Yes | Free |
  | Groq | llama3-70b | No | Free tier |

  **Phase 0 Stack (Fully Free)**

  ```
  ┌─────────────────────────────────────────────────────────────┐
  │              PHASE 0 - FULLY LOCAL STACK                    │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
  │  │   Ollama    │  │  ChromaDB   │  │   Neo4j     │         │
  │  │  (LLM)      │  │  (Vectors)  │  │  (Graph)    │         │
  │  │             │  │             │  │             │         │
  │  │ llama3.1:8b │  │  Local DB   │  │  Docker     │         │
  │  │ + nomic-    │  │             │  │             │         │
  │  │   embed     │  │             │  │             │         │
  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
  │         │                │                │                 │
  │         └────────────────┼────────────────┘                 │
  │                          │                                  │
  │                          ▼                                  │
  │              ┌───────────────────────┐                      │
  │              │   Governance RAG CLI  │                      │
  │              │   gov-rag query "..." │                      │
  │              └───────────────────────┘                      │
  │                                                             │
  │  Cost: $0        Privacy: 100% Local                        │
  └─────────────────────────────────────────────────────────────┘
  ```

  **Prerequisites**

  ```bash
  # Docker (for Neo4j)
  brew install docker

  # Ollama (for LLM + embeddings)
  brew install ollama

  # Python 3.10+
  python --version
  ```

  **Setup Script**

  ```bash
  #!/bin/bash
  # scripts/setup-rag.sh

  set -e
  echo "=== Setting up Governance RAG (Phase 0) ==="

  # 1. Start Neo4j
  docker run -d \
    --name goldenpath-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/goldenpath123 \
    -e NEO4J_PLUGINS='["apoc"]' \
    -v neo4j_data:/data \
    neo4j:5.13.0

  # 2. Pull Ollama models
  ollama pull llama3.1:8b
  ollama pull nomic-embed-text

  # 3. Create Python environment
  python -m venv .venv-rag
  source .venv-rag/bin/activate
  pip install -r requirements-rag.txt

  # 4. Initialize the index
  python scripts/rag/build_index.py

  echo "=== Setup complete! ==="
  ```

  **Dependencies (requirements-rag.txt)**

  ```
  llama-index>=0.10
  graphiti-core>=0.3
  chromadb>=0.4
  neo4j>=5.0
  ollama>=0.1
  llama-index-llms-ollama
  llama-index-embeddings-ollama
  pydantic>=2.0
  pyyaml
  click
  rich
  ```

  **Project Structure**

  ```
  scripts/rag/
  ├── __init__.py
  ├── build_index.py       # Index governance docs
  ├── query.py             # Query interface
  ├── config.py            # Configuration
  └── cli.py               # CLI wrapper
  ```

  **Core Config (config.py)**

  ```python
  from dataclasses import dataclass
  from pathlib import Path

  @dataclass
  class RAGConfig:
      docs_root: Path = Path("docs")
      index_path: Path = Path(".rag-index")
      neo4j_uri: str = "bolt://localhost:7687"
      neo4j_user: str = "neo4j"
      neo4j_password: str = "goldenpath123"
      ollama_base_url: str = "http://localhost:11434"
      llm_model: str = "llama3.1:8b"
      embed_model: str = "nomic-embed-text"
      top_k: int = 5
      include_patterns: list = None

      def __post_init__(self):
          self.include_patterns = [
              "docs/10-governance/**/*.md",
              "docs/20-contracts/**/*.md",
              "docs/adrs/**/*.md",
          ]
  ```

  **Makefile Targets**

  ```makefile
  rag-setup:    ## Setup RAG infrastructure
  	@./scripts/setup-rag.sh

  rag-index:    ## Build/rebuild RAG index
  	@source .venv-rag/bin/activate && python scripts/rag/cli.py index

  rag-query:    ## Query RAG (usage: make rag-query Q="question")
  	@source .venv-rag/bin/activate && python scripts/rag/cli.py ask $(Q)

  rag-status:   ## Check RAG system status
  	@source .venv-rag/bin/activate && python scripts/rag/cli.py status
  ```

  **Example Usage**

  ```bash
  # One-time setup
  make rag-setup

  # Build index
  make rag-index

  # Query
  make rag-query Q="What are the TDD requirements?"
  make rag-query Q="What depends on GOV-0017?"
  ```

  **Example Output**

  ```
  Query: What testing framework is required for Terraform modules?

  ╭─────────────── Vector Search Results ───────────────╮
  │ Score │ Source                    │ Preview         │
  │ 0.847 │ docs/10-governance/GOV-.. │ Terraform mod.. │
  │ 0.823 │ docs/adrs/ADR-0182-tdd..  │ All infra co.. │
  ╰─────────────────────────────────────────────────────╯

  ╭─────────────── Knowledge Graph Results ─────────────╮
  │ Entity          │ Fact                              │
  │ terraform_test  │ Required framework for TF modules │
  │ GOV-0017        │ Defines TDD policy                │
  ╰─────────────────────────────────────────────────────╯

  ╭───────────────────── Answer ────────────────────────╮
  │ Terraform modules require **terraform test** using  │
  │ `.tftest.hcl` files. Defined in [GOV-0017].        │
  ╰─────────────────────────────────────────────────────╯
  ```

  **Implementation Timeline**

  | Day | Task |
  |-----|------|
  | Day 1 | Setup script, Docker Neo4j, Ollama models |
  | Day 2 | build_index.py, test with 5 docs |
  | Day 3 | query.py, CLI, Makefile targets |
  | Day 4 | Index all governance docs, tune retrieval |
  | Day 5 | Documentation, team demo |

  **Cost Summary**

  | Component | Cost |
  |-----------|------|
  | Neo4j (Docker) | Free |
  | Ollama (llama3.1 + nomic-embed) | Free |
  | ChromaDB | Free |
  | **Total** | **$0** |

  **What This Delivers**

  | Capability | Included |
  |------------|----------|
  | Vector search (semantic) | Yes |
  | Knowledge graph (relationships) | Yes |
  | Multi-hop queries | Yes |
  | Citation-backed answers | Yes |
  | Fully local/private | Yes |
  | Zero cloud costs | Yes |

  This is aggressive Phase 0 - full hybrid RAG (vector + knowledge graph) from day one with zero cloud dependencies.

- User / 2026-01-27: Where does multi-query expansion fit in, what is it?

- Claude Opus 4.5 / 2026-01-27: **Multi-Query Expansion (Deferred to Phase 1)**

  Multi-query expansion generates multiple variations of a user query, runs all against the retriever, and merges results for better recall.

  **How It Works**

  ```
  User query: "How do I test Terraform modules?"
                    │
                    ▼
            LLM Expansion
                    │
                    ▼
  ┌─────────────────────────────────────────────┐
  │ Query 1: "How do I test Terraform modules?" │
  │ Query 2: "terraform test framework"         │
  │ Query 3: "tftest.hcl files how to write"    │
  │ Query 4: "GOV testing requirements infra"   │
  └─────────────────────────────────────────────┘
                    │
                    ▼
          Run ALL queries
                    │
                    ▼
        Merge & Dedupe Results
                    │
                    ▼
          Better Coverage
  ```

  **Why It Helps**

  | Problem | How Multi-Query Solves It |
  |---------|---------------------------|
  | User says "TDD", docs say "testing policy" | Generates "testing policy" as variant |
  | Single query misses edge cases | Multiple angles = better recall |
  | Vocabulary mismatch | Different phrasings cover more ground |

  **LlamaIndex Implementation**

  ```python
  from llama_index.core.retrievers import QueryFusionRetriever

  retriever = QueryFusionRetriever(
      retrievers=[vector_retriever, bm25_retriever],
      llm=llm,
      num_queries=4,
      mode="reciprocal_rerank",
      use_async=True,
  )
  ```

  **Comparison**

  | Metric | Single Query | Multi-Query |
  |--------|--------------|-------------|
  | Recall | Good | Better |
  | Latency | ~50ms | ~150ms |
  | Complexity | Simple | Medium |

  **Decision:** Defer to Phase 1. Get baseline working first, add if recall is poor. Easy to toggle on later.

- User / 2026-01-27: What about contextual retrieval?

- Claude Opus 4.5 / 2026-01-27: **Contextual Retrieval Explained**

  Contextual retrieval (introduced by Anthropic) adds document context to each chunk BEFORE embedding, dramatically improving retrieval accuracy.

  **The Problem with Standard Chunking**

  ```
  Original document: GOV-0017-tdd-and-determinism.md
  ─────────────────────────────────────────────────
  # TDD Policy

  ## Scope
  This policy applies to all infrastructure code.

  ## Requirements
  All parsers must have unit tests.
  Coverage threshold is 60%.
  ─────────────────────────────────────────────────

  Standard chunking produces:
  ┌─────────────────────────────────────┐
  │ Chunk 1: "# TDD Policy\n\n## Scope" │  ← Has context
  └─────────────────────────────────────┘
  ┌─────────────────────────────────────┐
  │ Chunk 2: "All parsers must have     │  ← LOST context!
  │           unit tests. Coverage      │     What doc?
  │           threshold is 60%."        │     What section?
  └─────────────────────────────────────┘
  ```

  **Contextual Retrieval Solution**

  ```
  Before embedding, prepend context to each chunk:

  ┌─────────────────────────────────────────────────────────┐
  │ "This chunk is from GOV-0017-tdd-and-determinism.md,   │
  │  a governance policy about Test-Driven Development.    │
  │  It appears in the 'Requirements' section.             │
  │                                                        │
  │  All parsers must have unit tests. Coverage threshold  │
  │  is 60%."                                              │
  └─────────────────────────────────────────────────────────┘

  Now the embedding captures:
  ✓ Document identity (GOV-0017)
  ✓ Document purpose (TDD governance)
  ✓ Section context (Requirements)
  ✓ The actual content
  ```

  **How It Works**

  ```
  ┌─────────────────────────────────────────────────────────────┐
  │                 CONTEXTUAL RETRIEVAL                        │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  1. CHUNK DOCUMENT                                          │
  │     Split into semantic chunks                              │
  │                                                             │
  │  2. GENERATE CONTEXT (LLM call per chunk)                   │
  │     "Describe this chunk's context in the document"         │
  │                                                             │
  │  3. PREPEND CONTEXT                                         │
  │     context + "\n\n" + chunk_content                        │
  │                                                             │
  │  4. EMBED THE CONTEXTUALIZED CHUNK                          │
  │     Now embedding includes document context                 │
  │                                                             │
  │  5. STORE WITH METADATA                                     │
  │     chunk, context, file_path, section, doc_type            │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
  ```

  **Anthropic's Results**

  | Method | Retrieval Failure Rate |
  |--------|------------------------|
  | Standard chunking | 5.7% |
  | + Contextual retrieval | 1.9% (67% reduction) |
  | + Contextual + BM25 hybrid | 1.3% (77% reduction) |

  **Implementation**

  ```python
  from llama_index.core.node_parser import SentenceSplitter
  from llama_index.llms.ollama import Ollama

  llm = Ollama(model="llama3.1:8b")

  def add_context_to_chunk(chunk: str, doc_metadata: dict) -> str:
      """Use LLM to generate context for chunk."""
      prompt = f"""
      Document: {doc_metadata['file_path']}
      Document type: {doc_metadata['doc_type']}
      Full document summary: {doc_metadata.get('summary', 'N/A')}

      Given the above document context, write a brief (2-3 sentence)
      description that situates this chunk within the document:

      Chunk:
      {chunk[:500]}

      Context description:
      """
      response = llm.complete(prompt)
      return f"{response.text}\n\n{chunk}"

  # During indexing
  for chunk in chunks:
      contextualized = add_context_to_chunk(chunk.text, chunk.metadata)
      chunk.text = contextualized  # Replace with contextualized version
  ```

  **Cost Consideration**

  | Aspect | Impact |
  |--------|--------|
  | Indexing time | Slower (LLM call per chunk) |
  | Index size | ~20% larger (context text) |
  | Query time | Same |
  | Accuracy | Significantly better |

  With Ollama (free), the only cost is indexing time.

  **When to Use**

  | Scenario | Use Contextual Retrieval? |
  |----------|---------------------------|
  | Documents have clear structure | Yes - context helps a lot |
  | Chunks lose meaning in isolation | Yes |
  | Speed-critical indexing | No - adds latency |
  | Small corpus (<100 docs) | Optional |
  | Large corpus with varied docs | Yes |

  **Governance Docs = Perfect Fit**

  Your docs have:
  - Clear document types (GOV, ADR, PRD, EC)
  - Structured sections (Scope, Requirements, etc.)
  - Cross-references between docs
  - Chunks that need document context

  **Simplified Alternative: Template-Based Context**

  Instead of LLM-generated context, use templates:

  ```python
  def template_context(chunk, metadata):
      return f"""
      Source: {metadata['file_path']}
      Type: {metadata['doc_type']}
      Section: {metadata.get('section', 'Unknown')}

      {chunk}
      """
  ```

  Faster (no LLM call), still helpful, good for Phase 0.

  **Phase Recommendation**

  | Phase | Approach |
  |-------|----------|
  | Phase 0 | Template-based context (fast, no LLM overhead) |
  | Phase 1 | LLM-generated context if accuracy needs boost |
  | Phase 2 | Full contextual + BM25 hybrid |

  **Decision:** Use template-based contextual retrieval in Phase 0 (free, fast, helpful). Upgrade to LLM-generated context in Phase 1 if needed.

- User / 2026-01-27: What is context-aware chunking?

- Claude Opus 4.5 / 2026-01-27: **Context-Aware Chunking Explained**

  Context-aware chunking splits documents intelligently based on structure and meaning, not arbitrary character counts.

  **The Problem with Naive Chunking**

  ```
  Standard chunking (fixed size = 500 chars):

  # TDD Policy

  ## Scope
  This policy applies to all infrastructure code
  including Terraform modules, Python scripts, and
  ─────────────── CHUNK BOUNDARY ───────────────  ← BAD!
  shell scripts. Exceptions require approval.

  Problems:
  ├── Cuts mid-sentence
  ├── Cuts mid-section
  ├── Loses header context
  └── Chunks don't represent complete ideas
  ```

  **Context-Aware Chunking Solution**

  ```
  ┌─────────────────────────────────────────────┐
  │ Chunk 1: SCOPE SECTION (complete)           │
  │ # TDD Policy                                │
  │ ## Scope                                    │
  │ This policy applies to all infrastructure   │
  │ code including Terraform modules...         │
  └─────────────────────────────────────────────┘
             ↓ Clean break at section boundary
  ┌─────────────────────────────────────────────┐
  │ Chunk 2: REQUIREMENTS SECTION (complete)    │
  │ ## Requirements                             │
  │ All parsers must have unit tests...         │
  └─────────────────────────────────────────────┘
  ```

  **Types of Context-Aware Chunking**

  | Type | How It Works | Best For |
  |------|--------------|----------|
  | Markdown-aware | Split on headers (##, ###) | GOV, ADR, PRD docs |
  | Sentence-based | Split at sentence boundaries | Prose, paragraphs |
  | Semantic | Use embeddings to find topic shifts | Unstructured text |
  | Code-aware | Split on functions/classes | Source code |
  | Recursive | Try large chunks, split smaller if needed | Mixed content |

  **Markdown-Aware Chunking (Perfect for Governance Docs)**

  ```python
  from llama_index.core.node_parser import MarkdownNodeParser

  parser = MarkdownNodeParser()
  nodes = parser.get_nodes_from_documents(documents)

  # Each node contains:
  # - The section content
  # - Header hierarchy (h1 > h2 > h3)
  # - Metadata (file path, section name)
  ```

  **Output Example for GOV-0017:**

  ```
  Node 1:
    metadata: {header_path: "TDD Policy > Scope", level: 2}
    content: "This policy applies to all infrastructure..."

  Node 2:
    metadata: {header_path: "TDD Policy > Requirements", level: 2}
    content: "All parsers must have unit tests..."
  ```

  **Semantic Chunking (Finds Natural Breakpoints)**

  ```python
  from llama_index.core.node_parser import SemanticSplitterNodeParser

  parser = SemanticSplitterNodeParser(
      embed_model=embed_model,
      breakpoint_percentile_threshold=95,
  )
  ```

  Uses embeddings to detect topic shifts - when consecutive sentences have very different embeddings, that's a natural chunk boundary.

  **Recursive Chunking (Best of Both Worlds)**

  ```python
  from llama_index.core.node_parser import SentenceSplitter

  parser = SentenceSplitter(
      chunk_size=1024,
      chunk_overlap=200,
      paragraph_separator="\n\n",
  )
  ```

  Logic: Try whole sections → split at paragraphs → split at sentences. Never cut mid-sentence.

  **Comparison**

  | Method | Pros | Cons | Use When |
  |--------|------|------|----------|
  | Fixed size | Simple | Cuts randomly | Never for docs |
  | Markdown-aware | Respects structure | Only for markdown | GOV, ADR, PRD |
  | Sentence-based | Clean boundaries | May miss topics | Prose |
  | Semantic | Finds natural breaks | Slower | Unstructured |
  | Recursive | Flexible fallback | Complex | Mixed content |

  **Implementation for Governance Docs**

  ```python
  from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter

  def chunk_governance_doc(doc):
      # Step 1: Split by markdown structure
      markdown_parser = MarkdownNodeParser(include_metadata=True)
      nodes = markdown_parser.get_nodes_from_documents([doc])

      # Step 2: Split large sections further
      sentence_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
      final_nodes = []
      for node in nodes:
          if len(node.text) > 512:
              sub_nodes = sentence_splitter.get_nodes_from_documents([node])
              final_nodes.extend(sub_nodes)
          else:
              final_nodes.append(node)

      return final_nodes
  ```

  **Complete Chunking Pipeline**

  ```
  1. MARKDOWN-AWARE CHUNKING
     Split on headers, preserve structure
                 │
                 ▼
  2. SENTENCE FALLBACK
     Split large sections at sentence boundaries
                 │
                 ▼
  3. CONTEXTUAL ENRICHMENT
     Prepend: "Source: GOV-0017, Section: Requirements"
                 │
                 ▼
  4. EMBED & STORE
     Vector store + metadata
  ```

  **Phase 0 Config**

  ```python
  parser = MarkdownNodeParser(
      include_metadata=True,
      include_prev_next_rel=True,
  )
  ```

  **Decision:** Use Markdown-aware chunking for Phase 0 - your docs are all markdown with clear structure. Add sentence fallback for large sections. This gives complete, meaningful chunks without complexity.

- User / 2026-01-27: What is the Docling library?

- Claude Opus 4.5 / 2026-01-27: **Docling - Document Processing Library (Future Consideration)**

  Docling is IBM's open-source document processing library that converts complex documents (PDF, DOCX, PPTX, images) into structured formats optimized for RAG.

  **What Docling Does**

  ```
  INPUT                         OUTPUT
  ─────                         ──────
  PDF, DOCX, PPTX    ────▶     Structured JSON
  Images, HTML                  Markdown
                                Tables preserved
                                Figures extracted
  ```

  **Key Features**

  | Feature | Description |
  |---------|-------------|
  | Layout understanding | Columns, headers, footers |
  | Table extraction | Structure preserved as data |
  | Figure extraction | Images + descriptions |
  | OCR | Scanned document support |
  | Hierarchy detection | Sections, subsections |

  **Why It Matters for RAG**

  | Problem | How Docling Solves It |
  |---------|----------------------|
  | PDFs lose structure | Preserves layout, headers, sections |
  | Tables become garbled | Extracts as structured data |
  | Multi-column confusion | Understands reading order |
  | Scanned docs unreadable | Built-in OCR |

  **Basic Usage**

  ```python
  from docling.document_converter import DocumentConverter

  converter = DocumentConverter()
  result = converter.convert("governance-policy.pdf")

  # Export as markdown (great for RAG)
  markdown = result.document.export_to_markdown()
  ```

  **LlamaIndex Integration**

  ```python
  from llama_index.readers.docling import DoclingReader

  reader = DoclingReader()
  documents = reader.load_data(file_path="docs/")
  ```

  **Comparison with Other Parsers**

  | Parser | PDFs | Tables | OCR | Structure |
  |--------|------|--------|-----|-----------|
  | PyPDF2 | Basic | No | No | No |
  | pdfplumber | Good | Partial | No | Partial |
  | Unstructured | Good | Good | Yes | Good |
  | **Docling** | Excellent | Excellent | Yes | Excellent |

  **Relevance for This Project**

  | Doc Type | Parser |
  |----------|--------|
  | GOV-*.md, ADR-*.md, PRD-*.md | MarkdownNodeParser |
  | External PDFs | Docling |
  | Confluence exports | Docling |
  | Architecture diagrams | Docling |

  **Phase Decision**

  | Phase | Docling Use |
  |-------|-------------|
  | Phase 0 | Skip - all docs are markdown |
  | Phase 1 | Add if ingesting external PDFs |
  | Phase 2 | Required for multi-source federation |

  **Installation (When Needed)**

  ```bash
  pip install docling llama-index-readers-docling
  ```

  **Decision:** Not needed for Phase 0 - governance docs are already markdown. Add Docling when ingesting external PDFs, Confluence exports, or vendor compliance documents.

- User / 2026-01-27: What is hierarchical RAG?

- Claude Opus 4.5 / 2026-01-27: **Hierarchical RAG Explained**

  Hierarchical RAG creates multi-level summaries of documents, enabling retrieval at different granularity levels - from high-level concepts down to specific details.

  **The Problem with Flat RAG**

  ```
  Query: "What is the overall testing philosophy?"

  Flat RAG returns:
  ├── Chunk about coverage thresholds
  ├── Chunk about pytest fixtures
  └── Chunk about terraform test

  Problem: Scattered details, missing the "big picture"
  ```

  **Hierarchical RAG Solution**

  ```
  Level 3: CORPUS SUMMARY
           "The governance framework defines TDD as mandatory..."
                              │
                              ▼
  Level 2: DOCUMENT SUMMARIES
           ┌───────────┐ ┌───────────┐ ┌───────────┐
           │ GOV-0017  │ │ ADR-0182  │ │ GOV-0016  │
           │ summary   │ │ summary   │ │ summary   │
           └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                 │             │             │
                 ▼             ▼             ▼
  Level 1: SECTION SUMMARIES
           ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
           │Scope│ │Reqs │ │Tools│ │CI   │
           └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
              │       │       │       │
              ▼       ▼       ▼       ▼
  Level 0: RAW CHUNKS
           ┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐┌──┐
           │  ││  ││  ││  ││  ││  ││  ││  │
           └──┘└──┘└──┘└──┘└──┘└──┘└──┘└──┘
  ```

  **How It Works**

  | Query Type | Retrieved Level | Example |
  |------------|-----------------|---------|
  | High-level | Level 2-3 summaries | "What's the testing philosophy?" |
  | Specific | Level 0-1 chunks | "What's the coverage threshold?" |
  | Mixed | Multiple levels | "Explain TDD requirements in detail" |

  **RAPTOR Algorithm (Popular Implementation)**

  ```
  1. CHUNK documents (Level 0)
  2. CLUSTER similar chunks by embedding
  3. SUMMARIZE each cluster with LLM (Level 1)
  4. REPEAT: cluster summaries → summarize → Level 2
  5. Continue until single root summary
  6. INDEX all levels (chunks + all summaries)
  ```

  **LlamaIndex Implementation**

  ```python
  from llama_index.packs.raptor import RaptorPack

  raptor = RaptorPack(
      documents=documents,
      llm=llm,
      embed_model=embed_model,
      tree_depth=3,
  )

  # Query traverses the tree
  response = raptor.run("What is the overall testing philosophy?")
  ```

  **Natural Hierarchy for Governance Docs**

  ```
  Level 3: All governance docs summary
           │
           ├── Level 2: GOV-* summary (policies)
           │            ├── GOV-0017 (TDD)
           │            └── GOV-0016 (Testing stack)
           │
           ├── Level 2: ADR-* summary (decisions)
           │
           └── Level 2: PRD-* summary (requirements)
  ```

  **Comparison: Flat vs Hierarchical**

  | Aspect | Flat RAG | Hierarchical RAG |
  |--------|----------|------------------|
  | Index size | Smaller | Larger (summaries) |
  | Build time | Faster | Slower (LLM calls) |
  | High-level queries | Poor | Excellent |
  | Detail queries | Good | Good |
  | Complexity | Simple | Medium |

  **When to Use**

  | Scenario | Use Hierarchical? |
  |----------|-------------------|
  | Small corpus (<50 docs) | Optional |
  | Large corpus (100+ docs) | Yes |
  | "What/why" questions | Yes |
  | Specific lookups only | No |

  **Phase Recommendation**

  | Phase | Approach |
  |-------|----------|
  | Phase 0 | Flat RAG (prove basic value) |
  | Phase 1 | Add document-level summaries |
  | Phase 2 | Full RAPTOR hierarchy |

  **Decision:** Defer to Phase 1+. Hierarchical RAG requires LLM calls during indexing to generate summaries. Better to prove flat RAG works first, then add hierarchy if users frequently ask high-level questions.

- User / 2026-01-27: What is agentic RAG?

- Claude Opus 4.5 / 2026-01-27: **Agentic RAG Explained**

  Agentic RAG is when an AI agent actively orchestrates the retrieval process - deciding what to search, evaluating results, and iterating until it has enough information to answer.

  **Standard RAG vs Agentic RAG**

  ```
  STANDARD RAG:
  User Query ──▶ Retrieve ──▶ Generate Answer
  (Single pass, fixed query, hope for the best)

  AGENTIC RAG:
  User Query
       │
       ▼
  ┌─────────────────────────────────────────┐
  │              AGENT LOOP                 │
  │                                         │
  │  1. REASON: What do I need?             │
  │       │                                 │
  │       ▼                                 │
  │  2. RETRIEVE: Search vector/graph       │
  │       │                                 │
  │       ▼                                 │
  │  3. EVALUATE: Enough? Relevant?         │
  │       │                                 │
  │       ├── NO ──▶ Reformulate, retry     │
  │       │                                 │
  │       ▼                                 │
  │  4. SYNTHESIZE: Combine and answer      │
  └─────────────────────────────────────────┘
  ```

  **Key Capabilities**

  | Capability | Standard RAG | Agentic RAG |
  |------------|--------------|-------------|
  | Query reformulation | No | Yes |
  | Multi-step retrieval | No | Yes |
  | Tool selection | No | Yes |
  | Result evaluation | No | Yes |
  | Self-correction | No | Yes |

  **Example: Complex Query**

  ```
  Query: "What testing is required for EKS and who owns it?"

  STANDARD RAG:
    Single search → Mixed chunks → Incomplete answer

  AGENTIC RAG:
    Step 1: Search "EKS testing requirements"
            Found: GOV-0017 says terraform test required

    Step 2: Search "EKS module owner"
            Found: Nothing clear

    Step 3: Reformulate: "aws_eks CODEOWNERS"
            Found: platform-team owns modules/aws_eks

    Step 4: Synthesize complete answer
  ```

  **ReAct Pattern (Reasoning + Acting)**

  ```
  THOUGHT 1: I need testing requirements for EKS.
  ACTION 1:  vector_search("EKS testing requirements")
  OBSERVATION 1: Found GOV-0017 mentions TDD policy.

  THOUGHT 2: Let me check Terraform-specific requirements.
  ACTION 2:  lookup_doc("GOV-0017")
  OBSERVATION 2: "Terraform modules use terraform test"

  THOUGHT 3: I have enough info.
  ACTION 3:  FINISH
  ANSWER:    "EKS requires terraform test per GOV-0017"
  ```

  **Implementation with LlamaIndex**

  ```python
  from llama_index.core.agent import ReActAgent
  from llama_index.core.tools import QueryEngineTool, FunctionTool

  # Define tools
  vector_tool = QueryEngineTool.from_defaults(
      query_engine=vector_index.as_query_engine(),
      name="vector_search",
      description="Search governance docs semantically"
  )

  graph_tool = QueryEngineTool.from_defaults(
      query_engine=knowledge_graph.as_query_engine(),
      name="graph_search",
      description="Find entity relationships"
  )

  # Create agent
  agent = ReActAgent.from_tools(
      tools=[vector_tool, graph_tool],
      llm=llm,
      max_iterations=10,
      verbose=True,
  )

  # Agent orchestrates retrieval
  response = agent.chat(
      "Compare testing requirements for Python vs Terraform"
  )
  ```

  **Agentic RAG Patterns**

  | Pattern | Description | Use Case |
  |---------|-------------|----------|
  | ReAct | Reason → Act → Observe → Repeat | General purpose |
  | Self-RAG | Retrieve → Critique → Re-retrieve | High accuracy |
  | Corrective RAG | Retrieve → Evaluate → Correct | Error recovery |
  | Adaptive RAG | Route to best strategy | Multi-source |

  **Cost Consideration**

  | Aspect | Standard RAG | Agentic RAG |
  |--------|--------------|-------------|
  | LLM calls/query | 1 | 3-10+ |
  | Latency | ~1 sec | ~5-15 sec |
  | With Ollama | Free | Free (slower) |
  | Accuracy | Good | Better |

  **When to Use**

  | Scenario | Standard | Agentic |
  |----------|----------|---------|
  | Simple lookups | ✅ | Overkill |
  | Multi-part questions | ❌ | ✅ |
  | High accuracy needed | ⚠️ | ✅ |
  | Speed critical | ✅ | ❌ |
  | Multiple sources | ⚠️ | ✅ |

  **Phase Recommendation**

  | Phase | Approach |
  |-------|----------|
  | Phase 0 | Standard RAG (prove basic retrieval) |
  | Phase 1 | Simple agent with 2-3 tools |
  | Phase 2 | Full ReAct agent with correction |

  **Decision:** Defer to Phase 1+. Agentic RAG adds latency and complexity. Nail basic retrieval first, then add agent orchestration when users need complex multi-step answers.

- User / 2026-01-27: What is LanceDB?

- Claude Opus 4.5 / 2026-01-27: **LanceDB - Alternative Vector Database**

  LanceDB is a serverless, embedded vector database built on the Lance columnar format. Gaining popularity as a lightweight alternative to ChromaDB/FAISS.

  **Key Characteristics**

  ```
  • Serverless - no separate process to run
  • Embedded - runs in your application process
  • Lance format - columnar storage optimized for ML
  • Zero-copy - fast data access
  • Multi-modal - vectors, text, images in same table
  ```

  **LanceDB vs Other Vector DBs**

  | Feature | LanceDB | ChromaDB | FAISS | Pinecone |
  |---------|---------|----------|-------|----------|
  | Serverless | Yes | No (server) | Yes | No (cloud) |
  | Embedded | Yes | Yes | Yes | No |
  | Multi-modal | Yes | No | No | No |
  | SQL filtering | Yes | Yes | Manual | Yes |
  | Cloud option | Yes | No | No | Yes |
  | Cost | Free | Free | Free | Paid |

  **Key Advantages**

  | Advantage | Description |
  |-----------|-------------|
  | Zero config | `pip install lancedb` and go |
  | No server | Runs in-process, no Docker needed |
  | Multi-modal | Store vectors + images + text together |
  | SQL filtering | `WHERE doc_type = 'GOV'` built-in |
  | Versioning | Time-travel queries |

  **Basic Usage**

  ```python
  import lancedb

  # Connect (creates local directory)
  db = lancedb.connect("./governance-db")

  # Create table
  data = [
      {"text": "TDD is required", "doc_type": "GOV", "file": "GOV-0017.md"},
      {"text": "Coverage is 60%", "doc_type": "GOV", "file": "GOV-0017.md"},
  ]
  table = db.create_table("governance", data)

  # Search with filtering
  results = table.search("testing requirements") \
      .where("doc_type = 'GOV'") \
      .limit(5) \
      .to_pandas()
  ```

  **LlamaIndex Integration**

  ```python
  from llama_index.vector_stores.lancedb import LanceDBVectorStore

  vector_store = LanceDBVectorStore(
      uri="./governance-db",
      table_name="governance",
  )
  ```

  **When to Choose LanceDB**

  | Scenario | LanceDB? | Why |
  |----------|----------|-----|
  | Simple local RAG | Yes | Zero setup |
  | Multi-modal (images) | Yes | Native support |
  | Serverless deploy | Yes | No infra |
  | Large scale (millions) | Maybe | Consider Qdrant |
  | Already using ChromaDB | Maybe | Migration effort |

  **Trade-off vs ChromaDB**

  | Aspect | ChromaDB | LanceDB |
  |--------|----------|---------|
  | Maturity | More mature | Newer |
  | Community | Larger | Growing |
  | Setup | Needs server | Embedded |
  | Multi-modal | No | Yes |
  | Filtering | Good | Better (SQL) |

  **Phase Consideration**

  | Phase | Recommendation |
  |-------|----------------|
  | Phase 0 | Stick with ChromaDB (already decided) |
  | Phase 1 | Evaluate if multi-modal needed |
  | Future | Consider for diagrams/images |

  **Decision:** Keep ChromaDB for Phase 0. Consider LanceDB if you need to index architecture diagrams or images alongside text in future phases.

- User / 2026-01-27: Compare Arize Phoenix vs LangSmith

- Claude Opus 4.5 / 2026-01-27: **LLM Observability: Arize Phoenix vs LangSmith**

  These are observability platforms for monitoring, debugging, and evaluating RAG pipelines.

  **What They Do**

  ```
  Your RAG Pipeline
       │
       ▼
  Query → Embed → Retrieve → Generate → Response
       │       │         │          │
       └───────┴─────────┴──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   OBSERVABILITY     │
              │   • Trace each step │
              │   • Latency metrics │
              │   • Token usage     │
              │   • Retrieval quality│
              └─────────────────────┘
  ```

  **Comparison**

  | Aspect | Arize Phoenix | LangSmith |
  |--------|---------------|-----------|
  | Company | Arize AI | LangChain |
  | Open Source | Yes (Apache 2.0) | No |
  | Self-hosted | Yes | No (cloud only) |
  | Free tier | Unlimited local | Limited |
  | Cost | Free (self-host) | Usage-based |
  | Framework lock-in | None | LangChain-centric |
  | LlamaIndex support | Native | Via callback |

  **Feature Comparison**

  | Feature | Phoenix | LangSmith |
  |---------|---------|-----------|
  | Trace visualization | Yes | Yes |
  | Latency tracking | Yes | Yes |
  | Token counting | Yes | Yes |
  | Embedding analysis | Yes | Limited |
  | Retrieval evaluation | Yes | Yes |
  | Self-hosted | Yes | No |
  | Privacy (local data) | Yes | No (cloud) |
  | Team collaboration | Limited | Yes |

  **Phoenix Setup**

  ```bash
  pip install arize-phoenix openinference-instrumentation-llama-index
  ```

  ```python
  import phoenix as px
  from phoenix.otel import register
  from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

  # Launch Phoenix UI
  px.launch_app()

  # Instrument LlamaIndex (auto-traces all calls)
  tracer_provider = register()
  LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

  # View traces at http://localhost:6006
  ```

  **What You See**

  ```
  TRACE: "What are the TDD requirements?"

  ├── query (45ms)
  │   └── input: "What are the TDD requirements?"
  │
  ├── embedding (12ms)
  │   └── model: nomic-embed-text
  │
  ├── retrieval (23ms)
  │   └── top_k: 5
  │   └── GOV-0017.md (score: 0.89)
  │   └── ADR-0182.md (score: 0.76)
  │
  └── llm (1.2s)
      └── model: llama3.1:8b
      └── tokens: 847 in, 156 out
  ```

  **Recommendation**

  | Criteria | Winner |
  |----------|--------|
  | Open source | Phoenix |
  | Self-hosted/private | Phoenix |
  | Free | Phoenix |
  | LlamaIndex native | Phoenix |
  | UI polish | LangSmith |
  | Team features | LangSmith |

  **Phase 0 Stack Addition**

  ```python
  # requirements-rag.txt
  arize-phoenix
  openinference-instrumentation-llama-index
  ```

  **Decision:** Use **Arize Phoenix** for Phase 0. It's free, open source, self-hosted, and has native LlamaIndex integration. Data stays local (privacy). Add to the RAG stack for debugging retrieval quality and monitoring performance.

- User / 2026-01-28: Google Colab vs Jupyter Notebook - do they do the same thing?

- Claude Opus 4.5 / 2026-01-28: **Google Colab vs Jupyter Notebook**

  Yes, fundamentally the same thing - both are **interactive Python notebooks** where you write and run code in cells.

  ```
  ┌─────────────────────────────────────────┐
  │  Jupyter Notebook                       │
  │  - The original open-source project     │
  │  - Runs on your machine                 │
  │  - You own the environment              │
  └─────────────────────────────────────────┘
                      │
                      │ Google forked/hosted it
                      ▼
  ┌─────────────────────────────────────────┐
  │  Google Colab                           │
  │  - Jupyter Notebook in the cloud        │
  │  - Runs on Google's servers             │
  │  - Google manages the environment       │
  └─────────────────────────────────────────┘
  ```

  **What's the Same**

  | Aspect | Both Have |
  |--------|-----------|
  | File format | `.ipynb` |
  | Execution model | Cell-based (code + markdown) |
  | Kernel | Python |
  | Workflow | Write → Run → See output |

  **What's Different**

  | Aspect | Jupyter (Local) | Google Colab |
  |--------|-----------------|--------------|
  | Where it runs | Your laptop | Google's cloud |
  | Setup | `pip install jupyter` | Zero (browser) |
  | GPU access | Only if you have one | Free T4 (limited hours) |
  | Cost | Free (your hardware) | Free tier available |
  | Ollama integration | ✅ Direct localhost | ❌ Complex |
  | Neo4j/ChromaDB | ✅ Docker Compose | ❌ Complex setup |
  | File access | ✅ Direct filesystem | Google Drive mount |
  | Persistence | ✅ Persistent | Session resets |
  | Sharing | Export required | ✅ Easy link sharing |

  **For Phase 0 RAG Stack: Use Local Jupyter**

  Your stack (Ollama + ChromaDB + Neo4j + Phoenix) runs locally via Docker. Colab can't easily access `localhost:11434` (Ollama) or `localhost:7687` (Neo4j).

  ```bash
  # Quick setup
  pip install jupyterlab
  jupyter lab
  ```

  **When to Use Each**

  | Use Case | Best Choice |
  |----------|-------------|
  | Phase 0 RAG development | Local Jupyter |
  | Learning with cloud APIs (OpenAI) | Colab |
  | GPU-intensive fine-tuning | Colab |
  | Sharing notebooks with team | Colab |
  | Iterating on local `docs/` corpus | Local Jupyter |
  | Integration with repo workflow | Local Jupyter |

  **Analogy:** Think of it like **VS Code local** vs **GitHub Codespaces** - same editor, different host.

  **Decision:** Use local Jupyter Notebook for Phase 0 RAG experimentation. All stack components (Ollama, ChromaDB, Neo4j, Phoenix) are local services that need localhost access.

- User / 2026-01-28: What about RAGAS?

- Claude Opus 4.5 / 2026-01-28: **RAGAS - RAG Assessment Framework**

  RAGAS (Retrieval Augmented Generation Assessment) is an evaluation framework specifically designed to measure RAG pipeline quality.

  **What It Measures**

  ```
  Your RAG Pipeline
       │
       ▼
  Query → Retrieve → Generate → Answer
       │         │           │
       │         │           │
       ▼         ▼           ▼
  ┌─────────────────────────────────────┐
  │           RAGAS METRICS             │
  ├─────────────────────────────────────┤
  │ Context Precision  │ Are retrieved  │
  │                    │ docs relevant? │
  ├────────────────────┼────────────────┤
  │ Context Recall     │ Did we get all │
  │                    │ relevant docs? │
  ├────────────────────┼────────────────┤
  │ Faithfulness       │ Is answer      │
  │                    │ grounded in    │
  │                    │ retrieved docs?│
  ├────────────────────┼────────────────┤
  │ Answer Relevancy   │ Does answer    │
  │                    │ address query? │
  └─────────────────────────────────────┘
  ```

  **The Four Core Metrics**

  | Metric | What It Measures | Score Range |
  |--------|------------------|-------------|
  | **Context Precision** | % of retrieved chunks that are relevant | 0-1 |
  | **Context Recall** | % of relevant chunks that were retrieved | 0-1 |
  | **Faithfulness** | Is answer supported by context (no hallucination)? | 0-1 |
  | **Answer Relevancy** | Does answer actually address the question? | 0-1 |

  **Why RAGAS Matters**

  | Without RAGAS | With RAGAS |
  |---------------|------------|
  | "Seems to work" | Quantified quality scores |
  | Vibes-based evaluation | Data-driven improvement |
  | Unknown failure modes | Identified weak spots |
  | Can't compare changes | A/B test retrieval strategies |

  **Basic Usage**

  ```python
  from ragas import evaluate
  from ragas.metrics import (
      context_precision,
      context_recall,
      faithfulness,
      answer_relevancy,
  )
  from datasets import Dataset

  # Prepare evaluation data
  eval_data = {
      "question": ["What are the TDD requirements?"],
      "answer": ["All parsers must have unit tests per GOV-0017"],
      "contexts": [["GOV-0017 defines TDD policy...", "Coverage is 60%..."]],
      "ground_truth": ["Unit tests required, 60% coverage threshold"]
  }

  dataset = Dataset.from_dict(eval_data)

  # Run evaluation
  results = evaluate(
      dataset,
      metrics=[
          context_precision,
          context_recall,
          faithfulness,
          answer_relevancy,
      ],
  )

  print(results)
  # {'context_precision': 0.92, 'faithfulness': 0.88, ...}
  ```

  **RAGAS vs Phoenix**

  | Aspect | RAGAS | Arize Phoenix |
  |--------|-------|---------------|
  | Purpose | Evaluation/scoring | Observability/tracing |
  | When | Batch evaluation | Real-time monitoring |
  | Output | Quality scores | Traces, latency, tokens |
  | Use case | "Is my RAG good?" | "Why is this query slow?" |

  **They're Complementary:**

  ```
  Development Cycle:

  1. BUILD → Use Phoenix to debug traces
  2. EVALUATE → Use RAGAS to score quality
  3. IMPROVE → Fix issues found
  4. REPEAT
  ```

  **Integration with LlamaIndex**

  ```python
  from ragas.integrations.llama_index import evaluate

  # Evaluate your query engine directly
  results = evaluate(
      query_engine=index.as_query_engine(),
      metrics=[faithfulness, answer_relevancy],
      dataset=eval_dataset,
  )
  ```

  **Creating Evaluation Dataset**

  ```python
  # For governance docs, create test questions with known answers
  eval_questions = [
      {
          "question": "What testing framework is required for Terraform?",
          "ground_truth": "terraform test with .tftest.hcl files",
          "source": "GOV-0017"
      },
      {
          "question": "What is the coverage threshold?",
          "ground_truth": "60% for parsers and scripts",
          "source": "GOV-0017"
      },
  ]
  ```

  **Phase Recommendation**

  | Phase | RAGAS Use |
  |-------|-----------|
  | Phase 0 | Create 10-20 eval questions, baseline scores |
  | Phase 1 | Expand to 50+ questions, automate in CI |
  | Phase 2 | Continuous evaluation, regression alerts |

  **Installation**

  ```bash
  pip install ragas
  ```

  **Decision:** Add RAGAS to Phase 0 stack for baseline evaluation. Create a small eval dataset (10-20 governance questions) to quantify retrieval quality. Use alongside Phoenix - Phoenix for debugging, RAGAS for scoring.

- User / 2026-01-28: How would we interact with this - FastAPI with React frontend or just CLI? Can it be synchronous or just asynchronous?

- Claude Opus 4.5 / 2026-01-28: **RAG Interface Options**

  **Sync vs Async Reality**

  | Operation | Typical Latency | Sync Viable? |
  |-----------|-----------------|--------------|
  | Embedding | 10-50ms | Yes |
  | Vector search | 10-30ms | Yes |
  | Graph query | 20-50ms | Yes |
  | LLM generation | 1-10 seconds | Feels slow |

  LLM generation is the bottleneck. Can be sync, but users expect streaming.

  **Interface Options**

  ```
  ┌─────────────────────────────────────────────────────────────┐
  │                    INTERFACE OPTIONS                         │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  OPTION 1: CLI (Phase 0)                                    │
  │  ┌─────────────────────────────────────────────┐            │
  │  │ $ gov-rag ask "What are TDD requirements?"  │            │
  │  │ > Searching... (spinner)                    │            │
  │  │ > Answer: Per GOV-0017, all parsers...      │            │
  │  └─────────────────────────────────────────────┘            │
  │  Pros: Simple, no infra, sync is fine                       │
  │  Cons: Not shareable, terminal only                         │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  OPTION 2: FastAPI + Streaming (Phase 1)                    │
  │  ┌─────────────────────────────────────────────┐            │
  │  │ POST /query {"question": "..."}             │            │
  │  │ Response: Server-Sent Events (streaming)    │            │
  │  └─────────────────────────────────────────────┘            │
  │  Pros: API-first, streamable, integrations                  │
  │  Cons: Need to run server                                   │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  OPTION 3: FastAPI + React (Phase 2)                        │
  │  ┌─────────────────────────────────────────────┐            │
  │  │  [Search governance docs...]        [Ask]   │            │
  │  │  ┌─────────────────────────────────────┐    │            │
  │  │  │ Answer streaming in real-time...    │    │            │
  │  │  │ Sources: GOV-0017, ADR-0182         │    │            │
  │  │  └─────────────────────────────────────┘    │            │
  │  └─────────────────────────────────────────────┘            │
  │  Pros: Nice UX, shareable, visual citations                 │
  │  Cons: Frontend maintenance, more infra                     │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │  OPTION 4: Backstage Plugin (Phase 2+)                      │
  │  ┌─────────────────────────────────────────────┐            │
  │  │ Embed RAG directly in Backstage UI          │            │
  │  │ "Ask about this component's governance"     │            │
  │  └─────────────────────────────────────────────┘            │
  │  Pros: Integrated with IDP, contextual                      │
  │  Cons: Backstage plugin complexity                          │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
  ```

  **Streaming Architecture (Phase 1+)**

  ```python
  # FastAPI with streaming
  from fastapi import FastAPI
  from fastapi.responses import StreamingResponse
  from llama_index.core import VectorStoreIndex

  app = FastAPI()

  @app.post("/query")
  async def query(request: QueryRequest):
      # Retrieval is fast - do sync
      nodes = retriever.retrieve(request.question)

      # Generation streams
      async def generate():
          response = query_engine.query(request.question)
          async for token in response.async_response_gen():
              yield f"data: {token}\n\n"
          yield f"data: [DONE]\n\n"

      return StreamingResponse(generate(), media_type="text/event-stream")
  ```

  **React Consumption**

  ```typescript
  // React streaming client
  const askQuestion = async (question: string) => {
    const response = await fetch('/api/query', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      setAnswer(prev => prev + chunk);  // Stream to UI
    }
  };
  ```

  **Phase Recommendation**

  | Phase | Interface | Why |
  |-------|-----------|-----|
  | **Phase 0** | CLI only | Prove value, no infra overhead |
  | **Phase 1** | FastAPI (streaming) | Enable integrations, API-first |
  | **Phase 2** | Backstage plugin | Natural fit for IDP users |

  **Phase 0 CLI Implementation**

  ```python
  # scripts/rag/cli.py
  import click
  from rich.console import Console
  from rich.live import Live
  from rich.spinner import Spinner

  console = Console()

  @click.command()
  @click.argument('question')
  def ask(question: str):
      """Ask a question about governance docs."""

      with Live(Spinner("dots", text="Searching..."), refresh_per_second=10):
          # Retrieval (fast, sync)
          nodes = retriever.retrieve(question)

      console.print(f"\n[bold]Sources:[/bold]")
      for node in nodes[:3]:
          console.print(f"  - {node.metadata['file_path']}")

      console.print(f"\n[bold]Answer:[/bold]")
      # Stream tokens to terminal
      for token in query_engine.query(question).response_gen:
          console.print(token, end="")
      console.print()

  if __name__ == "__main__":
      ask()
  ```

  **Decision Matrix**

  | If You Need... | Use |
  |----------------|-----|
  | Quick validation | CLI |
  | API integrations | FastAPI |
  | Team access | FastAPI + simple HTML |
  | Full UX | React + FastAPI |
  | IDP integration | Backstage plugin |

  **Recommendation**

  ```
  Phase 0: CLI (this week)
     ↓
  Phase 1: FastAPI + streaming (if CLI proves value)
     ↓
  Phase 2: Backstage plugin (natural fit for IDP)
  ```

  Skip standalone React - go straight to Backstage plugin if you need a UI. That's where your users already are.

  **Decision:** Phase 0 uses CLI only (sync with streaming output). Phase 1 adds FastAPI with Server-Sent Events for streaming. Phase 2 integrates as Backstage plugin rather than standalone React app.
