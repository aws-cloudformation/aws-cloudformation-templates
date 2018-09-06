# StackMetrics macro

When the `StackMetrics` macro is used in a CloudFormation template, any CloudFormation stack deployed from that template will output custom CloudWatch metrics for the stack.

* CloudFormation stack operations
    * Creates
    * Updates
    * Deletes
* CloudFormation resources created

Metrics are provided both per stack and overall across all stacks that are using the macro.

The `macro.template` template also creates a simple dashboard for viewing the aggregated data from these metrics.

See `example.template` for example usage.

## How to install and use the CloudFormation macro in your AWS account

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
        --stack-name stackmetrics-macro \
        --template-file packaged.template \
        --capabilities CAPABILITY_IAM
    ```

4. To test out the macro's capabilities, try launching two stacks from the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name stackmetrics-macro-example-1 \
        --template-file example.template \
        --capabilities CAPABILITY_IAM

    aws cloudformation deploy \
        --stack-name stackmetrics-macro-example-2 \
        --template-file example.template \
        --capabilities CAPABILITY_IAM
    ```

### Usage

To make use of the macro, add `Transform: StackMetrics` to the top level of your CloudFormation template.

Here is a trivial example template:

```yaml
Transform: StackMetrics
Resources:
  Bucket:
    Type: S3::Bucket
```

To see the stack metrics, you can check the `CloudFormation-Stacks` dashboard in the CloudWatch console.

## Authors

[Steve Engledow](https://linkedin.com/in/stilvoid)  
Senior Solutions Builder  
Amazon Web Services

[Jason Gregson](https://linkedin.com/in/jgregson)  
Global Solutions Architect  
Amazon Web Services
