# PrefixListResource
AWS CloudFormation Lambda-backed Custom Resource for retrieving the PrefixListID associated with a Gateway VPC Endpoint (S3/DynamoDB).  This can be used to define egress rules for the Security Groups associated with private EC2 instances.

The lambda function is written in Python and based on the  [crhelper.py](https://github.com/awslabs/aws-cloudformation-templates/tree/master/community/custom_resources/python_custom_resource_helper) Custom Resource framework.

* `FunctionCode` contains the lambda function and helper libraries.
* `Templates` contains the function deploy templateÂ and a sample WaitCondition template with egress rules defined.

## Install

### Using the aws cli:

You can install the function using the CloudFormation [`package`](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html) and [`deploy`](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/deploy/index.html) commands.
You will need an S3 bucket to store the lambda function code.  Once you've created the bucket,
 run the following CLI commands to create the function stack:

```
aws cloudformation package \
  --template-file Templates/function-template.yaml \
  --s3-bucket *Your S3 bucket* \
  --s3-prefix *Your S3 object prefix* \
  --output-template-file Templates/packaged-function-template.yaml
```

```
aws cloudformation deploy \
  --template-file Templates/packaged-function-template.yaml \
  --stack-name GetPLCustomResource \
  --capabilities CAPABILITY_IAM
```

CloudFormation will package up the python files, upload them to your S3 bucket, create the lambda function with appropriate permissions and export the Lambda function ARN as `GetPLCustomResource` for use in other stacks.


## Sample CloudFormation snippet:

The following YAML snippet demonstrates how to retrieve and use a Prefix List from within your template using the regional service name associated with your endpoint:

```yaml
Resources:
  S3PrefixListID:
    DependsOn: S3Endpoint
    Type: Custom::GetPL
    Properties:
      ServiceToken:
        Fn::ImportValue: GetPLCustomResource
      PrefixListName: !Sub "com.amazonaws.${AWS::Region}.s3"```
  PrivateSG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: "Outbound traffic to S3"
      SecurityGroupEgress:
      -
          IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          DestinationPrefixListId: !GetAtt S3PrefixListID.PrefixListID
      VpcId: !Ref VPC
```