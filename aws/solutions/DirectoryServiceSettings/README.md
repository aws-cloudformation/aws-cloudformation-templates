# Directory Settings

## Description

This solution updates the settings for an AD Connector or AWS Managed AD directory.

- Enables directory monitoring by using an Amazon SNS topic to send emails when the status of the directory changes.
- (Optional) Creates a custom access URL that can be used with AWS applications and services, to reach a login page that is associated to the
  directory.
- (Optional) Enable single sign-on, this allows users in your directory to access certain AWS services from a computer joined to the directory without
  having to enter their credentials separately. joined to the directory.
- (Optional) Creates **LAB EXAMPLE** IAM roles that can be used to delegate users/groups access to certain areas of the AWS Management Console.
  - User/Group assignment to these IAM roles has to be done manually via Directory Services -> Directory -> Application Management Tab.

## Notes

- AD Connector is not an AWS CloudFormation supported resource, therefore using an AWS CloudFormation custom resource.
- CloudWatch Logs Log Group uses Amazon managed server-side encryption. Optionally, a KMS CMK can be used.
- SNS Topic using Amazon managed server-side encryption. Optionally, a KMS CMK can be used.

## Resources

- [Monitor your AD Connector directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ad_connector_monitor.html)
- [Monitor your AWS Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_monitor.html)
- [Enable access to AWS applications and services](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_manage_apps_services.html)
- [Creating an access URL](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_create_access_url.html)
- [Single sign-on](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_single_sign_on.html)
- [Enable access to the AWS Management Console with AD credentials](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/ms_ad_management_console_access.html)

## Attributions

Using the [aws-cloudformation/custom-resource-heper](https://github.com/aws-cloudformation/custom-resource-helper) to handle the AWS CloudFormation
Custom Resource responses for the given resources.

## Instructions

1. Run [src/package.sh](src/package.sh) to package the code and dependencies.
2. Upload the [src/directory_settings_custom_resource.zip](src/directory_settings_custom_resource.zip) to an S3 bucket, note the bucket name.
3. Launch the AWS CloudFormation stack using the [DIRECTORY_SETTINGS.cfn.yaml](templates/DIRECTORY_SETTINGS.cfn.yaml) template file as the source.
