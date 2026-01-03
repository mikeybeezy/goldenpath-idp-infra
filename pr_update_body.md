Select at least one checkbox per section by changing `[ ]` to `[x]`.

## Change Type
- [x] Feature
- [ ] Bug fix
- [ ] Infra change
- [x] Governance / Policy

## Decision Impact
- [x] Requires ADR
- [ ] Updates existing ADR
- [ ] No architectural impact

## Production Readiness
- [x] Readiness checklist completed
- [ ] No production impact

## Testing / Validation
- [ ] Plan/apply link provided (paste below)
- [x] Test command or run ID provided (paste below)
- [ ] Not applicable

Testing/Validation details:
- Plan/apply link: N/A (Docs/Scripts only)
- Test command/run: `python3 scripts/validate-metadata.py docs` (Ran locally)

## Risk & Rollback
- [ ] Rollback plan documented (link or notes below)
- [ ] Data migration required
- [x] No data migration
- [ ] Not applicable

Rollback notes/link: Revert commit.

## Notes / Summary (optional)
- Implements Metadata Fabric (Strategy, Tooling, Templates).
- Integrated Infracost `CostCenter` grouping.
- Docs backfill planned as follow-up.
