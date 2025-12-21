# Golden Path IDP Infra

This repository contains Terraform modules and environment definitions that provision the baseline cloud infrastructure for the Golden Path Internal Developer Platform (IDP). The code is designed to be approachable—even if you are still in college or just getting started with Terraform.

## Repository Layout

```
.
├── modules/        # Reusable Terraform modules (VPC, subnets, SG, compute, etc.)
├── envs/           # Per-environment stacks (dev, test, staging, prod)
│   └── <env>/      # Each environment has its own main.tf, backend.tf, terraform.tfvars
├── main.tf         # Root provider + Terraform settings shared across envs
└── README.md
```

Each environment composes the shared modules so you can deploy the same architecture with different CIDRs or tags.

## Prerequisites

1. **Terraform 1.5+** – install from <https://developer.hashicorp.com/terraform/downloads>.
2. **AWS credentials configured** – run `aws configure` or export `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.
3. **An S3 bucket & DynamoDB table (optional but recommended)** for remote state (edit `envs/<env>/backend.tf` to point at your bucket/table).

## Step-by-Step Usage

1. **Clone the repo**
   ```sh
   git clone <repo-url> && cd goldenpath-idp-infra
   ```

2. **Review the modules**
   - `modules/vpc`: creates the VPC, internet gateway, and public route table.
   - `modules/aws_subnet`: defines public/private subnets.
   - `modules/aws_sg`: reusable HTTPS security group.
   - `modules/aws_compute`: EC2 instance + network interface.

3. **Pick an environment to work with**
   ```sh
   cd envs/dev   # replace dev with test/staging/prod if needed
   ```
   - `main.tf` already wires the shared modules with sensible defaults.
   - `terraform.tfvars` can override values (e.g., AMI IDs, instance types).
   - `backend.tf` is where you point to your remote state bucket/table.

4. **Initialize Terraform for that environment**
   ```sh
   terraform init
   ```
   This downloads provider plugins and configures remote state.

5. **Preview the changes**
   ```sh
   terraform plan -out plan.out
   ```
   Review the plan output; it shows exactly what AWS resources will be created or changed.

6. **Apply when ready**
   ```sh
   terraform apply plan.out
   ```
   Terraform will create the VPC, subnets, route tables, and security groups defined for the environment. Confirm with `yes` when prompted.

7. **Tear down (optional)**
   ```sh
   terraform destroy
   ```
   Use this when you need to clean up the environment to avoid AWS charges.

## Customizing the Infrastructure

- **CIDR ranges & AZs**: Adjust the `local.public_subnets` and `local.private_subnets` blocks inside each `envs/<env>/main.tf`.
- **Tags**: Edit `local.common_tags` per environment so resources include organizational metadata.
- **Compute module**: Instantiate `modules/aws_compute` inside an environment if you need EC2 instances. Pass in `subnet_id`, `security_group_ids`, `ami_id`, etc., to match the environment’s resources.

## Tips

- Commit changes per environment so you can trace who modified what.
- Run `terraform fmt` before committing to keep files tidy.
- Use separate AWS accounts or isolated VPC CIDRs for `dev`, `test`, `staging`, and `prod` so they never conflict.

You now have a reproducible foundation for the Golden Path IDP. Expand it by adding more modules (EKS, RDS, Argo CD) as the platform evolves.
