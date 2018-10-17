# Deploy AmazonCloudWatchAgent to Ec2 instance by CloudFormation

## Issue
Customer does not know how to deploy AmazonCloudWatchAgent by CloudFormation and how to upgrade the configuration of CloudFormation.
By default, CloudFormation only supports SysV, how does customer work around this limitation?

## Resolution
These templates in this inline directory were designed to put the json configuration into the templates.
Customer can update the json configuration easily in templates then update the stack.
CloudFormation will check the configuration change and restart the AmazonCloudWatchAgent.

## limitation
In these templates, we just provide a way to deploy the AmazonCloudWatchAgent, and upgrade the configuration of AmazonCloudWatchAgent.
If customer wants to upgrade the AmazonCloudWatchAgent application, we suggest he recycle his hosts.
