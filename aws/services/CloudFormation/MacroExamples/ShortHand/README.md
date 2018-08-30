# ShortHand CloudFormation Macro

The `ShortHand` macro provides convenience syntax to allow you to create short CloudFormation templates that expand into larger documents upon deployment to a stack.

See below for instructions to install and use the macro and for a full description of the macro's features.

## How to install and use the ShortHand macro in your AWS account

### Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts:
    * If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. Package the CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

    ```shell
    aws cloudformation package \
        --template-file macro.template \
        --s3-bucket <your bucket name here> \
        --output-template-file packaged.template
    ```

3. Deploy the packaged CloudFormation template to a CloudFormation stack:

    ```shell
    aws cloudformation deploy \
        --stack-name shorthand-macro \
        --template-file packaged.template \
        --capabilities CAPABILITY_IAM
    ```

4. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name shorthand-macro-example \
        --template-file example.template \
        --capabilities CAPABILITY_IAM
    ```

### Usage

To make use of the macro, add `Transform: ShortHand` to the top level of your CloudFormation template.

Here is a trivial example template:

```yaml
Transform: ShortHand
Resources:
  - S3::Bucket
```

## Features

The ShortHand macro provides the following features to your CloudFormation templates:

* A resource can be defined by a single string that contains its name, type, and proprties.

    For example:

    ```yaml
    "MyBucket AWS::S3::Bucket AccessControl=PublicRead"
    ```

    This would translate into:

    ```yaml
    MyBucket:
      Type: AWS::S3::Bucket
      Properties:
        AccessControl: PublicRead
    ```

* You can omit the resource name and one will be generated for you.

    For example:

    ```yaml
    "AWS::S3::Bucket AccessControl=PublicRead"
    ```

* You can shorten the resource type name by omitting parts of it from the left. As long as the result unambiguously refers to a valid CloudFormation resource type, the `ShortHand` macro will deal with it.

    For example:

    ```yaml
    "Bucket AccessControl=PublicRead"
    ```

    And:

    ```yaml
    "EC2::Instance"  # We need the `EC2::` prefix as there are other resource types that end with `Instance` (e.g. `AWS::OpsWorks::Instance`)
    ```

* All string values automatically use `Fn::Sub` if the value contains a sequence like `${something}`

    For example:

    ```yaml
    "MyBucketPolicy BucketPolicy Bucket=${MyBucket}"
    ```

    Will result in:

    ```yaml
    MyBucketPolicy:
      Type: AWS::S3::BucketPolicy
      Properties:
        Bucket:
          Fn::Sub: "${MyBucket}"
    ```

* You can address sub-properties using dot-notation.

    For example:

    ```yaml
    "MyBucket Bucket VersioningConfiguration.Status=Enabled"
    ```

* If you need to specify lots of properties (as is often the case) you can use object synax instead of a string.

    For example:

    ```yaml
    MyBucket S3::Bucket:
      AccessControl: PublicRead
      VersioningConfiguration.Status: Enabled
    ```

* To make all of these features possible, the `Resources` section of your template must now be an array rather than an object.

    A full example template would look like this:

    ```yaml
    Transform: ShortHand

    Parameters:
      Name:
        Type: String

    Resources:
      - S3::Bucket BucketName=${Name}
    ```

## Author

[Steve Engledow](https://linkedin.com/in/stilvoid)  
Senior Solutions Builder  
Amazon Web Services
