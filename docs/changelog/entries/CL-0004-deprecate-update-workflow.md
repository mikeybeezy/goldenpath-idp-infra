## [0.0.4] - 2026-01-02

### Changed
- **CI/CD**: `Apply - Infra Terraform Apply (dev)` workflow now supports resuming/updating ephemeral builds (removed mandatory `new_build=true` check).

### Removed
- **CI/CD**: `Apply - Infra Terraform Update (dev)` workflow has been removed. It is superseded by the improved Apply workflow which handles both creation and updates.
