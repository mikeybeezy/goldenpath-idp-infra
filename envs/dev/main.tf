terraform {
  required_version = ">= 1.5.0"
}

locals {
  environment = var.environment
  name_prefix = var.name_prefix != "" ? var.name_prefix : "goldenpath-${local.environment}"
  public_subnets = var.public_subnets
  private_subnets = var.private_subnets

  common_tags = merge(
    {
      Environment = local.environment
      Project     = "goldenpath-idp"
      ManagedBy   = "terraform"
    },
    var.common_tags,
  )
}

module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr = var.vpc_cidr
  vpc_tag  = "${local.name_prefix}-vpc"
  tags     = local.common_tags
}

module "subnets" {
  source = "../../modules/aws_subnet"

  vpc_id          = module.vpc.vpc_id
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets
  tags            = local.common_tags
}

module "public_route_table" {
  source = "../../modules/aws_route_table"

  vpc_id                 = module.vpc.vpc_id
  name                   = "${local.name_prefix}-public-rt"
  gateway_id             = module.vpc.internet_gateway_id
  subnet_ids             = module.subnets.public_subnet_ids
  destination_cidr_block = "0.0.0.0/0"
  tags                   = local.common_tags
}

module "web_security_group" {
  source = "../../modules/aws_sg"

  name                     = "${local.name_prefix}-web-sg"
  vpc_id                   = module.vpc.vpc_id
  ingress_cidr_blocks      = ["0.0.0.0/0"]
  ingress_ipv6_cidr_blocks = ["::/0"]
  tags                     = local.common_tags
}
