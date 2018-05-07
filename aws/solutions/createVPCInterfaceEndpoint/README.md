Create VPC interface endpoint using CloudFormation

Issue
I am not able to create interface endpoint using CloudFormation as it doesn't support this yet, how to work around this?

Resolution
Using AWS Lambda and CloudFormation Custom Resources we can go around this limitation, allowing the creation of the VPC interface endpoint from within a CloudFormation Stack.

Instructions
Create a lambda backed custom resource using the lambda_vpce_interface.json file. In this stack you need to specify local VPC ID, Subnet ID, Security group, and service name to be used to create the interface endpoint
