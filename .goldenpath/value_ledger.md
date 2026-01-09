# Value Ledger (VQ)

This file documents `value_ledger.json`, the Value Quantification (VQ) ledger.
The ledger records time reclaimed by automation scripts and aggregates the
running total in `total_reclaimed_hours`.

## How it is updated

Automation scripts call `vq_logger.log_heartbeat(...)` to append entries. Each
entry captures:

- timestamp
- script name
- reclaimed_hours

## Primary generators

- `scripts/sync_ecr_catalog.py`

Other scripts may add entries when they implement VQ logging via
`scripts/lib/vq_logger.py`.
