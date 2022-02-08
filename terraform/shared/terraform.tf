terraform {
  required_version = "= 1.1.4"

  backend "s3" {
    bucket         = "opg.terraform.state"
    key            = "costs-to-metrics/terraform.tfstate"
    encrypt        = true
    region         = "eu-west-1"
    role_arn       = "arn:aws:iam::311462405659:role/costs-to-metrics-ci"
    dynamodb_table = "remote_lock"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.1.0"
    }
  }
}

variable "DEFAULT_ROLE" {
  default = "costs-to-metrics-ci"
}

locals {
  management = "311462405659"
  shared     = "679638075911"
}

provider "aws" {
  alias  = "management"
  region = "eu-west-1"
  default_tags {
    tags = merge(local.mandatory_tags, local.optional_tags)
  }
  assume_role {
    role_arn     = "arn:aws:iam::${local.management}:role/${var.DEFAULT_ROLE}"
    session_name = "terraform-session"
  }
}

provider "aws" {
  region = "eu-west-1"
  alias  = "shared"
  default_tags {
    tags = merge(local.mandatory_tags, local.optional_tags)
  }
  assume_role {
    role_arn     = "arn:aws:iam::${local.shared}:role/${var.DEFAULT_ROLE}"
    session_name = "terraform-session"
  }
}

data "aws_caller_identity" "current" {
  provider = aws.management
}

data "aws_region" "current" {
  provider = aws.management
}
