data "aws_lambda_layer_version" "sentry" {
  layer_name = "arn:aws:lambda:${data.aws_region.current.name}:943013980633:layer:SentryPythonServerlessSDK"
  version    = var.sentry_lambda_layer_version
}

resource "aws_lambda_function" "refresh" {
  filename = "${path.module}/functions/lambda.zip"

  function_name    = var.lambda_name
  handler          = "lambda.handler"
  role             = aws_iam_role.lambda.arn
  runtime          = var.lambda_runtime
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256("${path.module}/functions/lambda.zip")
  architectures    = [var.lambda_architecture]

  description = var.lambda_description

  layers = [
    data.aws_lambda_layer_version.sentry.arn,
  ]

  environment {
    variables = {
      AUTO_SCALING_GROUP_IS_ARM_DEFAULT                        = var.auto_scaling_group_is_arm_default ? "True" : "False"
      AUTO_SCALING_GROUP_NAME                                  = var.autoscaling_group_name
      DESCRIBE_INSTANCE_REFRESHES_MAX_RECORDS                  = var.describe_instance_refreshes_max_records
      REFRESH_INSTANCE_WARMUP                                  = var.instance_refresh_instance_warmup
      REFRESH_MIN_HEALTHY_PERCENTAGE                           = var.instance_refresh_min_healthy_percentage
      REFRESH_SKIP_MATCHING                                    = var.instance_refresh_skip_matching ? "True" : "False"
      SENTRY_DSN                                               = var.sentry_dsn
      SENTRY_ENVIRONMENT                                       = var.sentry_environment
      SSM_PARAMETER_NAME                                       = var.ami_ssm_parameter
      SSM_PARAMETER_NAME_ARM                                   = var.ami_ssm_parameter_arm
      UPDATE_MIXED_INSTANCES_POLICY_OVERRIDEN_LAUNCH_TEMPLATES = var.update_mixed_instances_policy_overriden_launch_templates ? "True" : "False"
      DD_TRACE_ENABLED                                         = var.datadog_trace_enabled
    }
  }
}

resource "aws_lambda_permission" "allow_cloudwatch_events" {
  statement_id  = "AllowCloudWatchEventsInvokeFunction"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.refresh.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.rule.arn
}
