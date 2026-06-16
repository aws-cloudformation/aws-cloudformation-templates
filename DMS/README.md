# AWS CloudFormation Template: Aurora to S3 Migration using AWS DMS

## Description
This CloudFormation template sets up a complete environment for migrating data from an Aurora PostgreSQL database to Amazon S3 using AWS Database Migration Service (DMS). The template creates all necessary resources for both full load and ongoing replication (CDC) from Aurora to S3.

## Prerequisites
Before you deploy this template, you need:
1. An AWS account with permissions to create the required resources
2. Your IP address CIDR for accessing the Aurora database
3. An existing Aurora DB Cluster Snapshot ARN
4. A SecretManager secret with name "aurora-source-enpoint-password" and it should store the password of the source database snapshot.

## Parameters
| Parameter Name | Description | Default | Type |
|---------------|-------------|---------|------|
| ClientIP | IP CIDR range for RDS access | 0.0.0.0/0 | String |
| ExistsDMSVPCRole | Whether dms-vpc-role exists | N | String |
| ExistsDMSCloudwatchRole | Whether dms-cloudwatch-logs-role exists | N | String |
| SnapshotIdentifier | Aurora DB Cluster Snapshot ARN | - | String |

## Usage
1. Navigate to AWS CloudFormation in the AWS Console
2. Create a new stack using this template
3. Fill in the required parameters
4. Review and create the stack
5. Wait for the stack creation to complete

## Outputs
- StackName: Name of the deployed CloudFormation stack
- RegionName: AWS Region where resources are deployed
- S3BucketName: Name of the created S3 bucket
- AuroraEndpoint: Endpoint address of the Aurora cluster

## Security
This template includes several security features:
- Encrypted storage for Aurora and S3
- Security group restrictions
- S3 bucket public access blocking
- IAM roles with least privilege access

## Costs
The resources created by this template will incur AWS charges. Please refer to the [AWS Pricing page](https://aws.amazon.com/pricing/) for details.
