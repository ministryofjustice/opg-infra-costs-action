resource "aws_sqs_queue" "ship_to_opg_metrics" {
  name                              = "ship-to-opg-metrics"
  delay_seconds                     = 90
  max_message_size                  = 2048
  message_retention_seconds         = 86400
  receive_wait_time_seconds         = 10
  kms_master_key_id                 = aws_kms_key.ship_to_metrics_queue.id
  kms_data_key_reuse_period_seconds = 300
}

resource "aws_sqs_queue_policy" "ship_to_opg_metrics" {
  queue_url = aws_sqs_queue.ship_to_opg_metrics.id
  policy    = data.aws_iam_policy_document.ship_to_opg_metrics_queue_policy.json
}

data "aws_iam_policy_document" "ship_to_opg_metrics_queue_policy" {
  statement {
    effect    = "Allow"
    resources = [aws_sqs_queue.ship_to_opg_metrics.arn]
    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ListQueueTags",
      "sqs:ReceiveMessage",
      "sqs:SendMessage",
    ]
    principals {
      type        = "AWS"
      identifiers = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_lambda_event_source_mapping" "ship_to_opg_metrics" {
  event_source_arn = aws_sqs_queue.ship_to_opg_metrics.arn
  function_name    = module.costs_to_sqs.lambda_function.arn
}

resource "aws_kms_key" "ship_to_metrics_queue" {
  description             = "ship-to-metrics queue encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.ship_to_metrics_queue_kms.json
}

resource "aws_kms_alias" "ship_to_metrics_queue_alias" {
  name          = "alias/ship_to_metrics_queue_encryption"
  target_key_id = aws_kms_key.ship_to_metrics_queue.key_id
}

# See the following link for further information
# https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
data "aws_iam_policy_document" "ship_to_metrics_queue_kms" {
  statement {
    sid       = "Enable Root account permissions on Key"
    effect    = "Allow"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
      ]
    }
  }

  statement {
    sid       = "Allow Key to be used for Encryption"
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
    ]

    principals {
      type = "Service"
      identifiers = [
        "*"
      ]
    }
  }

  statement {
    sid       = "Key Administrator"
    effect    = "Allow"
    resources = ["*"]
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"
    ]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/breakglass"]
    }
  }
}
