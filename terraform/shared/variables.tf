locals {
  mandatory_tags = {
    business-unit = "OPG"
    application   = "costs-to-metrics"
    owner         = "OPG WebOps: opgteam@digital.justice.gov.uk"
  }
  optional_tags = {
    source-code = "https://github.com/ministryofjustice/opg-org-infra"
  }
}

variable "costs_to_sqs_lambda_container_version" {
  type    = string
  default = "latest"
}
