# AWS CloudFormation Macro to merge IAM policy statements
Often resource policies (e.g. KMS resource policy, S3 resource policy) have common IAM policy statements that need to be applied to multiple IAM policies. These common IAM policy statements make the code repetitive and hard to change.

For example, each AWS KMS key should have policy statements for the KMS administrator's access.
```yaml
# ...
Resources:
  rS3KMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: AWS KMS key for encrypting Amazon S3
      KeyPolicy:
        Id: kms-key-s3
        Version: '2012-10-17'
        Statement:
        # Common for each key
        - Sid: Allow access for Key Administrators
          Effect: Allow
          Principal:
            AWS: !Ref pKMSAdminRoles
          Action:
          - kms:Create*
          #...
          Resource: "*"
        # Common for each key
        - Sid: Allow granting of the key to Key Administrators
          Effect: Allow
          Principal:
            AWS: !Ref pKMSAdminRoles
          Action:
          - kms:CreateGrant
          #...
          Resource: "*"
          Condition:
            #...
        # Common for each key
        - Sid: Allow direct access to key metadata to the account
          Effect: Allow
          Principal:
            AWS: !Sub arn:${AWS::Partition}:iam::${AWS::AccountId}:root
          Action:
          - kms:Describe*
          #...
          Resource: "*"
        # S3 specific
        - Sid: Allow access through Amazon S3 for all principals in the account that are authorized to use Amazon S3
          Effect: Allow
          Principal:
            AWS: "*"
          Action:
          - kms:Encrypt
          #...
          Resource: "*"
          Condition:
            #...
      KeySpec: SYMMETRIC_DEFAULT
      #...
# ...
```
This Macro can be used to merge multiple IAM policy statements from a set of statement files.

The macro can be used via `Fn::Transform`. For example:
```yaml
# ...
Resources:
  rS3KMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: AWS KMS key for encrypting Amazon S3
      KeyPolicy:
        Id: kms-key-s3
        Version: '2012-10-17'
        Statement:
          Fn::Transform:
            Name: MergeStatements
            Parameters:
              #Merge statements in these files
              Files: !Sub templates/${pEnv}/kms-admin.json,templates/${pEnv}/kms-s3.json
      KeySpec: SYMMETRIC_DEFAULT
      #...
  rMWAAKMSKey:
    Type: AWS::KMS::Key
    Properties:
      Description: AWS KMS key for encrypting Amazon MWAA
      KeyPolicy:
        Id: kms-key-mwaa
        Version: "2012-10-17"
        Statement:
          Fn::Transform:
            Name: MergeStatements
            Parameters:
              #Merge statements in these files
              Files: !Sub templates/${pEnv}/kms-admin.json,templates/${pEnv}/kms-s3.json,templates/${pEnv}/kms-logs.json,templates/${pEnv}/kms-mwaa.json
      KeySpec: SYMMETRIC_DEFAULT
      #...
# ...
```
Here, the `Files` parameter points to comma delimited list of `json` files that define the IAM policy statement. For example:
```json
{
    "Statement": [
        {
            "Sid": "Allow access for Key Administrators",
            "Effect": "Allow",
            "Principal": {
                "AWS": {
                    "Ref": "pKMSAdminRoles"
                }
            },
            "Action": [
                "kms:Create*",
                #...
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow granting of the key to Key Administrators",
            "Effect": "Allow",
            "Principal": {
                "AWS": {
                    "Ref": "pKMSAdminRoles"
                }
            },
            "Action": [
                "kms:CreateGrant",
                #...
            ],
            "Resource": "*",
            "Condition": {
              #...
            }
        },
        {
            "Sid": "Allow direct access to key metadata to the account",
            "Effect": "Allow",
            "Principal": {
                "AWS": {
                    "Fn::Sub": "arn:${AWS::Partition}:iam::${AWS::AccountId}:root"
                }
            },
            "Action": [
                "kms:Describe*",
                #...
            ],
            "Resource": "*"
        }
    ]
}
```

<div style="page-break-after: always;"></div>

## Deployment
- Provide the parameters, as per your environment, in `params.json` parameter file. Provide the name of an existing bucket in `pBucketName`, and ARNs of KMS admin roles in `pKMSAdminRoles`
  ```json
  [
    {
      "ParameterKey": "pBucketName",
      "ParameterValue": "<your-template-bucket>"
    },
    {
        "ParameterKey": "pKMSAdminRoles",
        "ParameterValue": "<comma-delimited-list-of-admin-role-arns>"
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
- Deploy the `macro.yaml` template to a CloudFormation stack e.g. "myp-dev-MergeStatements-macro"
  ```bash
  aws cloudformation deploy --stack-name myp-dev-MergeStatements-macro --template-file ./macro.yaml --parameter-overrides file://params.json --capabilities CAPABILITY_NAMED_IAM
  ```
- Copy the sample statement files to bucket. For example:
  ```bash
  aws s3 cp kms-admin.json s3://${pBucketName}/templates/${pEnv}/kms-admin.json
  aws s3 cp kms-s3.json s3://${pBucketName}/templates/${pEnv}/kms-s3.json
  aws s3 cp kms-logs.json s3://${pBucketName}/templates/${pEnv}/kms-logs.json
  aws s3 cp kms-mwaa.json s3://${pBucketName}/templates/${pEnv}/kms-mwaa.json
  ```
- Deploy the `example.yaml` template to a CloudFormation stack e.g. "myp-dev-MergeStatements-example".
  ```bash
  aws cloudformation deploy --stack-name myp-dev-MergeStatements-example --template-file ./example.yaml --parameter-overrides file://params.json
  ```
- Verify the merged key policy on the [AWS KMS console](https://console.aws.amazon.com/kms/home?region=us-east-1#/kms/keys)

## Cleanup
- Delete the "myp-dev-MergeStatements-example" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-MergeStatements-example
  ```
- Delete the "myp-dev-MergeStatements-macro" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-MergeStatements-macro
  ```

## Usage
- Use the macro via the `Fn::Transform` function for any AWS CloudFormation resource that expects IAM policy document. For example:
  ```yaml
  # ...
  KeyPolicy:
    Id: kms-key-mwaa
    Version: "2012-10-17"
    Statement:
      Fn::Transform:
        Name: MergeStatements
        Parameters:
          #Merge statements in these files
          Files: !Sub templates/${pEnv}/kms-admin.json,templates/${pEnv}/kms-s3.json,templates/${pEnv}/kms-logs.json,templates/${pEnv}/kms-mwaa.json
  # ...
  ```
- `Files` parameter is the only mandatory parameter. It points to comma delimited list of `json` files that define the IAM policy statement.
  - Statements in the `json` file may also be parameterized, using the intrinsic function [Ref](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html) and [Sub](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html). For example:
  ```json
  {
    "Statement": [
      {
        "Sid": "Allow access through Amazon S3 for all principals in the account that are authorized to use Amazon S3",
        "Effect": "Allow",
        "Principal": {
          "AWS": "*"
        },
        "Action": [
          "kms:Encrypt",
          # ...
        ],
        "Resource": "*",
        "Condition": {
          "StringEquals": {
            "kms:CallerAccount": {
              "Ref": "AWS::AccountId"
            },
            "kms:ViaService": {
              "Fn::Sub": "s3.${AWS::Region}.amazonaws.com"
            }
          }
        }
      }
    ]
  }
  ```
## Authors

[Vivek Goyal](https://github.com/vivgoyal-aws) AWS ProServ Sr. Cloud Infrastructure Architect
