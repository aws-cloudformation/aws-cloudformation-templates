# S3AccessLogs

- [S3AccessLogs](#s3accesslogs)
  - [Description](#description)
  - [Notes](#notes)
  - [Resources](#resources)
  - [Instructions](#instructions)

## Description

This solution creates an Amazon S3 bucket to be used as a destination for S3 server access logs.

## Notes

- If no bucket name is specified, then the bucket name will follow this syntax: `aws-s3-access-logs-<account>-<region>`
- Amazon S3 Buckets using Amazon managed server-side encryption. Using a KMS CMK is not supported.

## Resources

- [Amazon S3 server access logging](https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerLogs.html)
- [Enabling Amazon S3 server access logging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html)

## Instructions

1. Launch the AWS CloudFormation stack using the [S3AccessLogs.cfn.yaml](templates/S3AccessLogs.cfn.yaml) template file as the source.
