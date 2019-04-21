from functools import singledispatch
import json
import traceback

import boto3
from botocore.vendored import requests


# https://forums.aws.amazon.com/thread.jspa?threadID=302268
@singledispatch
def restore(value):
  return dict(true=True, false=False).get(value, value)


restore.register(list, lambda value: [restore(element) for element in value])
restore.register(dict, lambda value: {restore(key): restore(value) for key, value in value.items()})


def lambda_handler(event, context):
  try:
    event = restore(event)
    properties = event['ResourceProperties']
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-api.html
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn=properties['Role'], RoleSessionName='session')
    credentials = response['Credentials']
    client = boto3.client(
        properties['Service'],
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
    response = getattr(client, properties['Action'])(**properties['Parameters'])
    response = dict(
        Status='SUCCESS',
        Data=response,
        RequestId=event['RequestId'],
        StackId=event['StackId'],
        LogicalResourceId=event['LogicalResourceId'],
        # https://github.com/aws/aws-lambda-go/blob/master/cfn/wrap.go#L39
        # https://github.com/awsdocs/aws-cloudformation-user-guide/blob/6c35b11cc64b0b7142aa4f34191e841c877eb05b/doc_source/aws-properties-lambda-function-code.md#module-source-code
        PhysicalResourceId=context.log_stream_name,
    )
  except Exception as e:
    traceback.print_exc()
    response = dict(
        Status='FAILED',
        Reason=e,
        RequestId=event['RequestId'],
        StackId=event['StackId'],
        LogicalResourceId=event['LogicalResourceId'],
        PhysicalResourceId=context.log_stream_name,
    )
  requests.put(
      event['ResponseURL'], data=json.dumps(response,
                                            default=format)).raise_for_status()
