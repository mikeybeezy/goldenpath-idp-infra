---
id: EC-0004-backstage-copilot-plugin
title: Backstage AI Copilot Plugin
type: extension_capability
status: proposed
relates_to:
  - INDEX
  - ROADMAP
  - RB-0001-platform-incident-response
dependencies:
  - Backstage (existing)
  - Runbooks (35+ existing)
  - Makefile targets (existing)
  - YAML schemas (existing)
priority: medium
vq_class: velocity
estimated_roi: $15,000/year (reduced MTTR + platform team toil)
effort_estimate: 2-6 weeks (depending on approach)
owner: platform-team
---

## Executive Summary

Build an AI-powered copilot for GoldenPath IDP that assists operators with platform tasks using **Retrieval-Augmented Generation (RAG)** over existing runbooks, documentation, and operational knowledge. The copilot:

- **Answers Questions**: "How do I rotate RDS credentials?" → retrieves RB-0029
- **Suggests Commands**: "Deploy to staging" → proposes `make deploy ENV=staging`
- **Explains Errors**: Paste stack trace → identifies issue + suggests remediation

**Estimated ROI**: $15,000/year from reduced MTTR (15 min → 5 min) and platform team escalations.

**Strategic Fit**: 5/5 - Leverages existing copilot-ready assets (35+ runbooks, Makefile targets, YAML schemas).

## Problem Statement

Platform operators and development teams face:

1. **Documentation Hunting**: 35+ runbooks across multiple directories, hard to find the right one
2. **Tribal Knowledge**: Experienced engineers know which commands to run; new team members don't
3. **Slow Incident Response**: MTTR increased by searching docs during incidents
4. **Platform Team Bottleneck**: Simple questions escalate to platform team (~3 hours/week)

Current friction:
- Average runbook lookup: 5-10 minutes
- New engineer onboarding: 2 weeks to learn platform patterns
- Incident MTTR: 15-30 min (could be 5 min with faster guidance)

## Proposed Solution

### Copilot Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Backstage AI Copilot                             │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐   │
│  │   User Query    │───▶│   RAG Pipeline   │───▶│  LLM Response    │   │
│  │                 │    │                 │    │                  │   │
│  │  "How do I      │    │  1. Embed query │    │  "Use RB-0029:   │   │
│  │   rotate RDS    │    │  2. Search docs │    │   make rotate-   │   │
│  │   creds?"       │    │  3. Build prompt│    │   rds-secret"    │   │
│  └─────────────────┘    └─────────────────┘    └──────────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Knowledge Sources                             │  │
│  │                                                                   │  │
│  │   Runbooks (35+)      Makefile Targets      YAML Schemas   │  │
│  │  docs/70-operations/   Makefile                schemas/          │  │
│  │                                                                   │  │
│  │  📖 ADRs (150+)         Scripts               Incident Logs  │  │
│  │  docs/adrs/            scripts/                (optional)        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Interaction Modes

| Mode | Description | Risk Level | Phase |
|------|-------------|------------|-------|
| **Read-Only** | Answer questions, explain docs | None | 1 |
| **Suggest** | Propose commands, show before execute | Low | 1 |
| **Guided** | Step-by-step walkthrough with confirmation | Low | 2 |
| **Execute** | Run approved commands (future) | Medium | 3+ |

**Recommendation**: Start with Read-Only + Suggest (Copilot mode, not Autopilot).

### Example Interactions

**Query 1: Finding the right runbook**
```
User: "The backstage pod is crashing, what do I check?"

Copilot: Based on RB-0031-idp-stack-deployment.md, here's what to check:

1. Check pod status:
   kubectl get pods -n backstage

2. View pod logs:
   kubectl logs -n backstage deployment/backstage --tail=100

3. Common issues:
   - Missing database connection → verify RDS endpoint in secret
   - ECR pull failure → check IRSA role permissions

📖 Full runbook: docs/70-operations/runbooks/RB-0031-idp-stack-deployment.md
```

**Query 2: Suggesting a command**
```
User: "I need to rotate the keycloak database password"

Copilot: To rotate the Keycloak RDS credentials, use RB-0029:

Suggested command:
  make rds-rotate-secret APP=keycloak ENV=dev

This will:
1. Generate new password in Secrets Manager
2. Update the keycloak_user role in RDS
3. Trigger pod restart to pick up new credentials

⚠️ Requires: AWS credentials with Secrets Manager access

Run this command? [Copy to clipboard]
```

