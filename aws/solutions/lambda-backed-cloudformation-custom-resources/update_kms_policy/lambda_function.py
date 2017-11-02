#!/usr/bin/env python
"""ClooudFormation custom Lambda backed resource that appends/removes given properties to a KMS key policy."""
# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
########################################################
# Changelog
# 1.0.0
#   Made compliant with major Python linters
#     flake8 (pep8 & pyflakes)
#       Disabled E501 (line length)
#       Disabled E241 (whitespace after comma)
#     OpenStack Style Guide
#       Disabled H306 (alphabetize imports)
#     pep257
#     pycodestyle
#     pylint
#       Disabled C0301 (line length)
#       Disabled C0326 (whitespace after comma)
from __future__ import print_function
import json
import boto3
from botocore.vendored import requests


DEBUG_MODE = True  # Manually change when debugging
try:
    CFN_CLIENT = boto3.client('cloudformation')
    KMS_CLIENT = boto3.client('kms')
except Exception as error:
    print('Error creating boto3.client, error text follows:\n%s' % error)
    raise Exception(error)


def format_response_body(event, context, response_status, response_data, physical_resource_id):
    """Format the response for Cloudformation."""
    if DEBUG_MODE is True:
        print("Started function format_response_body")
    response_body = {}
    response_body['Status'] = response_status
    if response_status is "FAILED":
        response_body['Reason'] = response_data['Message']
    else:
        response_body['Reason'] = "completed"
    response_body['PhysicalResourceId'] = physical_resource_id or context.log_stream_name
    response_body['StackId'] = event['StackId']
    response_body['RequestId'] = event['RequestId']
    response_body['LogicalResourceId'] = event['LogicalResourceId']
    response_body['Data'] = response_data
    if DEBUG_MODE is True:
        print("Finished function format_response_body")
    return response_body


def send(event, context, response_status, response_data, physical_resource_id):
    """Send a response."""
    if 'ResponseURL' in event:
        if DEBUG_MODE is True:
            print("Started function send")
            print("CF Response URL: " + event['ResponseURL'])
        response_body = format_response_body(event, context, response_status, response_data, physical_resource_id)
        json_response_body = json.dumps(response_body)
        if DEBUG_MODE is True:
            print("CF Response Body: %s" % str(json_response_body))
        headers = {
            'content-type': '',
            'content-length': str(len(json_response_body))
            }
        try:
            response = requests.put(
                event['ResponseURL'],
                data=json_response_body,
                headers=headers
                )
            if DEBUG_MODE is True:
                print("CF Status code: ", response.reason)
                print("Finished function send")
        except Exception as error:  # pylint: disable=W0703
            print("Failed to send event, raising exception without retrying.")
            raise Exception(error)


def validate_role_on_create(event, context):
    """Validate the role we are running as is the right one."""
    if DEBUG_MODE is True:
        print("Started function validate_role_on_create")
    try:
        describe_stacks_response = CFN_CLIENT.describe_stacks(
            StackName=event['StackId']
            )
    except Exception as error:  # pylint: disable=W0703
        custom_raise_exception(event, context, str('Error describing our stack to discover our IAM role, error text follows:\n' + str(error)))
    if 'Stacks' in describe_stacks_response:
        if describe_stacks_response['Stacks']:
            if 'RoleARN' in describe_stacks_response['Stacks'][0]:
                stack_role = describe_stacks_response['Stacks'][0]['RoleARN']
            else:
                stack_role = None
        else:
            stack_role = None
    else:
        stack_role = None
    if DEBUG_MODE is True:
        print("Finished function validate_role_on_create, role is %s" % stack_role)


def custom_raise_exception(event, context, message):
    """Raise an exception, print error, etc."""
    print(message)
    response_data = {
        'Message': message
        }
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
    else:
        send(event, context, 'FAILED', response_data, None)
    raise Exception(message)


def validate_inputs(event, context):
    """Evaluate our inputs and error if they are incorrect."""
    if DEBUG_MODE is True:
        print("Received event: \n%s" % json.dumps(event, indent=2))
    if 'StackId' not in event or 'ResourceProperties' not in event:
        custom_raise_exception(event, context, 'Malformed CloudFormation request, missing StackId or ResourceProperties.')
    # Check our CloudFormation parameters
    for parameter in ['kms-key-id-arn', 'iam-principal-arn', 'actions-csv']:
        if parameter not in event['ResourceProperties']:
            custom_raise_exception(event, context, 'Malformed CloudFormation request, missing one or more ResourceProperties.')
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping CloudFormation role validation due to local testing.")
    else:
        validate_role_on_create(event, context)
    if DEBUG_MODE is True:
        print("Stack ID : %s" % event['StackId'])
        print("Stack Name : %s" % str(event['StackId']).split('/')[1])


