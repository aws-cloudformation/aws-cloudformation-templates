# AWS CloudFormation Macro to merge local tags with common tags
AWS cloud resources support [tagging](https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html) to identify, organize, search for, and filter resources. Tags are used to categorize resources by purpose, ownership, environment, or other criteria like costing.

A well organized solution involving AWS resources should define a tagging strategy that includes static tags, parameterized tags and local tags. This results into a long list of tags that must be defined for each resource. For example:
```yaml
# ...
Resources:
  rCustomerDataBucket:
    Type: AWS::S3::Bucket
    # ...
    Properties:
      AccessControl: Private
      # ...
      Tags:
        - Key: Project
          Value: !Ref pProject
        - Key: Env
          Value: !Ref pEnv
        - Key: CreatedBy
          Value: !Ref AWS::StackId
        - Key: Team
          Value: my-team
        - Key: Owner
          Value: my-team@example.com
        - Key: Org
          Value: my-org
        - Key: CostCenter
          Value: 99999
        - Key: Purpose
          Value: customer-data
        - Key: Confidentiality
          Value: L3
# ...
```
Any change in the tagging strategy may impact many AWS CloudFormation templates and AWS resources.

This Macro can be used to merge local tags with common static and parameterized tags, resulting in concise and manageable templates.

The macro can be used via `Fn::Transform`. For example:
```yaml
# ...
Resources:
  rCustomerDataBucket:
    Type: AWS::S3::Bucket
    # ...
    Properties:
      AccessControl: Private
      # ...
      Tags:
        Fn::Transform:
          Name: MergeTags
          Parameters:
            TagsFile: !Sub templates/${pEnv}/tags.json
            Purpose: customer-data
            Confidentiality: L3
# ...
```
Here, the `TagsFile` parameter points to a `json` file that defines common static and parameterized tags. For example:
```json
{
  "Tags": [
    {
      "Key": "Project",
      "Value": {
        "Ref": "pProject"
      }
    },
    {
      "Key": "Env",
      "Value": {
        "Ref": "pEnv"
      }
    },
    {
      "Key": "CreatedBy",
      "Value": {
        "Ref": "AWS::StackId"
      }
    },
    {
      "Key": "Team",
      "Value": "my-team"
    },
    {
      "Key": "Owner",
      "Value": "my-team@example.com"
    },
    {
      "Key": "Org",
      "Value": "my-org"
    },
    {
      "Key": "CostCenter",
      "Value": "99999"
    }
  ]
}
```

<div style="page-break-after: always;"></div>

## Deployment
- Provide the parameters, as per your environment, in `params.json` parameter file. Provide the name of an existing bucket in `pBucketName`.
  ```json
  [
    {
      "ParameterKey": "pBucketName",
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
- Deploy the `macro.yaml` template to a CloudFormation stack e.g. "myp-dev-MergeTags-macro"
  ```bash
  aws cloudformation deploy --stack-name myp-dev-MergeTags-macro --template-file ./macro.yaml --parameter-overrides file://params.json --capabilities CAPABILITY_NAMED_IAM
  ```
- Copy the sample common tag file `tags.json` to bucket. For example:
  ```bash
  aws s3 cp tags.json s3://${pBucketName}/templates/${pEnv}/tags.json
  ```
- Deploy the `example.yaml` template to a CloudFormation stack e.g. "myp-dev-MergeTags-example".
  ```bash
  aws cloudformation deploy --stack-name myp-dev-MergeTags-example --template-file ./example.yaml --parameter-overrides file://params.json
  ```
- Verify the merged static, parameterized and local tags for the newly created sample bucket
  ```bash
  aws s3api get-bucket-tagging --bucket ${SampleBucketName}
  {
    "TagSet": [
      {
        "Key": "Project",
        "Value": "myp"
      },
      {
        "Key": "Env",
        "Value": "dev"
      },
      {
        "Key": "CreatedBy",
        "Value": "<stack-arn>"
      },
      {
        "Key": "Team",
        "Value": "my-team"
      },
      {
        "Key": "Owner",
        "Value": "my-team@example.com"
      },
      {
        "Key": "Org",
        "Value": "my-org"
      },
      {
        "Key": "CostCenter",
        "Value": "99999"
      },
      {
        "Key": "Purpose",
        "Value": "customer-data"
      },
      {
        "Key": "Confidentiality",
        "Value": "L3"
      }
    ]
  }
  ```
## Cleanup
- Delete the "myp-dev-MergeTags-example" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-MergeTags-example
  ```
- Delete the "myp-dev-MergeTags-macro" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-MergeTags-macro
  ```

## Usage
- Use the macro via the `Fn::Transform` function for any AWS CloudFormation resource that supports [Tags](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html) property. For example:
  ```yaml
  # ...
  Tags:
    Fn::Transform:
      Name: MergeTags
      Parameters:
        TagsFile: !Sub templates/${pEnv}/tags.json
  # ...
  ```
- `TagsFile` parameter is the only mandatory parameter. It points to a `json` file that defines common tags.
  - Tags in the `json` file may be static. For example:
    ```json
    {
      "Tags": [
        {
          "Key": "CostCenter",
          "Value": "99999"
        }
      ]
    }
    ```
  - Tags in the `json` file may also be parameterized, using the intrinsic function [Ref](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html). For example:
    ```json
    {
      "Tags": [
        {
          "Key": "Env",
          "Value": {
            "Ref": "pEnv"
          }
        },
        {
          "Key": "CreatedBy",
          "Value": {
            "Ref": "AWS::StackId"
          }
        }
      ]
    }
    ```
- Resource specific local tags can be specified via additional `TagKey: TagValue` parameters. For example:
  ```yaml
  # ...
  Tags:
    Fn::Transform:
      Name: MergeTags
      Parameters:
        TagsFile: !Sub templates/${pEnv}/tags.json
        Purpose: customer-data
        Confidentiality: L3
  # ...
  ```
## Authors

[Vivek Goyal](https://github.com/vivgoyal-aws) AWS ProServ Sr. Cloud Infrastructure Architect

