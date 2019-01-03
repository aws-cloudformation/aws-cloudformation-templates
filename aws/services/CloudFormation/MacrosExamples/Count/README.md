# Count CloudFormation Macro

The `Count` macro provides a template-wide `Count` property for CloudFormation resources. It allows you to specify multiple resources of the same type without having to cut and paste.

## How to install and use the Count macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts:
    * If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. Package the Macro CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

    ```shell
    aws cloudformation package \
        --template-file template.yaml \
        --s3-bucket <your bucket name here> \
        --output-template-file packaged.yaml
    ```

3. Deploy the packaged CloudFormation template to a CloudFormation stack:

    ```shell
    aws cloudformation deploy \
        --stack-name Count-macro \
        --template-file packaged.yaml \
        --capabilities CAPABILITY_IAM
    ```

4. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name Count-test \
        --template-file test.yaml \
        --capabilities CAPABILITY_IAM
    ```

### Usage

To make use of the macro, add `Transform: Count` to the top level of your CloudFormation template.

Then specify permissions using a more natural syntax:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: Count
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Count: 3
  SQS:
    Type: AWS:::SQS::Queue
    Count: 2
```

### Important

You cannot use Count on resources that use a hardcoded name (`Name:` property). Duplicate names will cause a CloudFormation runtime failure.

## Author

[Jose Ferraris](https://github.com/j0lly)
AWS ProServ DevOps Consultant
Amazon Web Services
