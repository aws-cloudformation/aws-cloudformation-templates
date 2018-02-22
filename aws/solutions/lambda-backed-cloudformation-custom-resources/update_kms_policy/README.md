# Update KMS Key Policy from CloudFormation

This [AWS Lambda-backed CloudFormation Custom Resource](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html) can be used to update a [AWS KMS Key Policy](http://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html) from within CloudFormation.

By using this resource you can follow the AWS best practice of [least privileged access](http://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege) by adding and removing necessary AWS IAM ARNs and actions from the KMS key policy.  However, the role the Lambda function assumes can modify any KMS key policy by default, **please lock down the role permissions** if you intend to use this outside of a proof of concept.


# How to Install and Use the Lambda Function in Your AWS Account
1. Download the python file "lambda_function.py" to your local machine.
2. Create a zip file that contains the python file.
3. Upload that zip file to an AWS S3 bucket.
4. Run the CloudFormation template "deploy_update_kms_policy_lambda.yaml".
    1. You will need to fill in the parameter for S3 bucket name.
    2. You will need to fill in the parameter for S3 key that you stored the zip as.
5. Once CloudFormation finishes you can use the lambda function from within your CloudFormation templates.
6. An example CloudFormation Resource stanza is included in the file "example_usage_update_kms_policy.yaml".
    1. It is recommended to use [ImportValue function](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html) to get the KMS Key ARN from other CloudFormation stacks for use in the "kms-key-id-arn" parameter.
    2. You will normally include this stanza in the same CloudFormation template you create your IAM Role or IAM User, then use a Ref function to get the ARN for the "iam-principal-arn" parameter.
