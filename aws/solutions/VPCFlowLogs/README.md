# VPCFlowLogs

- [VPCFlowLogs](#vpcflowlogs)
  - [Description](#description)
  - [Resources](#resources)
  - [Solution Highlights](#solution-highlights)
  - [Instructions (Individual Templates)](#instructions-individual-templates)
  - [Instructions (Nested Stacks)](#instructions-nested-stacks)

## Description

This solution lets you enable Flow Logs for a VPC, and publish the flow log data to either CloudWatch Logs, S3, or both.

This solution can be implemented as individual templates accordingly, or leveraging the nested stacks `main` templates.

## Resources

- [Publishing flow logs to CloudWatch Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html)
- [Publishing flow logs to Amazon S3](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html)

## Solution Highlights

This solution provides methods to enable VPC flow logs, as designed. This solution can also be used as a reference in creating other CloudFormation
templates.

- VPC flow log settings are parameterized, so they can be customized as needed.
- Supports publishing VPC flow log data to `S3` using an existing S3 bucket, or having a new S3 bucket created with encryption.
  - By default, server-side encryption with Amazon S3-managed encryption keys
    [SSE-S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html) that uses `AES-256`.
  - If KMS Key is provided, then server-side encryption is done with the specified KMS CMK
    ([SSE-KMS](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html))
    - An option is provided to enable the use of an [S3 Bucket Key](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/enable-bucket-key.html).
- Supports publishing VPC flow log data to `CloudWatch Logs`
  - Lets you set the log retention for the log group being used for VPC flow logs.
  - By default, log group data is encrypted with CloudWatch Logs managing the server-side encryption keys.
  - If KMS Key is provided, then server-side encryption is done with the specified
    [KMS CMK](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/encrypt-log-data-kms.html)

## Instructions (Individual Templates)

1. Deploy [VPCFlowLogsCloudWatch.cfn.yaml](templates/VPCFlowLogsCloudWatch.cfn.yaml) template to enable VPC Flow Logs and publish data to CloudWatch
   Logs.
2. Deploy [VPCFlowLogsS3.cfn.yaml](templates/VPCFlowLogsS3.cfn.yaml) template to enable VPC Flow Logs and publish data to S3.

## Instructions (Nested Stacks)

1. Deploy [VPCFlowLogs-main.cfn.yaml](templates/VPCFlowLogs-main.cfn.yaml) template to enable VPC Flow Logs to CloudWatch Logs, S3, or both.
