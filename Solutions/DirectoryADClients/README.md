# DIRECTORY-AD-CLIENTS

## Description

This solution creates Linux and Windows EC2 instances and joins them to Active Directory (AD) via AD Connector or AWS Managed AD directory via
different SSM Association methods.

- `AWS-JoinDirectoryServiceDomain` SSM document is used to join AD domain.
- To join AD domain, EC2 instances must be able to resolve the AD domain, 2 options provided:
  - By default, DHCPOptionsSet is relied on to be able to resolve the AD domain.
  - If Domain DNS servers are provided, then they are set manually on the EC2 instances.
- Different methods used to initiate the Domain Join, as examples:
  - Windows EC2 instance using an inline SSM association
  - Windows and Linux EC2 instance using an SSM association resource targeting EC2 instance IDs
  - Windows EC2 instance using an SSM association resource targeting EC2 instance tags

## Notes

- For Linux Hosts, the
  [ssm-agent domainjoin plugin](https://github.com/aws/amazon-ssm-agent/blob/mainline/agent/plugins/domainjoin/domainjoin_unix_script.go), ignores
  hostname, and creates a random hostname with prefix "EC2AMAZ-"
- If NetBIOS name already exists in Active Directory, the domain join will fail.
  - Terminating an EC2 instance that was previous joined to Active Directory, does not delete the Computer Name. Remember to delete computer name in
    AD.
- Amazon EBS Volumes using Amazon managed server-side encryption or the CMK set as the default EBS encryption key. Optionally, a KMS CMK can be used.
- Amazon EC2 instance inline SSM associations, provides limited properties compared to using an
  [SSM Association resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-association.html).

## Resources

- [Join an EC2 instance to your AD Connector directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_join_instance.html)
- [Join an EC2 instance to your AWS Managed Microsoft AD directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_join_instance.html)
- [amazon-ssm-agent/agent/plugins/domainjoin](https://github.com/aws/amazon-ssm-agent/tree/mainline/agent/plugins/domainjoin)

## Instructions

1. Launch the AWS CloudFormation stack using the [DIRECTORY-AD-CLIENTS.cfn.yaml](templates/DIRECTORY-AD-CLIENTS.cfn.yaml) template file as the source.
