terraform {
  required_version = ">= 1.5.0"
}

locals {
  environment   = var.environment
  name_prefix   = var.name_prefix != "" ? var.name_prefix : "goldenpath-${local.environment}"
  public_subnets  = var.public_subnets
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

module "compute" {
  source = "../../modules/aws_compute"
  count  = var.compute_config.enabled ? 1 : 0

  name                 = var.compute_config.name
  ami_id               = var.compute_config.ami_id
  instance_type        = var.compute_config.instance_type
  subnet_id            = var.compute_config.subnet_type == "public" ? element(module.subnets.public_subnet_ids, 0) : element(module.subnets.private_subnet_ids, 0)
  security_group_ids   = concat([module.web_security_group.security_group_id], var.compute_config.additional_security_group_ids)
  ssh_key_name         = var.compute_config.ssh_key_name
  user_data            = var.compute_config.user_data
  iam_instance_profile = var.compute_config.iam_instance_profile
  network_interface_description = var.compute_config.network_interface_description
  root_volume_size     = var.compute_config.root_volume_size
  root_volume_type     = var.compute_config.root_volume_type
  root_volume_encrypted = var.compute_config.root_volume_encrypted
  tags                 = local.common_tags
}

/*module "eks" {
  source = "../../modules/aws_eks"
  count  = var.eks_config.enabled ? 1 : 0

  cluster_name       = var.eks_config.cluster_name
  kubernetes_version = var.eks_config.version
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.subnets.private_subnet_ids
  node_group_config  = var.eks_config.node_group
  tags               = local.common_tags

  depends_on = [module.public_route_table]
}*/
