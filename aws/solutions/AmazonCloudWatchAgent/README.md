# Deploy the Amazon CloudWatch agent to Amazon EC2 instances using AWS CloudFormation
The /inline and /ssm directories include templates to help you install the Amazon CloudWatch agent on Amazon EC2 instances using AWS CloudFormation. You can also use the templates to update the agent configuration after deployment. For more information, see https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-CloudFormation-Templates.html.


## /inline directory
The templates in the /inline directory have the CloudWatch agent configuration embedded into the AWS CloudFormation template. You can modify your CloudWatch agent configuration by modifying the template.

## /ssm directory
The templates in the /ssm directory load the agent configuration from Parameter Store. To use these templates, you must first create a configuration file and upload it to Parameter Store.
