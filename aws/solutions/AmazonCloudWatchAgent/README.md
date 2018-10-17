# Deploy AmazonCloudWatchAgent to Ec2 instance by CloudFormation

## issues
Some customers do not know how to install AmazonCloudWatchAgent with cloudformation or how to upgrade the configuration in cloudformation.
This module provides several example templates which explain how to install AmazonCloudWatchAgent and how to upgrade configuration.

### inline
The templates in inline directory give an example about how to embed the json configuration to the metadata.

### ssm
The templates in ssm directory give an example about how to integrate the retrieve the json configuration stored in SSM parameter store.
