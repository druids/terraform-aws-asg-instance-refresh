variable "ami_ssm_parameter" {
  default     = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"
  description = "Name of SSM parameter containing the current AMI"
  type        = string
}

variable "autoscaling_group_name" {
  description = "Name of the auto scaling group to refresh"
  type        = string
}

variable "cloudwatch_event_rule_name" {
  description = "Name of the CloudWatch Event Rule"
  default     = "ASGRefreshInstancesEventRule"
  type        = string
}

variable "cloudwatch_event_rule_schedule_expression" {
  description = "Schedule expression for CloudWatch Event Rule"
  default     = "cron(0 0 * * ? *)"
  type        = string
}

variable "describe_instance_refreshes_max_records" {
  description = "Page size for boto3 when calling autoscaling:DescribeInstanceRefreshes (max is 100)"
  default     = 100
  type        = number
}

variable "instance_refresh_instance_warmup" {
  description = "Instance warmup time for instance refresh"
  default     = 300
  type        = number
}

variable "instance_refresh_min_healthy_percentage" {
  description = "Minimum healthy percentage for instance refresh"
  default     = 90
  type        = number
}

variable "launch_template_version_description" {
  description = "Description of the new launch template version in Python's f-string format"
  default     = "Automated AMI refresh to \"{image_id}\""
  type        = string
}

variable "lambda_architecture" {
  description = "Set CPU architecture for the Lambda function. Valid values are \"x86_64\" and \"arm64\"."
  default     = "x86_64"
  type        = string
}

variable "lambda_description" {
  description = "Description of the Lambda function"
  default     = "Keeps ASG Launch Template updated with most recent AMI read from SSM Parameter"
  type        = string
}

variable "lambda_name" {
  description = "Name of the Lambda function"
  default     = "ASGRefreshInstances"
  type        = string
}

variable "lambda_role_description" {
  description = "Role description for the Lambda function"
  default     = ""
  type        = string
}

variable "lambda_role_name" {
  description = "Role name for the Lambda function"
  default     = "ASGRefreshInstancesLambdaRole"
  type        = string
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  default     = 60
  type        = number
}

variable "launch_template_name" {
  description = "Name of the launch template used by auto scaling group to refresh"
  type        = string
}

variable "launch_template_source_version" {
  description = "Source version for the new launch template"
  default     = "$Default"
  type        = string
}

variable "sentry_dsn" {
  default = null
  type    = string
}

variable "sentry_environment" {
  default = null
  type    = string
}

variable "sentry_lambda_layer_version" {
  default = 11
  type    = number
}
