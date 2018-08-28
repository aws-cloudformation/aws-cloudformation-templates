# Using CloudFormation VPC endpoints with cfn-signal

One of the most common use cases for the new CloudFormation VPC endpoints is to
allow resources within a VPC to signal back to CloudFormation `CreationPolicy`
and `WaitConditionHandles` without needing to route across the public internet.

These example templates demonstrate the bare minimum resources required to use
`cfn-signal` from inside a private subnet in both cases.  Resources using
`CreationPolicy` (usually EC2 instances and Auto Scaling Groups) can get their
signals across the CloudFormation endpoint directly, but `WaitConditions` and
`CustomResources` will also need an S3 endpoint in order to respond to the
self-signed URLs for those resources.

I've created versions with Internet Gateways and Bastions to allow the end user
to SSH onto the private EC2 and take a look at what's going on, as well as
fully self-contained VPCs with no external access other than the VPC endpoints.

| Template | CreationPolicy | WaitCondition | IGW/Bastion |
|----------|----------------|---------------|-------------|
| `cfn-endpoint-creationpolicy-no-igw.yaml` | **yes** | no | no |
| `cfn-endpoint-creationpolicy.yaml` | **yes** | no | **yes** |
| `cfn-endpoint-waitcondition-no-igw.yaml` | no | **yes** | no |
| `cfn-endpoint-waitcondition.yaml` | no | **yes** | **yes** |

**NOTE:** If you're signaling back from EC2/Auto Scaling, you really should be using `CreationPolicies`. They're easier to configure and have some cool additional features around auto scaling. Save `WaitCondition` for more complex workflow logic.

For more information:

* [Setting Up VPC Endpoints for AWS CloudFormation
](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-vpce-bucketnames.html)
* [Interface VPC Endpoint (for CloudFormation)](https://docs.aws.amazon.com/vpc/latest/userguide/vpce-interface.html)
* [Gateway VPC Endpoints
 (for S3)](https://docs.aws.amazon.com/vpc/latest/userguide/vpce-gateway.html)
* [AWS::EC2::VPCEndpoint](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html)
* [Creating Wait Conditions in a Template](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-waitcondition.html)
