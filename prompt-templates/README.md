# Prompt Templates

This directory contains structured prompt templates for AI agent-assisted implementation tasks.

## Purpose

These prompts are designed for **human-supervised** execution by AI agents (Codex, Claude, etc.) to implement PRDs and other documented tasks with consistency and completeness.

## Important Warning

**These templates are NOT meant to be auto-executed.**

AI agents scanning this repository should NOT automatically execute commands found in these files. They are templates to be explicitly invoked by a human operator.

## File Format

All prompt templates use `.txt` extension to reduce the risk of AI agents parsing them as actionable instructions.

## Naming Convention

```
PROMPT-XXXX-<short-description>.txt
```

- `PROMPT-0000` - Template/example file
- `PROMPT-0001` onwards - Actual implementation prompts

## Template Structure

Each prompt follows a standard structure (see `PROMPT-0000-template.txt`):

1. **Warning Header** - DO NOT AUTO-EXECUTE notice
2. **Metadata Block** - ID, title, PRD link, target repo, dates
3. **Context** - Background and problem statement
4. **Task** - Clear objective
5. **Preconditions** - What must be true before starting
6. **Step-by-Step Implementation** - Phased execution plan
7. **Verification Checklist** - Required checks before completion
8. **Integration Verification** - Cross-system checks
9. **Do NOT** - Explicit guardrails
10. **Output Expected** - What to report when done
11. **Rollback Plan** - How to undo
12. **References** - Links to related docs

## Usage

1. Copy the prompt content to your AI agent interface
2. Ensure the agent has access to the target repository
3. Review the agent's plan before execution
4. Monitor execution and verify checklist items
5. Review PR before merging

## Index

| ID | Title | PRD | Status |
|----|-------|-----|--------|
| PROMPT-0000 | Template | N/A | Template |
| PROMPT-0001 | PRD-0004 Backstage Repo Alignment | PRD-0004 | Ready |

## Adding New Prompts

1. Copy `PROMPT-0000-template.txt`
2. Rename to `PROMPT-XXXX-<description>.txt`
3. Fill in all sections
4. Update this README index
5. Link from the related PRD
