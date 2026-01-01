# Modules Overview

This page summarizes each Terraform module and links to its README.

## Core network

- `modules/vpc/README.md`: VPC, IGW, NAT gateway, and shared tags.
- `modules/aws_subnet/README.md`: Public/private subnets from declarative lists.
- `modules/aws_route_table/README.md`: Route tables and subnet associations.
- `modules/aws_sg/README.md`: HTTPS security group (tighten for non-dev).

## EKS

- `modules/aws_eks/README.md`: EKS cluster, node group, OIDC, and add-ons.
- `modules/aws_iam/README.md`: EKS IAM roles, OIDC trust, and policies.

## Compute and networking

- `modules/aws_compute/README.md`: EC2 instance with user data and tags.
- `modules/aws_nic/README.md`: Network interface with security group attach.

## Notes

- Each module README lists inputs, outputs, and caveats.
- Use module READMEs as the source of truth for supported variables.
