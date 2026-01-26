---
id: EC-0014-agent-scope-registry
title: 'EC-0014: Agent Scope Registry'
type: enhancement-concept
status: draft
domain: platform-core
owner: platform-team
lifecycle: proposed
schema_version: 1
risk_profile:
  production_impact: low
  security_risk: medium
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
  maturity: 1
relates_to:
  - EC-0013-agent-context-architecture
  - 07_AI_AGENT_GOVERNANCE
  - agent-merge-guard.yml
  - pr-guardrails.yml
---

# EC-0014: Agent Scope Registry

## Problem Statement

AI agents operating in the repository need different permission levels:

| Agent Type | Use Case | Should Be Allowed |
|------------|----------|-------------------|
| Code Agent (Claude, Copilot) | Feature development | Full code access with review |
| Doc Agent | Documentation updates | `.md` files only |
| Review Agent | Code review, feedback | Read-only + comments |
| Deps Agent (Dependabot) | Dependency updates | Package files only |

**Current state**: All agents are treated identically. Either they're blocked entirely (useless) or allowed fully (risky for limited-scope agents).

**Incident**: A trigger-happy agent pushed 717 files directly to development because there was no scope enforcement.

## Proposed Solution

### 1. Agent Identity Declaration

Agents MUST sign their work:

```
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
Co-Authored-By: Devin <devin@cognition.ai>
```

This signature is parsed by guardrails to identify the agent.

### 2. Scope Registry

Create `.github/agent-scopes.yml` that maps agent identities to permissions:

```yaml
# .github/agent-scopes.yml
version: 1

scopes:
  full-access:
    description: "Full repository access, human review required"
    allowed_paths: ["**/*"]
    blocked_paths: []
    requires_review: true
    can_merge: false  # Human must merge

  docs-only:
    description: "Documentation files only"
    allowed_paths:
      - "docs/**/*.md"
      - "*.md"
      - "session_capture/**/*.md"
      - "session_summary/**/*.md"
    blocked_paths:
      - "**/*.py"
      - "**/*.tf"
      - "**/*.yaml"
      - "**/*.yml"
      - "**/*.sh"
    requires_review: true
    can_merge: false

  deps-only:
    description: "Dependency files only"
    allowed_paths:
      - "package.json"
      - "package-lock.json"
      - "requirements.txt"
      - "requirements-dev.txt"
      - "pyproject.toml"
    blocked_paths: ["**/*"]  # Block everything not explicitly allowed
    requires_review: false   # Auto-merge for minor/patch
    can_merge: true
    auto_merge_conditions:
      - "semver:patch"
      - "semver:minor"

  review-only:
    description: "Read-only access, can comment but not modify"
    allowed_paths: []
    blocked_paths: ["**/*"]
    requires_review: false
    can_merge: false
    can_comment: true

agents:
  # Claude Code (this agent)
  "Claude Opus 4.5":
    scope: full-access
    email_pattern: "noreply@anthropic.com"

  "Claude Sonnet":
    scope: full-access
    email_pattern: "noreply@anthropic.com"

  # Devin - scope TBD based on use case
  "Devin":
    scope: docs-only  # Start restricted, elevate as needed
    email_pattern: "*@cognition.ai"

  # GitHub Copilot
  "GitHub Copilot":
    scope: full-access
    email_pattern: "noreply@github.com"

  # Dependabot
  "dependabot[bot]":
    scope: deps-only
    email_pattern: "*@dependabot.com"

  # Default for unknown agents
  "_default":
    scope: docs-only  # Restrictive default
    requires_review: true
```

### 3. Guardrail Enforcement

Update `pr-guardrails.yml` to read the scope registry and enforce:

```python
def check_agent_scope(pr_files, agent_name, scope_registry):
    """Validate PR files against agent's declared scope."""

    agent_config = scope_registry['agents'].get(agent_name, scope_registry['agents']['_default'])
    scope = scope_registry['scopes'][agent_config['scope']]

    violations = []

    for file in pr_files:
        # Check if file matches allowed paths
        allowed = any(fnmatch(file, pattern) for pattern in scope['allowed_paths'])
        blocked = any(fnmatch(file, pattern) for pattern in scope['blocked_paths'])

        if blocked or (not allowed and scope['allowed_paths']):
            violations.append(f"{file} - not in scope '{agent_config['scope']}'")

    return violations
```

### 4. Workflow Integration

```yaml
# In pr-guardrails.yml
- name: Check agent scope
  run: |
    # Extract agent from Co-Authored-By
    AGENT=$(git log -1 --format="%b" | grep "Co-Authored-By:" | head -1 | sed 's/Co-Authored-By: //' | cut -d'<' -f1 | xargs)

    if [ -n "$AGENT" ]; then
      echo "Agent detected: $AGENT"
      python3 scripts/check_agent_scope.py "$AGENT" "${{ github.event.pull_request.number }}"
    fi
```

## Scope Escalation Process

If an agent needs elevated permissions for a specific task:

1. **Human creates PR label**: `agent-scope:full-access`
2. **Guardrail recognizes override**: Allows expanded scope for that PR only
3. **Audit log captures**: "Scope elevated by @human for PR #123"

```yaml
# Label-based scope override
- name: Check scope override
  run: |
    LABELS="${{ join(github.event.pull_request.labels.*.name, ',') }}"

    if echo "$LABELS" | grep -q "agent-scope:full-access"; then
      echo "::notice::Scope elevated to full-access via label"
      echo "SCOPE_OVERRIDE=full-access" >> $GITHUB_ENV
    fi
```

## Benefits

| Benefit | Description |
|---------|-------------|
| **Least Privilege** | Agents only get permissions they need |
| **Auditability** | Clear record of who did what with which scope |
| **Flexibility** | Different agents can have different roles |
| **Safety** | Trigger-happy agents can't touch code if scoped to docs |
| **Scalability** | Add new agents with appropriate scope easily |

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Agent spoofs identity | Verify email domain, require signed commits |
| Scope too restrictive | Label-based escalation for exceptions |
| Config drift | Validate `agent-scopes.yml` in pre-commit |
| Unknown agent | Default to most restrictive scope |

## Implementation Phases

### Phase 1: Registry + Detection
- Create `.github/agent-scopes.yml`
- Add agent detection to `pr-guardrails.yml`
- Log agent identity in PR comments

### Phase 2: Enforcement
- Block PRs that violate scope
- Add scope override via labels
- Create audit log

### Phase 3: Self-Service
- Agents can request scope elevation in PR description
- Human approves via label
- Automated scope suggestions based on file patterns

## Related Documents

- [EC-0013: Universal Agent Context Architecture](EC-0013-agent-context-architecture.md) - Complements this with context loading
- [07_AI_AGENT_GOVERNANCE](../10-governance/07_AI_AGENT_GOVERNANCE.md) - Policy framework
- [PROMPT-0003](../../prompt-templates/PROMPT-0003-recursive-pr-gate-compliance.txt) - PR compliance process

## Decision

**Status**: Draft - Pending team review

**Next Steps**:
1. Review scope definitions with team
2. Decide default scope for unknown agents
3. Implement Phase 1
