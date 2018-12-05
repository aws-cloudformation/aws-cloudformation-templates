#cfn-response module

This module contains functions that respond on behalf of custom resources you create using AWS CloudFormation.

The module includes a send method, which sends a response object to a custom resource by way of a ResponseURL, which is an Amazon S3 pre-signed URL.

Any Lambda function using this module stops running after executing the module's send method.

For more information, read the AWS documentation [here][1]

[1]: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-cfnresponsemodule