**Query 3: Explaining an error**
```
User: "Error: secret 'goldenpath/dev/keycloak/postgres' not found"

Copilot: This error indicates the Keycloak database secret hasn't been
provisioned yet.

Likely causes:
1. RDS Terraform hasn't been applied for this environment
2. Application not in application_databases variable

Resolution (from RB-0031):
1. Check if app is defined:
   grep keycloak envs/dev-rds/terraform.tfvars

2. If missing, add to application_databases:
   keycloak = { database_name = "keycloak", username = "keycloak_user" }

3. Apply RDS changes:
   make apply-rds ENV=dev
```

## Architecture Integration

### Deployment Options

| Option | Description | Effort | Maintenance |
|--------|-------------|--------|-------------|
| **Slack Bot** | External bot, uses Slack API | 1-2 days | Low |
| **Teams Bot** | External bot, uses Teams API | 1-2 days | Low |
| **Backstage TechDocs** | Enhance existing search | Already exists | None |
| **Backstage Plugin** | Custom React + Node plugin | 2-4 weeks | Medium |

**Recommendation**: Start with Slack Bot (fastest to deploy), migrate to Backstage Plugin if adoption high.

### Slack Bot Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                      Slack Workspace                              │
│                                                                   │
│   User types: "@goldenpath-copilot how do I deploy to staging?"  │
│                                                                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                   Copilot Service (Lambda/ECS)                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  1. Receive Slack event                                     │  │
│  │  2. Embed query using OpenAI/Anthropic embeddings           │  │
│  │  3. Search vector store (Pinecone/pgvector/Chroma)         │  │
│  │  4. Retrieve relevant docs (top 5)                          │  │
│  │  5. Build prompt with context                               │  │
│  │  6. Query LLM (Claude/GPT-4)                                │  │
│  │  7. Return formatted response to Slack                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                      Vector Store                                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Indexed documents:                                          │  │
│  │  - docs/70-operations/runbooks/*.md (35 files)              │  │
│  │  - docs/adrs/*.md (150+ files)                              │  │
│  │  - Makefile targets + descriptions                          │  │
│  │  - schemas/*.yaml (request schemas)                         │  │
│  │  - docs/85-how-it-works/*.md                                │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### Files to Create

| File | Purpose |
|------|---------|
| `copilot/index.py` | Main RAG pipeline |
| `copilot/embeddings.py` | Document embedding utilities |
| `copilot/prompts/system.txt` | System prompt for LLM |
| `copilot/prompts/runbook.txt` | Prompt template for runbook queries |
| `copilot/slack_handler.py` | Slack event handler |
| `copilot/indexer.py` | Index docs to vector store |
| `copilot/requirements.txt` | Python dependencies |
| `Dockerfile.copilot` | Container for Lambda/ECS |
| `.github/workflows/copilot-index.yml` | Re-index on doc changes |

### LangChain Implementation Sketch

```python
# copilot/index.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load documents
from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader(
    "docs/70-operations/runbooks/",
    glob="**/*.md",
    show_progress=True
)
runbooks = loader.load()

# Create embeddings and store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(runbooks, embeddings)

# Build retrieval chain
llm = ChatAnthropic(model="claude-3-sonnet-20240229")

