# AMI-Search CloudFormation Custom Resource

Used to create a Lambda backed CloudFormation custom resource that can search for the latest AMI ID for you given some parameters.

# Included Files

1. deploy_get_latest_ami_id.yaml
 1. Used to deploy the Lambda
2. lambda_function.py
 1. The actual function
 2. You will need to zip it and upload to s3 to deploy via CloudFormation
3. example_usage_get_latest_ami_id.yaml
 1. An example CloudFormation template that shows how to call the lambda and how to get the return value
