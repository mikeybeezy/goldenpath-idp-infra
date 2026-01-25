# AGENT_CONTEXT: Read .agent/README.md for rules
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}