def get_kms_key_policy(event, context):
    """Retrieve the KMs key policy and return it."""
    if DEBUG_MODE is True:
        print("Started function 'get_kms_key_policy'.")
    try:
        kms_response = KMS_CLIENT.get_key_policy(
            KeyId=event['ResourceProperties']['kms-key-id-arn'],
            PolicyName='default'
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to retrieve the KMS key policy, aborting.")
        custom_raise_exception(event, context, error)
    if DEBUG_MODE is True:
        print("Retrieved key policy\n%s" % json.dumps(kms_response))
    return kms_response


def modify_kms_policy(event, context, new_policy_document_dict):
    """Call the modify API."""
    if DEBUG_MODE is True:
        print("Entering function 'modify_kms_policy'")
    try:
        # We need to convert the policy document from dict to string so we use json.dumps
        KMS_CLIENT.put_key_policy(
            KeyId=event['ResourceProperties']['kms-key-id-arn'],
            PolicyName='default',
            Policy=json.dumps(new_policy_document_dict),
            BypassPolicyLockoutSafetyCheck=False
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to update KMS key policy, aborting.")
        custom_raise_exception(event, context, error)
    return


def cloudformation_create(event, context):
    """Add the given permissions to the KMS key policy for the specified IAM ARN."""
    if DEBUG_MODE is True:
        print("Create Option: Attempting to run creation")
    original_policy_document = get_kms_key_policy(event, context)
    policy_json = json.loads(original_policy_document['Policy'])
    if isinstance(policy_json['Statement'], list):
        print("Resource is a list, appending...")
        policy_json['Statement'].append(
            {
                "Action": event['ResourceProperties']['actions-csv'].split(','),
                "Principal": {
                    "AWS": event['ResourceProperties']['iam-principal-arn']
                    },
                "Resource": "*",
                "Effect": "Allow"
                }
            )
        print(json.dumps(policy_json, indent=2))
    else:
        custom_raise_exception(event, context, 'Endpoint policy looks invalid, Statement stanza is not a list.')
    if DEBUG_MODE is True:
        print("New policy\n%s" % json.dumps(policy_json, indent=2))
    modify_kms_policy(event, context, policy_json)
    response_data = {}
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def cloudformation_update(event, context):
    """Cloudformation called us with CreateStack."""
    if DEBUG_MODE is True:
        print("Update Option: Not supported")
    response_data = {}
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def cloudformation_delete(event, context):
    """Delete the given IAM ARN from the KMS key policy."""
    if DEBUG_MODE is True:
        print("Delete Option: Attempting to remove IAM ARN from KMS key policy")
    original_policy_document = get_kms_key_policy(event, context)
    policy_json = json.loads(original_policy_document['Policy'])
    stanza_to_search_for = {
        "Action": event['ResourceProperties']['actions-csv'].split(','),
        "Principal": {
            "AWS": event['ResourceProperties']['iam-principal-arn']
            },
        "Resource": "*",
        "Effect": "Allow"
        }
    if stanza_to_search_for in policy_json['Statement']:
        print('test')
        policy_json['Statement'].remove(stanza_to_search_for)
    else:
        custom_raise_exception(event, context, 'Stanza not found in KMS key policy, nothing to delete, aborting.')
    if DEBUG_MODE is True:
        print("New policy\n%s" % json.dumps(policy_json, indent=2))
    modify_kms_policy(event, context, policy_json)
    response_data = {}
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def lambda_handler(event, context):
    """Main Lambda function."""
    validate_inputs(event, context)
    if event['RequestType'] == 'Create':
        cloudformation_create(event, context)
    elif event['RequestType'] == 'Update':
        cloudformation_update(event, context)
    elif event['RequestType'] == 'Delete':
        cloudformation_delete(event, context)


if __name__ == '__main__':
    TEST_EVENT = {
        'StackId': '012345678910/fake-stack-id',
        'RequestType': 'Create',
        'ResourceProperties': {
            'kms-key-id-arn': 'arn:aws:kms:us-west-2:012345678901:key/0000AAAA-BB11-CC22-DD33-EEEEEE444444',
            'iam-principal-arn': 'arn:aws:iam::012345678901:role/MyRoleName',
            'actions-csv': 'Encrypt,Decrypt,Generate*,Get*,List*,ReEncrypt*'
            }
        }
    TEST_CONTEXT = "bar"
    lambda_handler(TEST_EVENT, TEST_CONTEXT)
