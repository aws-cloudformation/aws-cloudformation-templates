# Join a new EC2 Windows to AD with no Powershelll

Cloudformation template that will join a new Windows Server instance to Active Directory without powershell in UserData.

Template will invoke the following:

- Create SSM Document
- Create IAM Role for the EC2 instance with the AWS Managed policy 'AmazonEC2RoleforSSM'
- Create EC2 Instance
- Attach the SSM document and IAM role to EC2 Instance
- Join EC2 instance to the Domain using EC2::Instance -> SsmAssociations
Prerequisites.

AWS Simple AD or Microsoft AD and have the following details:

- Directory ID
- Directory Name
- DNS Addresses