PROMPT = PromptTemplate(
    template="""You are a GoldenPath IDP platform copilot. Answer questions
    using the provided runbooks and documentation.

    Context from runbooks:
    {context}

    User question: {question}

    Provide:
    1. Direct answer to the question
    2. Relevant commands (if applicable)
    3. Link to the source runbook

    Answer:""",
    input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    chain_type_kwargs={"prompt": PROMPT}
)
```

## Strategic Use Cases

### Use Case 1: Incident Response Acceleration

**Before**: Engineer searches docs, asks in Slack, waits for response.
**After**: "@copilot RDS connection failing in staging" → immediate guidance.

**Value**: MTTR reduced from 15 min to 5 min per incident.

### Use Case 2: New Engineer Onboarding

**Before**: New hire spends 2 weeks learning platform patterns.
**After**: "@copilot how do I create a new secret request?" → immediate guidance.

**Value**: Onboarding reduced from 2 weeks to 3 days for basic operations.

### Use Case 3: Platform Team Toil Reduction

**Before**: Platform team answers same questions repeatedly (~3 hours/week).
**After**: Copilot handles 80% of routine questions.

**Value**: Platform team freed for higher-value work.

### Use Case 4: Self-Service Command Discovery

**Before**: "What Makefile targets are available for RDS?" → grep through Makefile.
**After**: "@copilot list RDS make targets" → formatted list with descriptions.

**Value**: Faster command discovery, reduced errors.

## Implementation Roadmap

### Phase 1: Minimum Viable Copilot (Week 1-2)

- [ ] Set up document indexing pipeline
- [ ] Index runbooks + Makefile + ADRs
- [ ] Create Slack bot with RAG
- [ ] Deploy to Lambda/ECS
- [ ] Basic testing with platform team

**Deliverables**:
- Working Slack bot answering runbook questions
- 80% accuracy on common queries
- Internal beta with platform team

### Phase 2: Enhanced Retrieval (Week 3-4)

- [ ] Add Makefile target parsing with descriptions
- [ ] Include YAML schema examples
- [ ] Improve prompt engineering
- [ ] Add feedback mechanism ("Was this helpful?")
- [ ] Create reindexing workflow on doc changes

**Deliverables**:
- Improved accuracy (90%+)
- Feedback collection for iteration
- Auto-reindex on PR merge

### Phase 3: Backstage Plugin (Week 5-6, if warranted)

- [ ] Create React frontend plugin
- [ ] Add chat interface to Backstage sidebar
- [ ] Integrate with TechDocs search
- [ ] Add command execution preview

**Deliverables**:
- Native Backstage experience
- Unified search + copilot

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Hallucination** | Medium | RAG grounds responses in real docs; add confidence scores |
| **Stale Information** | Medium | Reindex on every doc change; show last-updated timestamp |
| **Credential Exposure** | High | Never include secrets in responses; audit logs for queries |
| **Unauthorized Actions** | High | Copilot suggests only; human approves + executes |
| **Cost Overrun** | Low | Use Claude Haiku for simple queries, Sonnet for complex |
| **Low Adoption** | Medium | Start with Slack (where teams already are) |

### Compliance Considerations

| Concern | Recommendation |
|---------|----------------|
| **Audit Trail** | Log all queries and responses |
| **PII/Secrets** | Exclude sensitive files from index |
| **Approval Gates** | Never auto-execute; always suggest |
| **Data Residency** | Use EU region for LLM API if required |

**Key Principle**: AI assists, human approves, pipeline executes.

## Cost Analysis

### Infrastructure Costs

| Component | Monthly Cost | Annual Cost |
|-----------|--------------|-------------|
| **LLM API (Claude/GPT)** | ~$100-300 | $1,200-3,600 |
| **Vector Store (Pinecone)** | $70 | $840 |
| **Lambda/ECS Compute** | ~$20 | $240 |
| **Total** | ~$200-400/month | ~$2,500-4,500/year |

### Alternative: Self-Hosted

| Component | Monthly Cost | Annual Cost |
|-----------|--------------|-------------|
| **Open-source LLM (Llama)** | ~$200 (GPU instance) | $2,400 |
| **pgvector (existing RDS)** | $0 (use existing) | $0 |
| **Total** | ~$200/month | ~$2,400/year |

### Savings

| Metric | Before | After | Annual Value |
|--------|--------|-------|--------------|
| **MTTR (incidents)** | 15 min | 5 min | $5,000 |
| **Platform Team Toil** | 3 hrs/week | 0.5 hrs/week | $10,000 |
| **Onboarding Time** | 2 weeks | 3 days | Qualitative |
| **Total Savings** | | | ~$15,000/year |

**Net ROI**: $15,000 - $3,500 = **$11,500/year** (~330% return)

## Existing Copilot-Ready Assets

GoldenPath is already well-positioned for copilot integration:

| Asset | Count | Quality |
|-------|-------|---------|
| **Runbooks** | 35+ | Structured markdown with commands |
| **ADRs** | 150+ | Context + decisions |
| **Makefile Targets** | 50+ | Self-documenting with comments |
| **YAML Schemas** | 10+ | Request formats with examples |
| **How-It-Works Docs** | 20+ | Conceptual explanations |

### Quick Win: Makefile Introspection

```bash
# Already parseable command catalog
make help

