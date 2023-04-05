# AWS CloudFormation Macro to expand `AWS::EC2::VPCEndpoint` resource
A VPC endpoint enables private connectivity to [supported AWS services](https://docs.aws.amazon.com/vpc/latest/privatelink/aws-services-privatelink-support.html), where traffic between an Amazon VPC and a service does not leave the Amazon network.

AWS CloudFormation resource type [AWS::EC2::VPCEndpoint](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpcendpoint.html) provisions a VPC Endpoint for a service. When there is a need to create multiple VPC Endpoints the AWS CloudFormation template becomes repetitive and long.
For example:
```yaml
Resources:
  VPCEndpointSsm:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcEndpointType: Interface
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ssm
      VpcId: !Ref myVPC
      SubnetIds:
        - !Ref subnetA
        - !Ref subnetB
      SecurityGroupIds:
        - !Ref mySecurityGroup
  VPCEndpointEc2:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcEndpointType: Interface
      ServiceName: !Sub com.amazonaws.${AWS::Region}.ec2
      VpcId: !Ref myVPC
      SubnetIds:
        - !Ref subnetA
        - !Ref subnetB
      SecurityGroupIds:
        - !Ref mySecurityGroup
  VPCEndpointEC2Messages:
    Type: AWS::EC2::VPCEndpoint
    # ...
  VPCEndpointSsmMessages:
    Type: AWS::EC2::VPCEndpoint
    # ...
```
This Macro can be used to expand the `AWS::EC2::VPCEndpoint` resource resulting in a concise template. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandVPCEndpoint
# ...
Resources:
  VPCEndpoint:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ExpandServiceCodes: "ssm,ssmmessages,ec2,ec2messages"
      VpcEndpointType: Interface
      VpcId: !Ref myVPC
      SubnetIds:
        - !Ref subnetA
        - !Ref subnetB
      SecurityGroupIds:
        - !Ref mySecurityGroup
# ...
```
## Deployment
- Deploy the `macro.yaml` template to a CloudFormation stack e.g. "myp-dev-ExpandVPCEndpoint-macro"
  ```bash
  aws cloudformation deploy --stack-name myp-dev-ExpandVPCEndpoint-macro --template-file ./macro.yaml --capabilities CAPABILITY_NAMED_IAM
  ```
- Provide the parameters, as per your environment, in `params.json` parameter file.
  ```json
  [
    {
      "ParameterKey": "pVPCId",
      "ParameterValue": "vpc-xxx"
    },
    {
      "ParameterKey": "pSubnetIds",
      "ParameterValue": "subnet-aaa,subnet-bbb"
    },
    {
      "ParameterKey": "pSecurityGroupIds",
      "ParameterValue": "sg-xxx"
    }
  ]
  ```
- Deploy the `example.yaml` template to a CloudFormation stack e.g. "myp-dev-ExpandVPCEndpoint-example".
  ```bash
  aws cloudformation deploy --stack-name myp-dev-ExpandVPCEndpoint-example --template-file ./example.yaml --parameter-overrides file://params.json
  ```
## Cleanup
- Delete the "myp-dev-ExpandVPCEndpoint-example" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-ExpandVPCEndpoint-example
  ```
- Delete the "myp-dev-ExpandVPCEndpoint-macro" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-ExpandVPCEndpoint-macro
  ```
<div style="page-break-after: always;"></div>

## Usage
Reference this macro in any AWS CloudFormation template using the top-level resource. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandVPCEndpoint
```
Use custom property `ExpandServiceCodes` to define the comma delimited list of service codes to expand. For example:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: ExpandVPCEndpoint
# ...
Resources:
  VPCEndpointMWAA:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ExpandServiceCodes: "airflow.api,airflow.env,airflow.ops"
      VpcEndpointType: Interface
      # ...
  VPCEndpointECS:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      ExpandServiceCodes: "ecr.api,ecr.dkr,ecs,ecs-agent,ecs-telemetry"
      VpcEndpointType: Interface
      # ...
# ...
```
## Authors

[Vivek Goyal](https://github.com/vivgoyal-aws) AWS ProServ Sr. Cloud Infrastructure Architect
