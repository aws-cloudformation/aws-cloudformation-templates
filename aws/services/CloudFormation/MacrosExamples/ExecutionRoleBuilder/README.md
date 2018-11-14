# Execution Role Builder CloudFormation Macro

The `Execution Role Builder` macro provides a more natural syntax for developers to express the permissions they want to attach to IAM execution roles for their applications, while simultaneously providing IAM administrators with a way to templatize those permissions. When used in conjunction with permission boundaries, this provides an effective solution for delegated role creation.

See below for instructions to install and use the macro and for a full description of the macro's features.

## How to install and use the ShortHand macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts:
    * If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. While optional, this macro is normally expected to work in conjunction with permission boundaries:
    * If you don't have one already, follow [this example](https://aws.amazon.com/blogs/security/delegate-permission-management-to-developers-using-iam-permissions-boundaries/)
    * Note the ARN of the permission boundary for use below.

3. Package the Macro CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

    ```shell
    aws cloudformation package \
        --template-file macro.template \
        --s3-bucket <your bucket name here> \
        --output-template-file ExecutionRoleBuilderCFnMacro.packaged.template
    ```

4. Deploy the packaged CloudFormation template to a CloudFormation stack:

    ```shell
    aws cloudformation deploy \
        --stack-name ExecutionRoleBuilderCFnMacro.packaged.template \
        --template-file ExecutionRoleBuilderCFnMacro \
        --capabilities CAPABILITY_IAM
    ```

5. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name executionrolebuilder-macro-example \
        --template-file example.template \
        --parameter-overrides PermissionBoundaryArn=<your permission boundary ARN here> \
        --capabilities CAPABILITY_IAM
    ```

### Usage

To make use of the macro, add `Transform: ExecutionRoleBuilder` to the top level of your CloudFormation template.

Then specify permissions using a more natural syntax:

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExecutionRoleBuilder
Parameters:
  PermissionBoundaryArn:
    Type: String
    Description: ARN for the Permission Boundary Policy
Resources:
  ExecutionRoleBuilderMacroTestRole: 
    Type: "AWS::IAM::Role"
    Properties: 
      Type: "Lambda"
      Name: "ExecutionRoleForAppA"
      Path: "/boundedexecroles/"
      PermissionsBoundary:
        Ref: PermissionBoundaryArn
      Permissions:
        - ReadOnly: "arn:aws:s3:::mygreatbucket1"
        - ReadWrite: "arn:aws:dynamodb:us-west-2:123456789012:table/table1"
        - ReadOnly: "arn:aws:ssm:us-west-2:123456789012:parameter/dev/myapp1/*"
        - ReadOnly: "arn:aws:kms:us-west-2:123456789012:key/a8f4be2b-5fcd-zzzz-yyyy-xxxxxxxxxxxx"
```

After you have the basics working, customize the policy templates within the lambda function to tailor the resulting policies as desired.

### Important

The lambda function associated with this CFn macro is transforming short hand permission syntax into proper CloudFormation used to construct IAM policies. The proper use of boundary policies provides that outer boundary of what is permissible within those policies, but regardless, proper care should be taken to understand who has the ability to alter the lambda function, and that the function contents are what you expect them to be.

## Author

[Quint Van Deman](www.linkedin.com/in/quint-van-deman)
Prinicipal Business Development Manager
Amazon Web Services
