# Deploy AmazonCloudWatchAgent to Ec2 instance by CloudFormation

## Issue
Customer does not know how to deploy AmazonCloudWatchAgent by CloudFormation and how to upgrade the configuration of CloudFormation.
By default, CloudFormation only supports SysV, how does customer work around this limitation?

## Resolution
These templates in this ssm directory were designed to retrieve the json configuration from ssm parameter store.
Customer needs to provide the name of parameter store.
The script in the userdata will install AmazonCloudWatchAgent, download json configuration from ssm parameter store, then restart the AmazonCloudWatchAgent.
Since customer is using the SSM Parameter store to manage the configuration, we suggest customer use SSMAgent to update the configuration update for existing hosts in the future.
If you do not want to update the configuration with the SSMAgent, you need to create a dummy file and change the contents of the dummy file. Simply change the VERSION from "VERSION=1.0" to "VERSION=2.0" in '/opt/aws/amazon-cloudwatch-agent/etc/dummy.version' in the example templates.

## limitation
In these templates, we just provide a way to deploy the AmazonCloudWatchAgent, and upgrade the configuration of AmazonCloudWatchAgent.
If customer wants to upgrade the AmazonCloudWatchAgent application, we suggest he recycle his hosts.
