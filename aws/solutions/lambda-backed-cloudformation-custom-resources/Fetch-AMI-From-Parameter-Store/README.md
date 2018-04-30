# Fetch AMI ID from Parameter Store

This [AWS Lambda-backed CloudFormation Custom Resource](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html) can be used to fetch an AMI ID from the Parameter Store and launch instances using this AMI. This is an automated solution for the following examples:

1. https://aws.amazon.com/about-aws/whats-new/2018/04/amazon-ecs-provides-ecs-optimized-ami-metadata-via-ssm-parameter/
2. https://aws.amazon.com/blogs/mt/query-for-the-latest-windows-ami-using-systems-manager-parameter-store/

The native [SSM Parameter Types](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#aws-ssm-parameter-types) supported by CloudFormation cannot be used here because those parameter types only look for parameters in the account creating the stack. However, these parameters are actually owned by internal AWS accounts. By using this solution you can use the same CloudFormation template over time and across different regions but select the AMI you want to use without having to specify the AMI name or ID. This can save a lot of time since you no longer have to manually update templates or resources with the new AMI ID.


# How to Install and Use this solution in Your AWS Account
1. Download the python file "lambda_function.py" to your local machine.
2. Create a zip file that contains the python file.
3. Upload that zip file to an AWS S3 bucket. Make sure the bucket is in the same region you are planning to use this solution in.
4. Launch a stack with the CloudFormation template "Fetch-AMI-From-Parameter-Store.json". You will need to provide values for the following parameters:
    1. ParameterName - The name of the Parameter in the Parameter Store that contains the AMI ID. (Ex: /aws/service/ecs/optimized-ami/amazon-linux/recommended)
    2. FunctionBucket - The name of the bucket that contains the Lambda function zip file.
    3. FunctionKey - The name of the Lambda function zip file uploaded to S3.
    4. InstanceType - The instance type to launch.
    5. MinInstances - The minimum number of instances to have in the ASG.
    6. MaxInstances - The maximum number of instances to have in the ASG.
    7. Subnets - Subnets across which you want to launch instances.
5. Once CloudFormation finishes launching the stack, you can observe that the instances in the AutoScaling Group have been launched with the AMI that corresponds to the Parameter Name you specified.
