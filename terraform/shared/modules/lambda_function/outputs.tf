output "lambda_function" {
  value = aws_lambda_function.lambda_function
}

output "lambda_iam_role" {
  value = aws_iam_role.lambda_role
}
