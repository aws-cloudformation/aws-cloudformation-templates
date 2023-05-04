# AWS CloudFormation Macro to expand `AWS::CloudFormation::Stack` resource
AWS CloudFormation resource type [AWS::CloudFormation::Stack](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stack.html) nests a stack as a resource in a top-level template. When there is a need to create multiple nested stacks (e.g. multiple Amazon ECR repositories, or multiple Amazon S3 buckets) the AWS CloudFormation template becomes repetitive and long.
For example:
```yaml
Resources:
  rPvtRepoHelloWorld:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${pTemplateBucket}/templates/${pEnv}/ecr/ecr-repo.yaml"
      TimeoutInMinutes: '60'
      Parameters:
        pNamespace: !Ref pProject
        pRepoName: hello-world
        pProject: !Ref pProject
        pEnv: !Ref pEnv
  rPvtRepoHelloUsa:
    Type: AWS::CloudFormation::Stack
    Properties:
      # ...
      Parameters:
        pNamespace: !Ref pProject
        pRepoName: hello-usa
        # ...
  rPvtRepoHelloCa:
    Type: AWS::CloudFormation::Stack
    Properties:
      # ...
      Parameters:
        pNamespace: !Ref pProject
        pRepoName: hello-ca
        # ...
  rPvtS3Bucket1:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${pTemplateBucket}/templates/${pEnv}/s3/s3-bucket.yaml"
    #...
  rPvtS3Bucket2:
    Type: AWS::CloudFormation::Stack
    #...
  rPvtS3Bucket3:
    Type: AWS::CloudFormation::Stack
    #...
```
This Macro can be used to expand the `AWS::CloudFormation::Stack` resource resulting in a concise template. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandStack
# ...
Resources:
  rPvtRepo:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${pTemplateBucket}/templates/${pEnv}/ecr/ecr-repo.yaml"
      TimeoutInMinutes: '60'
      Parameters:
        pNamespace: !Ref pProject
        ExpandStack::pRepoName: "hello-world,hello-usa,hello-ca"
        pProject: !Ref pProject
        pEnv: !Ref pEnv
  rPvtS3:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub "https://s3.amazonaws.com/${pTemplateBucket}/templates/${pEnv}/s3/s3-bucket.yaml"
      TimeoutInMinutes: '60'
      Parameters:
        ExpandStack::pBucketName: "bucket1,bucket2,bucket3"
        pProject: !Ref pProject
        pEnv: !Ref pEnv
# ...
```
<div style="page-break-after: always;"></div>

## Deployment
- Deploy the `macro.yaml` template to a CloudFormation stack e.g. "myp-dev-ExpandStack-macro"
  ```bash
  aws cloudformation deploy --stack-name myp-dev-ExpandStack-macro --template-file ./macro.yaml --capabilities CAPABILITY_NAMED_IAM
  ```
- Resource type `AWS::CloudFormation::Stack` requires the stack template(s) be available on an Amazon S3 bucket (e.g. `pTemplateBucket`).
  - If you don't have one already, create one with `aws s3 mb s3://${pTemplateBucket}`
- Provide the parameters, as per your environment, in `params.json` parameter file. Provide the name of an existing bucket for templates in `pTemplateBucket`.
  ```json
  [
    {
      "ParameterKey": "pTemplateBucket",
      "ParameterValue": "<your-template-bucket>"
    },
    {
      "ParameterKey": "pProject",
      "ParameterValue": "myp"
    },
    {
      "ParameterKey": "pEnv",
      "ParameterValue": "dev"
    }
  ]
  ```
- Copy the sample `ecr-repo.yaml` template to `pTemplateBucket` bucket. For example:
  ```bash
  aws s3 cp ecr-repo.yaml s3://${pTemplateBucket}/templates/${pEnv}/ecr/ecr-repo.yaml
  ```
- Copy the sample `s3-bucket.yaml` template to `pTemplateBucket` bucket. For example:
  ```bash
  aws s3 cp s3-bucket.yaml s3://${pTemplateBucket}/templates/${pEnv}/s3/s3-bucket.yaml
  ```
- Deploy the `example.yaml` template to a CloudFormation stack e.g. "myp-dev-ExpandStack-example".
  ```bash
  aws cloudformation deploy --stack-name myp-dev-ExpandStack-example --template-file ./example.yaml --parameter-overrides file://params.json
  ```
## Cleanup
- Delete the "myp-dev-ExpandStack-example" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-ExpandStack-example
  ```
- Delete the "myp-dev-ExpandStack-macro" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-ExpandStack-macro
  ```
<div style="page-break-after: always;"></div>

## Usage
Reference this macro in any AWS CloudFormation template using the top-level resource. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandStack
```
Prefix the parameter that needs expansion with keyword `ExpandStack::`. Provide the comma delimited list of values to expand this parameter to. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandStack
# ...
Resources:
  rPvtRepo:
    Type: AWS::CloudFormation::Stack
    Properties:
      # ...
      Parameters:
        pNamespace: !Ref pProject
        #Only Ref or CommaDelimitedValue is supported
        ExpandStack::pRepoName: "hello-world,hello-usa,hello-ca"
        pProject: !Ref pProject
        pEnv: !Ref pEnv
# ...
```
## Authors

[Vivek Goyal](https://github.com/vivgoyal-aws) AWS ProServ Sr. Cloud Infrastructure Architect
