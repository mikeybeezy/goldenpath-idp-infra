## [0.0.3] - 2026-01-02

### Added
- **ADR-0064**: Documented decision to manage AWS Load Balancer Controller via Terraform.
- **Terraform**: `kubernetes_addons` module now includes `helm_release.aws_load_balancer_controller`.

### Changed
- **Bootstrap**: AWS Load Balancer Controller is now installed automatically during `terraform apply`, replacing the manual `10_aws_lb_controller.sh` step.

### Deprecated
- **Scripts**: `bootstrap/30_core-addons/10_aws_lb_controller.sh` is deprecated and will be removed.
