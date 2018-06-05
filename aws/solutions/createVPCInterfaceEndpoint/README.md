# Create VPC interface endpoint using CloudFormation
## Issue 
I am not able to create interface endpoint using CloudFormation as it doesn't support this yet, how to work around this?
## Short Description
Interface VPC endpoint enables you to connect to services provided by AWS PrivateLink. By default, CloudFormation doesn’t support creation of interface endpoints.
## Resolution 
Using AWS Lambda and CloudFormation Custom Resources we can go around this limitation, allowing the creation of the VPC interface endpoint from within a CloudFormation Stack.
## Instructions 
The following steps provide a brief overview of this process:
* Create a lambda backed custom resource using the lambda_vpce_interface.json file. In this stack you need to specify local VPC ID, Subnet ID, Security group, and service name to be used to create the interface endpoint
