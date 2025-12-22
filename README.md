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
   - `main.tf` wires the shared modules but now reads everything from variables, so you rarely edit this file.
   - `terraform.tfvars` is where you define the CIDR blocks, subnet objects, tags, and naming prefix for that environment.
   - `variables.tf` documents the inputs Terraform expects, making it easy to see what goes in the `tfvars`.
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

### Golden Commands (Makefile)

If you prefer a simplified workflow, the Makefile wraps the standard Terraform commands per environment:

```sh
make init ENV=dev
make plan ENV=dev
make apply ENV=dev
```

Each target runs the corresponding `terraform -chdir=envs/$ENV <command>` under the hood, so swap `dev` for `test`, `staging`, or `prod` as needed.

Step-by-step with the Makefile:
1. Open a terminal and `cd` into the repo root (`goldenpath-idp-infra`).
2. Pick an environment name (`dev`, `test`, `staging`, `prod`). Example uses `dev`.
3. Run `make init ENV=dev` to execute `terraform -chdir=envs/dev init` (downloads providers/state).
4. Run `make plan ENV=dev` to execute `terraform -chdir=envs/dev plan` and preview changes.
5. Run `make apply ENV=dev` to execute `terraform -chdir=envs/dev apply` and deploy (confirm when prompted).
6. Swap `ENV=dev` for `ENV=test`, `staging`, or `prod` to repeat; the Makefile just saves you from typing the `-chdir` commands manually.

## Customizing the Infrastructure

- **CIDR ranges & AZs**: edit `public_subnets` / `private_subnets` lists in `envs/<env>/terraform.tfvars`. Each item needs a `name`, `cidr_block`, and `availability_zone`, and you can add as many entries as you need (one per subnet/AZ pair). The subnet module automatically creates one subnet per object in the list. If your AWS account is limited to specific AZs (e.g., `eu-west-2a/b/c`), make sure the `availability_zone` fields match the zones that AWS allows in that region; otherwise Terraform will fail with “InvalidParameterValue” errors.

- **Tags**: add any key/value pairs under `common_tags` in the same `tfvars`; they merge with defaults so all resources stay labeled.

- **Name prefix & environment label**: set `name_prefix` and `environment` fields if you want different naming (e.g., `goldenpath-prod`).

- **Compute module**: every environment already includes the `aws_compute` module, but it’s disabled by default. Edit `compute_config` inside `envs/<env>/terraform.tfvars` (set `enabled = true`, choose an AMI, instance type, subnet type, etc.) to spin up a single EC2 instance. Leave `enabled = false` to skip it.

- **EKS (optional)**: the repo already contains an `aws_eks` module and wiring in every environment, but those blocks are commented out by default. To spin up a cluster for a specific env, remove the comment markers around the `module "eks"` block in `envs/<env>/main.tf`, the `variable "eks_config"` block in `envs/<env>/variables.tf`, and the `eks_config` object in `envs/<env>/terraform.tfvars`. Update the config (cluster name, version, node-group sizes/types), run `terraform plan`, and apply. Comment them back out whenever you want to pause or remove EKS.

## Tips

- Commit changes per environment so you can trace who modified what.
- Run `terraform fmt` before committing to keep files tidy.
- Use separate AWS accounts or isolated VPC CIDRs for `dev`, `test`, `staging`, and `prod` so they never conflict.

You now have a reproducible foundation for the Golden Path IDP. Expand it by adding more modules (EKS, RDS, Argo CD) as the platform evolves.
