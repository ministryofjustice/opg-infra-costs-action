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
    "QUEUE_URL" : aws_sqs_queue.ship_to_opg_metrics.url,
    "COST_EXPLORER_ROLE" : "arn:aws:iam::295814833350:role/CostExplorerAccessReadOnly",
    "CHUNK_SIZE" : 20,
  }
  image_uri                           = "${data.aws_ecr_repository.costs_to_sqs.repository_url}@${data.aws_ecr_image.costs_to_sqs.image_digest}"
  ecr_arn                             = data.aws_ecr_repository.costs_to_sqs.arn
  lambda_role_policy_document         = data.aws_iam_policy_document.costs_to_sqs_lambda_function_policy.json
  aws_cloudwatch_log_group_kms_key_id = aws_kms_key.cloudwatch.arn
  timeout                             = 300 # 300 seconds = 5 minutes
  providers                           = { aws = aws.management }
  lambda_function_tags                = { "image-tag" = var.costs_to_sqs_lambda_container_version }
}


data "aws_iam_policy_document" "costs_to_sqs_lambda_function_policy" {
  provider = aws.management
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
  statement {
    sid       = "AllowXRayAccess"
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets",
      "xray:GetSamplingStatisticSummaries",
    ]
  }
  statement {
    sid       = "CrossAccountAssumeRole"
    effect    = "Allow"
    resources = ["arn:aws:iam::295814833350:role/CostExplorerAccessReadOnly"]
    actions = [
      "sts:AssumeRole",
    ]
  }
}

resource "aws_cloudwatch_event_rule" "costs_to_sqs_schedule" {
  name                = "costs-to-sqs-lambda"
  description         = "Kicks off costs to SQS lambda"
  schedule_expression = "cron(0 3 * * ? *)"
}

resource "aws_cloudwatch_event_target" "costs_to_sqs_target" {
  rule = aws_cloudwatch_event_rule.costs_to_sqs_schedule.name
  arn  = module.costs_to_sqs.lambda_function.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_costs_to_sqs" {
  statement_id  = "AllowExecutionFromCloudWatchChecklists"
  action        = "lambda:InvokeFunction"
  function_name = module.costs_to_sqs.lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.costs_to_sqs_schedule.arn
}
