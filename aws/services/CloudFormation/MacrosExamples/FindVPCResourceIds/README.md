# AWS CloudFormation Macro to find VPC ResourceId(s) by tags
Large organizations often provision VPC and related resources via a centralized provisioning mechanisms. Application teams need a simple method to identify and use these VPC resources in their AWS CloudFormation template. Tagging is a good mechanism to uniquely identify the VPC resources for the target purpose. For example:
```
# VPC for project->myp environment->dev
Tags:
- Key: Project
  Value: myp
- Key: Env
  Value: dev

# VPC for project->myp environment->qa
Tags:
- Key: Project
  Value: myp
- Key: Env
  Value: qa
```
This Macro can be used to find following VPC ResourceId(s) by tags.
- VpcId
- SubnetIds
- SecurityGroupIds

The macro can be used via `Fn::Transform`. For example:
```
rSampleSG:
  Type: AWS::EC2::SecurityGroup
  Properties:
    # ...
    VpcId:
      Fn::Transform:
        Name: FindVPCResourceIdsByTags
        Parameters:
          ResourceType: VpcId # Find VpcId
          #Search by following tags
          Project: myp
          Env: dev
    # ...
rALB:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Type: application
    #...
    Subnets:
      Fn::Transform:
        Name: FindVPCResourceIdsByTags
        Parameters:
          ResourceType: SubnetIds # Find SubnetIds
          ReturnType: StringList  # Return StringList
          #Search VPC by following tags (VPC::<tag>)
          VPC::Project: myp
          VPC::Env: dev
          #Search Subnets by following tags
          ALB: 1
          Project: myp
          Env: env
    IpAddressType: ipv4
    SecurityGroups:
      Fn::Transform:
        Name: FindVPCResourceIdsByTags
        Parameters:
          ResourceType: SecurityGroupIds # Find SecurityGroupIds
          ReturnType: StringList  # Return StringList
          #Search VPC by following tags (VPC::<tag>)
          VPC::Project: myp
          VPC::Env: dev
          #Search SecurityGroups by following tags
          ALB: 1
          Project: myp
          Env: env
    #...
```
<div style="page-break-after: always;"></div>

## Deployment
- Deploy the `macro.yaml` template to a CloudFormation stack e.g. "myp-dev-FindVPCResources-macro"
  ```bash
  aws cloudformation deploy --stack-name myp-dev-FindVPCResources-macro --template-file ./macro.yaml --capabilities CAPABILITY_NAMED_IAM
  ```
- Deploy the `example.yaml` template to a CloudFormation stack e.g. "myp-dev-FindVPCResources-example". **Make sure VPC, Subnet(s), and Security Groups exist and tagged.**
  ```bash
  aws cloudformation deploy --stack-name myp-dev-FindVPCResources-example --template-file ./example.yaml
  ```
## Cleanup
- Delete the "myp-dev-FindVPCResources-example" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-FindVPCResources-example
  ```
- Delete the "myp-dev-FindVPCResources-macro" stack.
  ```bash
  aws cloudformation delete-stack --stack-name myp-dev-FindVPCResources-macro
  ```
<div style="page-break-after: always;"></div>

## Usage
The macro can be used to find following VPC ResourceId(s) by tags.
- VpcId
- SubnetIds
- SecurityGroupIds

Following table describes the parameters that control the behavior of the macro.
| Parameter | Mandatory | Value | Behavior |
| --------- | --------- | --------------- | ----------- |
| ResourceType | Yes | VpcId | Return a single matching VpcId (String). If multiple found, return one. |
| ResourceType | Yes | SubnetIds | Return one ore more matching SubnetIds (StringList/String). |
| ResourceType | Yes | SecurityGroupIds | Return one ore more SecurityGroupIds (StringList/String). |
| ReturnType | No (Default: StringList) | String | Return comma delimited string. |
| ReturnType | No (Default: StringList) | StringList | Return list of strings. |
| TagKey: TagValue | Yes | any: any | Find the requested `ResourceType` by matching tags.<br/>To find SubnetIds and SecurityGroupIds within a VPC, specify the VPC tags by prefixing it with "VPC::". |

## Authors

[Vivek Goyal](https://github.com/vivgoyal-aws) AWS ProServ Sr. Cloud Infrastructure Architect


