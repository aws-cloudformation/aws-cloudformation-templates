# AWS Managed Microsoft AD

## Description

This solution creates an AWS Managed Microsoft AD directory that runs Active Directory (AD).

- (Optional) Create AWS resources (IAM role & instance profile) to support seamlessly join Windows EC2 instances to your AWS Managed Microsoft AD
  directory.
- (Optional) Create AWS resources (IAM role, instance profile, and secret) to support seamlessly join Linux EC2 instances to your AWS Managed
  Microsoft AD directory.
- (Optional) Creates a Domain Members Security Group with **EXAMPLE** rules allowing all Private IP communications inbound.

## Notes

- CloudWatch Logs Log Group uses Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
- Secrets Manager Secrets using Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
- **NOTE** Security Group rules are configured to allow all inbound communications from [RFC1918](https://tools.ietf.org/html/rfc1918#section-3)
  Private Address Space, which includes: `10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16`, this is used as an **EXAMPLE**, however, all security group
  rules can be locked down based on the requirements.
- **NOTE** using the `Admin` AD credentials for the secret created to support seamlessly join Linux EC2 instances to AWS Managed Microsoft AD
  directory as an **EXAMPLE**.
  - However, you can create a new AD user and
    [delegate directory join privileges for AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_join_privileges.html),
    and then update the secret credentials accordingly.

## Resources

- [AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html)
- [AWS Managed Microsoft AD Prerequisites](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_getting_started_prereqs.html)
- [Join an EC2 instance to your AWS Managed Microsoft AD directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_join_instance.html)

## Instructions

1. Launch the AWS CloudFormation stack using the [MANAGEDAD.cfn.yaml](templates/MANAGEDAD.cfn.yaml) template file as the source.
