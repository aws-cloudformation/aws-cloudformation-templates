# Search for AMI ID from CloudFormation Custom Resource

This [AWS Lambda-backed CloudFormation Custom Resource](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html) can be used to search for an [AWS EC2 AMI ID](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/finding-an-ami.html) from within CloudFormation.

By using this resource you can use the same CloudFormation template over time but use the latest AMI.  This can save a lot of time in organizations that release new AMIs often.


# How to Install and Use the Lambda Function in Your AWS Account
1. Download the python file "lambda_function.py" to your local machine.
2. Create a zip file that contains the python file.
3. Upload that zip file to an AWS S3 bucket.
4. Run the CloudFormation template "deploy_get_latest_ami_id.yaml".
    1. You will need to fill in the parameter for S3 bucket name.
    2. You will need to fill in the parameter for S3 key that you stored the zip as.
5. Once CloudFormation finishes you can use the lambda function from within your CloudFormation templates.
6. An example CloudFormation Resource stanza is included in the file "example_usage_get_latest_ami_id.yaml".
    1. The parameters for the custom resource are based on the [AWS CLI parameters for describe-images](http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-images.html)
