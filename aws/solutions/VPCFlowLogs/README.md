# VPCFlowLogs

- [VPCFlowLogs](#vpcflowlogs)
  - [Description](#description)
  - [Notes](#notes)
  - [Resources](#resources)
  - [Instructions (Individual Stacks)](#instructions-individual-stacks)
  - [Instructions (Nested Stacks)](#instructions-nested-stacks)

## Description

This solution lets you enable Flow Logs for a VPC, and publish the flow log data to either Amazon CloudWatch Logs, Amazon S3, or both.

This solution can be implemented as individual templates accordingly, or leveraging the nested stacks `main` templates.

## Notes

- VPC flow log settings are parameterized, so they can be customized as needed.
- Supports publishing VPC flow log data to `Amazon S3` using an existing S3 bucket, or having a new S3 bucket created with encryption.
  - Amazon S3 bucket using Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
    - If using a KMS CMK, an option is provided to enable the use of an
      [Amazon S3 Bucket Key](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/enable-bucket-key.html).
- Supports publishing VPC flow log data to `Amazon CloudWatch Logs`
  - Lets you set the log retention for the log group being used for VPC flow logs.
  - CloudWatch Logs Log Group uses Amazon managed server-side encryption. Optionally, a KMS CMK can be used.

## Resources

- [Publishing flow logs to CloudWatch Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html)
- [Publishing flow logs to Amazon S3](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html)

## Instructions (Individual Stacks)

1. Launch the AWS CloudFormation stack using the [VPCFlowLogsCloudWatch.cfn.yaml](templates/VPCFlowLogsCloudWatch.cfn.yaml) template file as the
   source, to publish logs to Amazon CloudWatch Logs.
2. Launch the AWS CloudFormation stack using the [VPCFlowLogsS3.cfn.yaml](templates/VPCFlowLogsS3.cfn.yaml) template file as the source, to publish
   logs to Amazon S3.

## Instructions (Nested Stacks)

1. Launch the AWS CloudFormation root stack using the [VPCFlowLogs-main.cfn.yaml](templates/VPCFlowLogs-main.cfn.yaml) template file as the source, to
   publish logs to Amazon CloudWatch Logs and/or Amazon S3.
