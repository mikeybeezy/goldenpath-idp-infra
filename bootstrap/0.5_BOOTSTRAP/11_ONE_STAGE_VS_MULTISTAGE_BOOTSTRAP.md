# One-Stage vs Multi-Stage Bootstrap

This document explains when to use a single-run bootstrap versus a staged
bootstrap, and how to run each without confusion.

## One-stage bootstrap (default)

**Use case**
- You want the fastest path to a working platform.
- You can afford a temporary capacity bump during bootstrap.

**Flow**
1) Apply Terraform with bootstrap mode enabled (larger node group).
2) Run the full bootstrap runner.
3) Apply Terraform again with bootstrap mode disabled (scale down).

**Commands**
```
TF_VAR_bootstrap_mode=true terraform -chdir=envs/dev apply
bash bootstrap/0.5_bootstrap/goldenpath-idp-bootstrap.sh goldenpath-dev-eks eu-west-2
TF_VAR_bootstrap_mode=false terraform -chdir=envs/dev apply
```

## Multi-stage bootstrap (careful/staged)

**Use case**
- You want to validate each step before moving on.
- You are operating with tight capacity or strict change control.

**Flow**
1) Apply Terraform with bootstrap mode enabled (or keep normal size if patient).
2) Run scripts in order and validate after each step.
3) Scale down after everything is stable.

**Commands**
```
TF_VAR_bootstrap_mode=true terraform -chdir=envs/dev apply

bash bootstrap/0.5_bootstrap/00_prereqs/00_check_tools.sh
bash bootstrap/0.5_bootstrap/10_gitops-controller/10_argocd_helm.sh goldenpath-dev-eks eu-west-2
bash bootstrap/0.5_bootstrap/20_core-addons/10_aws_lb_controller.sh goldenpath-dev-eks eu-west-2 <vpc-id>
bash bootstrap/0.5_bootstrap/20_core-addons/20_cert_manager.sh goldenpath-dev-eks eu-west-2
bash bootstrap/0.5_bootstrap/30_platform-tooling/10_argocd_apps.sh dev
bash bootstrap/0.5_bootstrap/30_platform-tooling/20_kong_ingress.sh goldenpath-dev-eks eu-west-2
bash bootstrap/0.5_bootstrap/40_smoke-tests/10_kubeconfig.sh goldenpath-dev-eks eu-west-2
bash bootstrap/0.5_bootstrap/40_smoke-tests/20_audit.sh goldenpath-dev-eks eu-west-2

TF_VAR_bootstrap_mode=false terraform -chdir=envs/dev apply
```

## Decision rule

- Need speed: use the **one-stage runner**.
- Need control: use **multi-stage scripts**.
