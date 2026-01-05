locals {
  public_subnets_map = {
    for subnet in var.public_subnets : subnet.name => subnet
  }

  private_subnets_map = {
    for subnet in var.private_subnets : subnet.name => subnet
  }

  environment_tags = var.environment != "" ? { Environment = var.environment } : {}
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets_map

  vpc_id                  = var.vpc_id
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = each.value.name
      Tier = "public"
    },
    try(each.value.tags, {}),
    local.environment_tags,
  )
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets_map

  vpc_id                  = var.vpc_id
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = false

  tags = merge(
    var.tags,
    {
      Name = each.value.name
      Tier = "private"
    },
    try(each.value.tags, {}),
    local.environment_tags,
  )
}
