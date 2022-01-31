data "aws_ecr_repository" "costs_to_sqs" {
  name     = "costs-to-metrics"
  provider = aws.management
}

data "aws_ecr_image" "costs_to_sqs" {
  repository_name = "costs-to-metrics"
  image_tag       = var.costs_to_sqs_lambda_container_version
  provider        = aws.management
}

module "costs_to_sqs" {
  source            = "./modules/lambda_function"
  lambda_name       = "costs-to-sqs"
  description       = "Function to take Cloudwatch Logs Subscription Filters and send them to SQS"
  working_directory = "/var/task"
  environment_variables = {
    "QUEUE_URL" : "queue url"
  }
  image_uri                           = "${data.aws_ecr_repository.costs_to_sqs.repository_url}@${data.aws_ecr_image.costs_to_sqs.image_digest}"
  ecr_arn                             = data.aws_ecr_repository.costs_to_sqs.arn
  lambda_role_policy_document         = data.aws_iam_policy_document.costs_to_sqs_lambda_function_policy.json
  aws_cloudwatch_log_group_kms_key_id = aws_kms_key.cloudwatch.arn
  providers                           = { aws = aws.management }
  lambda_function_tags                = { "image-tag" = var.costs_to_sqs_lambda_container_version }
}


data "aws_iam_policy_document" "costs_to_sqs_lambda_function_policy" {
  statement {
    sid    = "AllowCostExplorerGet"
    effect = "Allow"
    actions = [
      "ce:get*"
    ]
    resources = ["*"]
  }
  statement {
    sid       = "AllowSQSAccess"
    effect    = "Allow"
    resources = [aws_sqs_queue.ship_to_opg_metrics.arn]
    actions = [
      "sqs:SendMessage",
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
    ]
  }
  provider = aws.management
}
