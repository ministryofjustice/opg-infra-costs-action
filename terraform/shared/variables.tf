locals {
  mandatory_tags = {
    business-unit = "OPG"
    application   = "costs-to-metrics"
    owner         = "OPG WebOps: opgteam@digital.justice.gov.uk"
  }
  optional_tags = {
    source-code = "https://github.com/ministryofjustice/opg-infra-costs-action"
  }
}

variable "costs_to_sqs_lambda_container_version" {
  type    = string
  default = "latest"
}

variable "ship_to_queue_lambda_container_version" {
  type    = string
  default = "latest"
}

variable "enable_ship_to_metrics" {
  type    = bool
  default = true
}
