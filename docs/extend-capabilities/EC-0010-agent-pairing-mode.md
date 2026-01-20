---
id: EC-0010-agent-pairing-mode
title: Agent Pairing Mode - Human-Machine Collaboration Protocol
type: extension-capability
status: proposed
owner: platform-team
domain: platform-core
relates_to:
  - ADR-0167
  - EC-0008-session-capture-ui
  - EC-0009-goldenpath-cli
  - session_capture_template
priority: low
vq_class: 🟡 HV/LQ
estimated_roi: TBD (interaction model improvement)
effort_estimate: Research phase only - implementation depends on Claude Code/Agent
  SDK
---
## Executive Summary

A collaborative interaction protocol where human and agent can fluidly switch between "driver" and "supporter" roles during a work session. Rather than strict request-response cycles, pairing mode enables exploratory collaboration where either party can lead, propose, or observe.

**Key Benefits**:
- Better for exploratory work (design, debugging, architecture)
- Human stays engaged without micromanaging
- Agent learns context and preferences through observation
- Reduces repeated context-setting across sessions
- Matches how experienced engineers actually pair

**Note**: This is primarily a **Claude Code / Agent SDK feature request**, not a GoldenPath platform feature. However, there are platform-level conventions and tooling that can support this interaction model.

## Problem Statement

### Current Interaction Model

```text
Request-Response Cycle:
  Human: "do X"
  Agent: [executes X completely]
  Agent: [reports results]
  Human: "now do Y"
  Agent: [executes Y completely]
  ...repeat...
```

### Limitations

1. **All-or-nothing execution**: Agent either does the whole task or nothing
2. **Context loss on handoff**: When human takes over, agent loses visibility
3. **No shared thinking space**: Ideas, alternatives, and decisions aren't captured collaboratively
4. **Rigid turn structure**: Doesn't match natural pairing dynamics
5. **Re-explaining context**: Each task requires re-establishing context

### Ideal Pairing Model

```text
Collaborative Pairing:
  Human: "let's work on X together"
  Agent: [enters pairing mode]

  Agent: "I see three approaches. Option A is..."
  Human: "I like A, but what about edge case Y?"
  Agent: "Good point. Let me adjust..."

  Human: "Actually, let me try this part manually"
  Agent: [observes, notes what human does]

  Human: "OK, you take over from here"
  Agent: [resumes with full context of human's work]

  [Session capture automatically records the collaboration]
```

## Proposed Solution

### What GoldenPath Can Do (Platform-Level)

#### 1. Pairing Session Capture Type

Extend session capture template for pairing sessions:

```yaml
# session_capture/2026-01-20-pairing-feature-x.md
---
id: session_pairing_2026_01_20_feature_x
type: pairing_session
participants:
  - human: mikesablaze
  - agent: claude-opus-4.5
mode: collaborative
---

## Pairing Log

### 08:30 - Agent proposes approach
[Agent] I see three options for implementing X...

### 08:35 - Human adjusts direction
[Human] Let's go with option A, but handle Y differently

### 08:45 - Human takes over
[Human - driving] I'll manually test this part
[Agent - observing] Noted: Human prefers to verify auth flows manually

### 09:00 - Agent resumes
[Agent - driving] Based on your testing, I'll now implement...
```

#### 2. Handoff Markers

Formalize handoff notation in session captures:

```markdown
## Handoff Log

| Time | From | To | Context |
|------|------|-----|---------|
| 08:45 | Agent | Human | Manual testing of auth flow |
| 09:00 | Human | Agent | Implement remaining endpoints |
| 09:30 | Agent | Human | Review and approval |
```

#### 3. Shared Scratchpad Convention

A `SCRATCHPAD.md` file for in-progress thinking:

```markdown
# Pairing Scratchpad - Feature X

## Current Question
How should we handle token refresh?

## Options Considered
- [ ] Option A: Refresh on 401
- [x] Option B: Proactive refresh (chosen)
- [ ] Option C: Let it fail

## Human Notes
> Token refresh needs to be transparent to user - Mike

## Agent Notes
> Implementing with 5-minute buffer before expiry

## Decisions Made
1. Use proactive refresh (09:15)
2. Buffer time: 5 minutes (09:20)
```

#### 4. Context Preservation Hooks

Session summary should capture enough for seamless resume:

```yaml
# In session summary
pairing_context:
  last_driver: agent
  human_preferences_learned:
    - prefers manual auth testing
    - likes detailed commit messages
    - wants dry-run before destructive ops
  open_questions:
    - token refresh interval (awaiting human input)
  agent_observations:
    - human debugs by adding console.logs first
    - human prefers small commits
```

### What Requires Agent SDK Changes (Future)

These require changes to Claude Code or the Agent SDK:

1. **Observation mode**: Agent watches human work without intervening
2. **Soft checkpoints**: Agent pauses at decision points for human input
3. **Context injection**: Human can "show" agent what they did offline
4. **Preference learning**: Agent remembers human patterns across sessions
5. **Explicit role switching**: `/human-drives` and `/agent-drives` commands

## Implementation Path

### Phase 1: Conventions Only (Now - P4)

1. Document pairing session capture format
2. Add handoff markers to session capture template
3. Create scratchpad convention for collaborative thinking
4. No code changes required

### Phase 2: Platform Tooling (Q2 - P3)

1. Add `type: pairing_session` to session capture schema
2. Create scratchpad template
3. Extend session summary to capture pairing context
4. Add pairing metrics to value ledger (optional)

### Phase 3: Agent SDK Proposal (Q3+ - External)

1. Document desired pairing behaviors
2. Submit feature request to Anthropic
3. Prototype with Claude Code hooks if available

## Success Criteria

| Metric | Target |
|--------|--------|
| Context re-explanation | < 1 per resumed session |
| Handoff friction | Seamless role switches |
| Session continuity | 90% context preserved across sessions |
| Human satisfaction | "Feels like real pairing" |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-engineering interaction | High | Start with conventions, not code |
| Single-user optimization | Medium | Document for future team use |
| Agent SDK dependency | High | Keep platform changes minimal |
| Scope creep | Medium | Phase 1 is documentation only |

## Decision

**Status**: Proposed (P4 - Research/Conventions only)

**Rationale**: This is valuable introspection work, but primarily depends on Agent SDK capabilities. GoldenPath can:
1. Establish conventions for pairing sessions
2. Extend session capture for collaborative work
3. Document preferences for future agent improvements

**Not building now**: Actual pairing mode requires Claude Code changes.

**Action**: Start noticing where current model fails. Document patterns in session captures. Use this data to inform future feature requests.

---

## References

- [Session Capture Template](../../session_capture/session_capture_template.md)
- [ADR-0167: Session Capture Guardrail](../adrs/ADR-0167-session-capture-guardrail.md)
- [EC-0008: Session Capture UI](EC-0008-session-capture-ui.md)
- [EC-0009: GoldenPath CLI](EC-0009-goldenpath-cli.md)

## Appendix: Pairing Patterns to Observe

When working with agents, note when you experience:

1. **"Let me just do this part"** - Where do you take over?
2. **"Wait, let me think"** - Where do you need the agent to pause?
3. **"You missed what I did"** - Where does context get lost?
4. **"I already told you"** - Where does the agent forget preferences?
5. **"Let's explore together"** - Where is request-response too rigid?

Document these in session captures to build evidence for feature requests.

Signed: platform-team (2026-01-20)
