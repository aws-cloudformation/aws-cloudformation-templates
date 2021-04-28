# AD Connector

## Description

This solution creates an AD Connector to connect to an on-premises directory.

- (Optional) Create AWS resources (IAM role & instance profile) to support seamlessly join Windows EC2 instances to your AD Connector directory.
- (Optional) Create AWS resources (IAM role, instance profile, and secret) to support seamlessly join Linux EC2 instances to your AD Connector
  directory.
- (Optional) Creates a Domain Members Security Group with **EXAMPLE** rules allowing all Private IP communications inbound.

## Notes

- AD Connector is not an AWS CloudFormation supported resource, therefore using an AWS CloudFormation custom resource.
- CloudWatch Logs Log Group uses Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
- Secrets Manager Secrets using Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
- **NOTE** Security Group rules are configured to allow all inbound communications from [RFC1918](https://tools.ietf.org/html/rfc1918#section-3)
  Private Address Space, which includes: `10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16`, this is used as an **EXAMPLE**, however, all security group
  rules can be locked down based on the requirements.

## Resources

- [Active Directory Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_ad_connector.html)
- [AD Connector Prerequisites](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/prereq_connector.html)
- [Join an EC2 instance to your AD Connector directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_join_instance.html)

## Attributions

Using the [aws-cloudformation/custom-resource-heper](https://github.com/aws-cloudformation/custom-resource-helper) to handle the AWS CloudFormation
Custom Resource responses for the given resources.

## Instructions

1. Run [src/package.sh](src/package.sh) to package the code and dependencies.
2. Upload the [src/adconnector_custom_resource.zip](src/adconnector_custom_resource.zip) to an S3 bucket, note the bucket name.
3. Launch the AWS CloudFormation stack using the [ADCONNECTOR.cfn.yaml](templates/ADCONNECTOR.cfn.yaml) template file as the source.
