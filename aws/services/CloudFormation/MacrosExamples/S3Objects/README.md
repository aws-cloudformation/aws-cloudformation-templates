# How to install and use the S3Objects macro in your AWS account

The `S3Objects` macro adds a new resource type: `AWS::S3::Object` which you can use to populate an S3 bucket.

You can either create new S3 objects or copy S3 buckets from other buckets that you have permissions to access.

As with any other CloudFormation resource, if you delete a stack containing S3 objects defined with this macro, those objects will be deleted.

A typical use case for this macro might be, for example, to populate an S3 website with static assets.

## Deploying

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
        --stack-name s3objects-macro \
        --template-file packaged.template \
        --capabilities CAPABILITY_IAM
    ```

4. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name s3objects-macro-example \
        --template-file example.template \
        --capabilities CAPABILITY_IAM
    ```

## Usage

To make use of the macro, add `Transform: S3Objects` to the top level of your CloudFormation template.

Here is a trivial example template:

```yaml
Transform: S3Objects
Resources:
  Bucket:
    Type: AWS::S3::Bucket

  Object:
    Type: AWS::S3::Object
    Properties:
      Target:
        Bucket: !Ref Bucket
        Key: README.md
        ContentType: text/plain
      Body: Hello, world!
```

## Features

### Creating a new S3 object

To create a new S3 object, add an `AWS::S3::Object` resource to your template and specify the `Target` and `Body` properties. For example:

```yaml
NewObject:
  Type: AWS::S3::Object
  Properties:
    Target:
      Bucket: !Ref TargetBucket
      Key: README.md
    Body: |
      # My text file

      This is my text file;
      there are many like it,
      but this one is mine.
```

The `Target` property has the following sub-properties:

* `Bucket` (REQUIRED): The name of the bucket that will store the new object

* `Key` (REQUIRED): The location within the bucket

* `ACL` (OPTIONAL - Default `private`): Sets a [canned ACL](https://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html#canned-acl) for the new object

The following sub-properties also apply if you are creating a new object (but not if you are copying an object from another S3 bucket):

* `ContentType` (OPTIONAL): Sets a custom content type for the new object

The `Body` property simply takes a string which will be used to populate the new object.

### Creating a new S3 object from binary data

You can create a binary file by using the `Base64Body` property and supplying your content base64-encoded. For example:

```yaml
SinglePixel:
  Type: AWS::S3::Object
  Properties:
    Target:
      Bucket: !Ref TargetBucket
      Key: 1pixel.gif
    Base64Body: R0lGODdhAQABAIABAP///0qIbCwAAAAAAQABAAACAkQBADs=
```

### Copying an S3 object from another bucket

To copy an S3 object, you need to specify the `Source` property as well as the `Target`. For example:

```yaml
CopiedObject:
  Type: AWS::S3::Object
  Properties:
    Source:
      Bucket: !Ref SourceBucket
      Key: index.html
    Target:
      Bucket: !Ref TargetBucket
      Key: index.html
      ACL: public-read
```

The `Source` property has the following sub-properties:

* `Bucket` (REQUIRED): The bucket to copy from

* `Key` (REQUIRED): The key of the S3 object that will be copied

## Author

[Steve Engledow](https://linkedin.com/in/stilvoid)  
Senior Solutions Builder  
Amazon Web Services
