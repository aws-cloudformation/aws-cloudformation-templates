# S3AccessLogs

- [S3AccessLogs](#s3accesslogs)
  - [Description](#description)
  - [Resources](#resources)
  - [Solution Highlights](#solution-highlights)
  - [Instructions](#instructions)

## Description

This solution creates an S3 bucket to be used as a destination for S3 server access logs.

## Resources

- [Amazon S3 server access logging](https://docs.aws.amazon.com/AmazonS3/latest/dev/ServerLogs.html)

## Solution Highlights

- Creates a new S3 bucket with encryption.
  - If no bucket name is specified, then bucket name will follow this syntax: `aws-s3-access-logs-<account>-<region>`
  - Server-side encryption with Amazon S3-managed encryption keys
    [SSE-S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingServerSideEncryption.html) that uses `AES-256` is used.

## Instructions

1. Deploy [S3AccessLogs.cfn.yaml](templates/S3AccessLogs.cfn.yaml) template to create an S3 bucket that can be used as a destination for S3 server
   access logs.