# Can extract target + description pairs:
# deploy-persistent: Deploy full stack with persistent RDS
# teardown-persistent: Destroy persistent cluster safely
# rds-rotate-secret: Rotate RDS credentials for APP
```

## Monitoring & Success Metrics

### Technical Metrics

- **Query Latency**: P95 < 3 seconds
- **Retrieval Accuracy**: Top-5 contains answer 90%+ of time
- **Uptime**: 99.9%

### Business Metrics

- **Adoption**: 50% of platform team using weekly by Month 2
- **Deflection Rate**: 80% of queries answered without escalation
- **User Satisfaction**: "Was this helpful?" > 4/5 average

### Quality Metrics

- **Hallucination Rate**: < 5% of responses contain incorrect info
- **Citation Rate**: 95%+ responses cite source document

## Alternatives Considered

### Option 1: Enhanced TechDocs Search

**Pros**: Already exists, no new infrastructure
**Cons**: Keyword search, no natural language understanding

**Decision**: Complement, don't replace

### Option 2: ChatGPT Enterprise

**Pros**: Managed service, enterprise features
**Cons**: No RAG over internal docs without Enterprise Search

**Decision**: Consider for Phase 2 if API approach too complex

### Option 3: Full Agent with Tool Execution

**Pros**: Automated operations
**Cons**: High compliance risk, requires approval workflows

**Decision**: Defer to Phase 3+ after trust established

## Open Questions

1. **LLM Provider**: Anthropic Claude vs OpenAI GPT-4?
   - **Recommendation**: Claude (better instruction following, longer context)

2. **Vector Store**: Pinecone vs pgvector vs Chroma?
   - **Recommendation**: pgvector (reuse existing RDS, no new vendor)

3. **Execution Mode**: Should copilot ever execute commands?
   - **Recommendation**: No in V1. Copilot suggests, human executes.

4. **Scope**: Include all docs or just runbooks?
   - **Recommendation**: Start with runbooks + Makefile, add ADRs in Phase 2

## Governance Compliance

### Born Governed Checklist

- [ ] Schema-driven configuration (copilot config YAML)
- [ ] Metadata header for scripts (SCRIPT-0037)
- [ ] ADR documentation (ADR after accepted)
- [ ] Changelog entry (CL-XXXX)
- [ ] Runbook creation (RB-0035-copilot-operations)
- [ ] Audit logging for all queries

### Security Review

- [ ] No secrets in indexed documents
- [ ] Query logs retained 30 days
- [ ] LLM API keys in Secrets Manager
- [ ] IRSA for AWS access

## References

- [LangChain Documentation](https://python.langchain.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Backstage Plugin Development](https://backstage.io/docs/plugins/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)

## Approval Workflow

- [ ] Platform team review
- [ ] Security review (data indexing, API access)
- [ ] Architecture approval
- [ ] Roadmap prioritization

---

**Status**: Proposed (awaiting platform team review)
**Next Action**: Discuss at next platform architecture meeting
**Contact**: @platform-team for questions

## RAG Readiness and Fit (Notes)

Short answer: we are structurally prepared for retrieval, but there is no RAG pipeline, vector store, or LLM integration in this repo today. The knowledge-graph and metadata work provides strong raw material, but integrating it would be new scope.

### What exists today (RAG-adjacent foundations)

- Knowledge graph architecture and intent are documented, not implemented as a retrievable store: `docs/adrs/ADR-0110-idp-knowledge-graph-architecture.md`.
- Relationship extraction builds a graph from doc references and calls out semantic gaps: `docs/70-operations/runbooks/RB-0019-relationship-extraction-script.md`.
- Metadata coverage and standardized IDs provide a clean corpus for chunking/indexing: `docs/10-governance/FEDERATED_METADATA_STRATEGY.md`, `scripts/extract_relationships.py`.
- Backstage currently links docs to GitHub rather than TechDocs, so RAG would need its own ingestion path: `docs/changelog/entries/CL-0102-backstage-docs-linkout.md`.

### Where RAG could fit

- Backstage assistant/search plugin that retrieves from docs + catalog metadata + relationship graph.
- CI/ops impact analysis helper that uses the relationship graph + doc corpus.
- Standalone internal service that indexes repo docs + metadata on a schedule and serves retrieval APIs.

### Scope call

- If the near-term goal is infra baseline + governance stability, RAG is likely out of scope (new service, data pipeline, and security model).
- If the goal includes developer-portal intelligence, a thin POC is a logical next layer.

### POC acceptance criteria (suggested)

- **Corpus**: index runbooks + Makefile targets + request schemas only (no ADRs in POC).
- **Retrieval quality**: for a curated set of 10 operator questions, top-3 results contain the correct runbook in at least 8 cases.
- **Citations**: every response includes source paths/links to the retrieved docs.
- **Safety**: read-only answers; no command execution; no secret content indexed.
- **Latency**: p50 response under 5 seconds in dev/staging.
- **Ops**: re-index on doc changes via CI or nightly job; basic query audit log retained 30 days.

### Out of scope (POC)

- Command execution or automation triggers.
- Production rollout or SSO integration.
- Indexing incident logs or external systems.
