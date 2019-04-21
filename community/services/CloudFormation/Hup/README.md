# Hup Transform

Run
[`cfn-init`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-init.html)
with
[Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html)
instead of
[`cfn-hup`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-hup.html).

## Advantages

1. One less daemon. You don't need `cfn-hup`. You do need
   [SSM Agent](https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html),
   but you can avoid running both of them.
2. No polling. No need to repeatedly poll for changes to
   `AWS::CloudFormation::Init` and no waiting for the `cfn-hup` interval
   for changes to take effect. Changes happen immediately.
3. No managing `cfn-hup` configuration with itself. If you configure
   `cfn-hup` with `cfn-init`, as the examples promote <sup>[1]</sup>
   <sup>[2]</sup>, then there's a chance of making a mistake you can't
   recover from (because it broke `cfn-hup`). By evaluating the
   configuration in the template instead of on the instance, you can
   recover because you can always update the template.
4. Rate control. You can control how many instances are updated at a
   time, without
   [resorting to replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html#aws-attribute-updatepolicy-examples).
   By default, Systems Manager will run `cfn-init` on
   [50 instances](https://docs.aws.amazon.com/systems-manager/latest/userguide/send-commands-multiple.html#send-commands-velocity)
   at a time.

## Example

```YAML
Parameters:
  ImageId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id
Transform: Hup
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Metadata:
      AWS::CloudFormation::Init:
        config:
          files:
            /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json:
              content:
                logs:
                  logs_collected:
                    files:
                      collect_list:
                      - file_path: /var/log/ecs/ecs-init.log
                        timestamp_format: "%Y-%m-%dT%H:%M:%SZ"
          services:
            sysvinit:
              amazon-cloudwatch-agent:
                files:
                - /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
    Properties:
      ImageId: !Ref ImageId
      UserData: !Base64 |
        #cloud-config
        packages:
        - amazon-cloudwatch-agent
        - amazon-ssm-agent
        - aws-cfn-bootstrap
      IamInstanceProfile: !Ref InstanceProfile
  InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
      - !Ref InstanceRole
  InstanceRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Statement:
          Effect: Allow
          Principal:
            Service: ec2.amazonaws.com
          Action: sts:AssumeRole
      ManagedPolicyArns:
      - !Sub arn:${AWS::Partition}:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role
      - !Sub arn:${AWS::Partition}:iam::aws:policy/CloudWatchAgentServerPolicy
      - !Sub arn:${AWS::Partition}:iam::aws:policy/service-role/AmazonEC2RoleforSSM
```

[`macro.py`](macro.py) will append the following
[custom resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html)
to the above template:

```YAML
  InstanceHup:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      Metadata:
        config:
          files:
            /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json:
              content:
                logs:
                  logs_collected:
                    files:
                      collect_list:
                      - file_path: /var/log/ecs/ecs-init.log
                        timestamp_format: "%Y-%m-%dT%H:%M:%SZ"
          services:
            sysvinit:
              amazon-cloudwatch-agent:
                files:
                - /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
      ServiceToken: arn:<partition>:lambda:<region>:<account-id>:function:Hup-CustomResourceFunction-...
      Service: ssm
      Action: send_command
      Parameters:
        DocumentName: AWS-RunShellScript
        Parameters:
          commands:
          - /opt/aws/bin/cfn-init --region ${AWS::Region} --stack ${AWS::StackName} --resource Instance
        Targets:
        - Key: tag:aws:cloudformation:stack-name
          Values:
          - !Ref AWS::StackName
        - Key: tag:aws:cloudformation:logical-id
          Values:
          - Instance
        CloudWatchOutputConfig:
          CloudWatchOutputEnabled: true
      Role: arn:<partition>:iam::<account-id>:role/Hup-SendCommandRole-...
```

Then [`custom_resource.py`](custom_resource.py) takes care of running
`cfn-init` when you make changes to `AWS::CloudFormation::Init`.

The `InstanceHup` `Metadata` is there just to trigger updates to the
custom resource. Otherwise it's ignored. `cfn-init` still uses the
`Instance` `AWS::CloudFormation::Init` metadata exclusively, as usual.

`Metadata` is under the `InstanceHup` `Properties` because otherwise
CouldFormation doesn't trigger updates. The custom resource is triggered
only when its properties change. Again, the `InstanceHup` `Metadata` is
ignored, except to detect changes.

## Auto Scaling Group Example

```YAML
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Metadata:
      AWS::CloudFormation::Init:
        config:
          files:
            /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json:
              content:
                logs:
                  logs_collected:
                    files:
                      collect_list:
                      - file_path: /var/log/ecs/ecs-init.log
                        timestamp_format: "%Y-%m-%dT%H:%M:%SZ"
          services:
            sysvinit:
              amazon-cloudwatch-agent:
                files:
                - /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
    Properties:
      ...
    UpdatePolicy:
      ...
```

`macro.py` will append the following custom resource:

```YAML
  AutoScalingGroupHup:
    Type: AWS::CloudFormation::CustomResource
    Properties:
      Metadata:
        config:
          files:
            /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json:
              content:
                logs:
                  logs_collected:
                    files:
                      collect_list:
                      - file_path: /var/log/ecs/ecs-init.log
                        timestamp_format: "%Y-%m-%dT%H:%M:%SZ"
          services:
            sysvinit:
              amazon-cloudwatch-agent:
                files:
                - /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
      ServiceToken: arn:<partition>:lambda:<region>:<account-id>:function:Hup-CustomResourceFunction-...
      Service: ssm
      Action: send_command
      Parameters:
        DocumentName: AWS-RunShellScript
        Parameters:
          commands:
          - /opt/aws/bin/cfn-init --region ${AWS::Region} --stack ${AWS::StackName} --resource AutoScalingGroup
        Targets:
        - Key: tag:aws:cloudformation:stack-name
          Values:
          - !Ref AWS::StackName
        - Key: tag:aws:cloudformation:logical-id
          Values:
          - AutoScalingGroup
        CloudWatchOutputConfig:
          CloudWatchOutputEnabled: true
      Role: arn:<partition>:iam::<account-id>:role/Hup-SendCommandRole-...
```

[1]: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-init-services
[2]: https://github.com/awslabs/aws-cloudformation-templates/blob/master/aws/solutions/AmazonCloudWatchAgent/inline/amazon_linux.template#L82
