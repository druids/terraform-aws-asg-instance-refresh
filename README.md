## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 3.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.refresh_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_role.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_lambda_function.refresh](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.allow_cloudwatch_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_autoscaling_group.group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/autoscaling_group) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_lambda_layer_version.sentry](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/lambda_layer_version) | data source |
| [aws_launch_template.template](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/launch_template) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_ami_ssm_parameter"></a> [ami\_ssm\_parameter](#input\_ami\_ssm\_parameter) | Name of SSM parameter containing the current AMI | `string` | `"/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"` | no |
| <a name="input_autoscaling_group_name"></a> [autoscaling\_group\_name](#input\_autoscaling\_group\_name) | Name of the auto scaling group to refresh | `string` | n/a | yes |
| <a name="input_cloudwatch_event_rule_name"></a> [cloudwatch\_event\_rule\_name](#input\_cloudwatch\_event\_rule\_name) | Name of the CloudWatch Event Rule | `string` | `"ASGRefreshInstancesEventRule"` | no |
| <a name="input_cloudwatch_event_rule_schedule_expression"></a> [cloudwatch\_event\_rule\_schedule\_expression](#input\_cloudwatch\_event\_rule\_schedule\_expression) | Schedule expression for CloudWatch Event Rule | `string` | `"cron(0 0 * * ? *)"` | no |
| <a name="input_describe_instance_refreshes_max_records"></a> [describe\_instance\_refreshes\_max\_records](#input\_describe\_instance\_refreshes\_max\_records) | Page size for boto3 when calling autoscaling:DescribeInstanceRefreshes (max is 100) | `number` | `100` | no |
| <a name="input_instance_refresh_instance_warmup"></a> [instance\_refresh\_instance\_warmup](#input\_instance\_refresh\_instance\_warmup) | Instance warmup time for instance refresh | `number` | `300` | no |
| <a name="input_instance_refresh_min_healthy_percentage"></a> [instance\_refresh\_min\_healthy\_percentage](#input\_instance\_refresh\_min\_healthy\_percentage) | Minimum healthy percentage for instance refresh | `number` | `90` | no |
| <a name="input_instance_refresh_skip_matching"></a> [instance\_refresh\_skip\_matching](#input\_instance\_refresh\_skip\_matching) | Skip matching instances for instance refresh | `bool` | `false` | no |
| <a name="input_lambda_architecture"></a> [lambda\_architecture](#input\_lambda\_architecture) | Set CPU architecture for the Lambda function. Valid values are "x86\_64" and "arm64". | `string` | `"x86_64"` | no |
| <a name="input_lambda_description"></a> [lambda\_description](#input\_lambda\_description) | Description of the Lambda function | `string` | `"Keeps ASG Launch Template updated with most recent AMI read from SSM Parameter"` | no |
| <a name="input_lambda_name"></a> [lambda\_name](#input\_lambda\_name) | Name of the Lambda function | `string` | `"ASGRefreshInstances"` | no |
| <a name="input_lambda_role_description"></a> [lambda\_role\_description](#input\_lambda\_role\_description) | Role description for the Lambda function | `string` | `""` | no |
| <a name="input_lambda_role_name"></a> [lambda\_role\_name](#input\_lambda\_role\_name) | Role name for the Lambda function | `string` | `"ASGRefreshInstancesLambdaRole"` | no |
| <a name="input_lambda_timeout"></a> [lambda\_timeout](#input\_lambda\_timeout) | Timeout for Lambda function in seconds | `number` | `60` | no |
| <a name="input_launch_template_name"></a> [launch\_template\_name](#input\_launch\_template\_name) | Name of the launch template used by auto scaling group to refresh | `string` | n/a | yes |
| <a name="input_launch_template_source_version"></a> [launch\_template\_source\_version](#input\_launch\_template\_source\_version) | Source version for the new launch template | `string` | `"$Default"` | no |
| <a name="input_launch_template_version_description"></a> [launch\_template\_version\_description](#input\_launch\_template\_version\_description) | Description of the new launch template version in Python's f-string format | `string` | `"Automated AMI refresh to \"{image_id}\""` | no |
| <a name="input_sentry_dsn"></a> [sentry\_dsn](#input\_sentry\_dsn) | n/a | `string` | `null` | no |
| <a name="input_sentry_environment"></a> [sentry\_environment](#input\_sentry\_environment) | n/a | `string` | `null` | no |
| <a name="input_sentry_lambda_layer_version"></a> [sentry\_lambda\_layer\_version](#input\_sentry\_lambda\_layer\_version) | n/a | `number` | `11` | no |
| <a name="input_update_mixed_instances_policy_overriden_launch_templates"></a> [update\_mixed\_instances\_policy\_overriden\_launch\_templates](#input\_update\_mixed\_instances\_policy\_overriden\_launch\_templates) | If you do not want to also update launch templates that override the default launch template, set this to false | `bool` | `true` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_asg_arn"></a> [asg\_arn](#output\_asg\_arn) | n/a |
| <a name="output_lt_arn"></a> [lt\_arn](#output\_lt\_arn) | n/a |
| <a name="output_lt_id"></a> [lt\_id](#output\_lt\_id) | n/a |
| <a name="output_lt_name"></a> [lt\_name](#output\_lt\_name) | n/a |
