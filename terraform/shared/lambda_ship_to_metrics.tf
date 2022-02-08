data "aws_ecr_repository" "ship_to_opg_metrics" {
  name     = "opg-metrics/ship-to-opg-metrics"
  provider = aws.management
}

data "aws_ecr_image" "ship_to_opg_metrics" {
  repository_name = "opg-metrics/ship-to-opg-metrics"
  image_tag       = var.ship_to_queue_lambda_container_version
  provider        = aws.management
}

data "aws_secretsmanager_secret_version" "opg_metrics_api_key" {
  secret_id     = data.aws_secretsmanager_secret.opg_metrics_api_key.id
  version_stage = "AWSCURRENT"
  provider      = aws.shared
}

data "aws_secretsmanager_secret" "opg_metrics_api_key" {
  name     = "opg-metrics-api-key/costs-to-metrics-development"
  provider = aws.shared
}

data "aws_kms_alias" "opg_metrics_api_key_encryption" {
  name     = "alias/opg_metrics_api_key_encryption"
  provider = aws.shared
}

module "ship_to_opg_metrics" {
  source            = "./modules/lambda_function"
  lambda_name       = "ship-to-opg-metrics"
  description       = "Function to take metrics from SQS and PUT them to OPG Metrics"
  working_directory = "/var/task"
  environment_variables = {
    "OPG_METRICS_URL" : "https://development.api.metrics.opg.service.justice.gov.uk"
    "SECRET_ARN" : data.aws_secretsmanager_secret_version.opg_metrics_api_key.arn
  }
  image_uri                           = "${data.aws_ecr_repository.ship_to_opg_metrics.repository_url}@${data.aws_ecr_image.ship_to_opg_metrics.image_digest}"
  ecr_arn                             = data.aws_ecr_repository.ship_to_opg_metrics.arn
  lambda_role_policy_document         = data.aws_iam_policy_document.ship_to_opg_metrics_lambda_function_policy.json
  aws_cloudwatch_log_group_kms_key_id = aws_kms_key.cloudwatch.arn
  lambda_function_tags                = { "image-tag" = var.ship_to_queue_lambda_container_version }
  providers                           = { aws = aws.management }
}

data "aws_iam_policy_document" "ship_to_opg_metrics_lambda_function_policy" {
  provider = aws.management
  statement {
    sid       = "AllowSQSAccess"
    effect    = "Allow"
    resources = [aws_sqs_queue.ship_to_opg_metrics.arn]
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
    ]
  }

  statement {
    sid    = "AllowSecretsManagerAccess"
    effect = "Allow"
    resources = [
      data.aws_secretsmanager_secret.opg_metrics_api_key.arn,
      "arn:aws:secretsmanager:eu-west-1:679638075911:secret:opg-metrics-api-key/costs-to-metrics-development"
    ]
    actions = [
      "secretsmanager:GetSecretValue",
    ]
  }
  statement {
    sid       = "AllowKMSDecrypt"
    effect    = "Allow"
    resources = [data.aws_kms_alias.opg_metrics_api_key_encryption.target_key_arn]
    actions = [
      "kms:Decrypt",
    ]
  }
}

resource "aws_lambda_event_source_mapping" "ship_to_opg_metrics" {
  count            = var.enable_ship_to_metrics ? 1 : 0
  event_source_arn = aws_sqs_queue.ship_to_opg_metrics.arn
  function_name    = module.ship_to_opg_metrics.lambda_function.arn
}
