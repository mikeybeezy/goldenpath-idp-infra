# VPC Module

## Purpose

This module provisions the foundational networking layer for the IDP environments. It creates:

- An AWS VPC with a configurable CIDR block and tags.
- An Internet Gateway (IGW), either newly created or reusing an existing one.
- An optional public route table that routes internet-bound traffic through the IGW.

It is meant to be consumed by higher-level stacks (e.g., `envs/*/main.tf`) that also provision subnets, route-table associations, and downstream services.

## Inputs

- `vpc_cidr` (string): CIDR block for the VPC (default `172.16.0.0/16`).
- `vpc_tag` (string): Name tag applied to the VPC (default `goldenpath-vpc`).
- `tags` (map(string)): Additional tags merged onto all resources created by the module.
- `create_internet_gateway` (bool): Whether to create a new IGW (default `true`).
- `existing_internet_gateway_id` (string): Provide an IGW ID to reuse instead of creating a new one.
- `create_public_route_table` (bool): Whether to create the public route table (default `true`).
- `public_route_cidr_block` (string): CIDR for the default route in the public route table (default `0.0.0.0/0`).
- `public_route_table_name` (string): Name tag for the public route table.

## Outputs

- `vpc_id`: The ID of the created VPC.
- `internet_gateway_id`: The ID of the IGW associated with the VPC (either newly created or reused).
- `public_route_table_id`: The ID of the public route table if it was created, otherwise `null`.

## Trade-offs

- The module keeps routing logic simple by only handling a single “public” route table. Additional private route tables or complex routing must be layered on by consuming modules (e.g., `aws_route_table` module).
- Flexibility to reuse an existing IGW is provided, but the module does not validate whether that IGW already belongs to another VPC; consumers must ensure correctness.
- Creating the route table within this module avoids an extra dependency but couples the VPC and basic routing; teams needing full control might prefer separate modules.

## Assumptions

- Subnets and route-table associations are managed outside of this module (e.g., via `modules/aws_subnet` and `modules/aws_route_table`).
- The AWS account/region supports the specified CIDR block and resource quotas (VPCs, IGWs, route tables).
- If `existing_internet_gateway_id` is provided, it belongs to the same AWS account and region where Terraform is running.

## Failure Modes

- **CIDR conflicts**: Supplying a CIDR that overlaps with an existing VPC in the same region will cause AWS API errors.
- **IGW reuse mismatch**: Providing an `existing_internet_gateway_id` that doesn’t belong to the target VPC will prevent the route table from referencing it and may leave the VPC without internet access.
- **Quota limits**: Hitting AWS limits for VPCs, IGWs, or route tables will cause the module to fail during creation.
- **Partial creation**: If the VPC is created but IGW/route table creation fails, a partial infrastructure may remain; re-running `terraform apply` usually completes once the underlying issue is fixed (e.g., quota, permissions).
