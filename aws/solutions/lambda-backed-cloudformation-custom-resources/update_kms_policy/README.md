# Update KMS Key Policy from CloudFormation

Used to create a Lambda backed CloudFormation custom resource that will add or remove given IAM ARNs from a given KMS key policy


# Included Files

1. deploy_update_endpoint_policy.yaml
 1. Used to deploy the Lambda
2. lambda_function.py
 1. The actual function
 2. You will need to zip it and upload to s3 to deploy via CloudFormation
3. example_usage_update_kms_policy.yaml
 1. An example CloudFormation template that shows how to call the lambda
