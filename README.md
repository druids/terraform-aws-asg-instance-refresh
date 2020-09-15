## Requirements

No requirements.

## Providers

The following providers are used by this module:

- archive

- aws

- null

## Required Inputs

The following input variables are required:

### autoscaling\_group\_name

Description: Name of the auto scaling group to refresh

Type: `string`

### launch\_template\_name

Description: Name of the launch template used by auto scaling group to refresh

Type: `string`

## Optional Inputs

The following input variables are optional (have default values):

### ami\_ssm\_parameter

Description: Name of SSM parameter containing the current AMI

Type: `string`

Default: `"/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"`

### cloudwatch\_event\_rule\_name

Description: Name of the CloudWatch Event Rule

Type: `string`

Default: `"ASGRefreshInstancesEventRule"`

### cloudwatch\_event\_rule\_schedule\_expression

Description: Schedule expression for CloudWatch Event Rule

Type: `string`

Default: `"cron(0 0 * * ? *)"`

### describe\_instance\_refreshes\_max\_records

Description: Page size for boto3 when calling autoscaling:DescribeInstanceRefreshes (max is 100)

Type: `string`

Default: `"100"`

### instance\_refresh\_instance\_warmup

Description: Instance warmup time for instance refresh

Type: `string`

Default: `"300"`

### instance\_refresh\_min\_healthy\_percentage

Description: Minimum healthy percentage for instance refresh

Type: `string`

Default: `"90"`

### lambda\_description

Description: Description of the Lambda function

Type: `string`

Default: `"Keeps ASG Launch Template updated with most recent AMI read from SSM Parameter"`

### lambda\_name

Description: Name of the Lambda function

Type: `string`

Default: `"ASGRefreshInstances"`

### lambda\_role\_description

Description: Role description for the Lambda function

Type: `string`

Default: `""`

### lambda\_role\_name

Description: Role name for the Lambda function

Type: `string`

Default: `"ASGRefreshInstancesLambdaRole"`

### lambda\_timeout

Description: Timeout for Lambda function in seconds

Type: `string`

Default: `60`

### launch\_template\_source\_version

Description: Source version for the new launch template

Type: `string`

Default: `"$Default"`

### launch\_template\_version\_description

Description: Description of the new launch template version in Python's f-string format

Type: `string`

Default: `"Automated AMI refresh to \"{image_id}\""`

## Outputs

The following outputs are exported:

### asg\_arn

Description: n/a

### lt\_arn

Description: n/a

### lt\_id

Description: n/a

### lt\_name

Description: n/a

