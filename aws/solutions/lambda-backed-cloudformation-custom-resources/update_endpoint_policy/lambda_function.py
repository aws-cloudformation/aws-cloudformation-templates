#!/usr/bin/env python
"""ClooudFormation custom Lambda backed resource that appends a given bucket ARN to a S3 VPC Endpoint policy."""
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
import os
import boto3
from botocore.vendored import requests


try:
    DEBUG_MODE = os.environ['DEBUG_MODE']
    print("DEBUG_MODE = " + str(DEBUG_MODE))
except KeyError:
    DEBUG_MODE = False  # Manually change when debugging
    print("DEBUG_MODE = " + str(DEBUG_MODE))

try:
    CFN_CLIENT = boto3.client('cloudformation')
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


def connect_to_region(event, context, region):
    """Connect to the given region."""
    try:
        ec2_client = boto3.client(
            'ec2',
            region_name=region,
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to connect to given region, aborting.")
        custom_raise_exception(event, context, error)
    return ec2_client


def validate_inputs(event, context):
    """Evaluate our inputs and error if they are incorrect."""
    if DEBUG_MODE is True:
        print("Received event: \n%s" % json.dumps(event, indent=2))
    if 'StackId' not in event or 'ResourceProperties' not in event:
        custom_raise_exception(event, context, 'Malformed CloudFormation request, missing StackId or ResourceProperties.')
    # Check our CloudFormation parameters
    for parameter in ['vpc-endpoint-id', 'bucket-arn', 'region']:
        if parameter not in event['ResourceProperties']:
            custom_raise_exception(event, context, 'Malformed CloudFormation request, missing one or more ResourceProperties.')
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping CloudFormation role validation due to local testing.")
    else:
        validate_role_on_create(event, context)
    if DEBUG_MODE is True:
        print("Stack ID : %s" % event['StackId'])
        print("Stack Name : %s" % str(event['StackId']).split('/')[1])


def describe_vpc_endpoints(event, context, ec2_client):
    """Run the describe API call."""
    if DEBUG_MODE is True:
        print("Entering function 'describe_vpc_endpoints'")
    try:
        describe_response = ec2_client.describe_vpc_endpoints(
            VpcEndpointIds=[
                event['ResourceProperties']['vpc-endpoint-id'],
                ]
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to connect to given region, aborting.")
        custom_raise_exception(event, context, error)
    if DEBUG_MODE is True:
        print(describe_response)
    if len(describe_response['VpcEndpoints']) < 1:
        custom_raise_exception(event, context, 'VPC Endpoint not found')
    # The policy document is a string, lets convert to dict to make editing easier
    policy_document_dict = json.loads(describe_response['VpcEndpoints'][0]['PolicyDocument'])
    if len(policy_document_dict['Statement']) > 1:
        custom_raise_exception(event, context, 'VPC Endpoint policy has multiple statements, that is not supported by this function')
    return policy_document_dict


def modify_vpc_endpoint(event, context, ec2_client, new_policy_document_dict):
    """Call the modify API."""
    if DEBUG_MODE is True:
        print("Entering function 'modify_vpc_endpoint'")
    try:
        # We need to convert the policy document from dict to string so we use json.dumps
        modify_response = ec2_client.modify_vpc_endpoint(
            PolicyDocument=json.dumps(new_policy_document_dict),
            VpcEndpointId=str(event['ResourceProperties']['vpc-endpoint-id'])
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to connect to given region, aborting.")
        custom_raise_exception(event, context, error)
    if modify_response['Return'] is 'False':
        custom_raise_exception(event, context, 'VPC endpoint policy failed to update')
    return


def cloudformation_create(event, context, ec2_client):
    """Add the given bucket to the VPC endpoint policy."""
    if DEBUG_MODE is True:
        print("Create Option: Attempting to run creation")
    original_policy_document = describe_vpc_endpoints(event, context, ec2_client)
    if isinstance(original_policy_document['Statement'][0]['Resource'], list):
        print("Resource is a list, appending...")
        original_policy_document['Statement'][0]['Resource'].append(str(event['ResourceProperties']['bucket-arn']))
        original_policy_document['Statement'][0]['Resource'].append(str(event['ResourceProperties']['bucket-arn'] + '/*'))
    elif isinstance(original_policy_document['Statement'][0]['Resource'], unicode):
        print("Resource is the default unicode string, replacing")
        original_policy_document['Statement'][0]['Resource'] = [
            str(event['ResourceProperties']['bucket-arn']),
            str(event['ResourceProperties']['bucket-arn'] + '/*')
            ]
    else:
        custom_raise_exception(event, context, 'Endpoint policy looks invalid, Resource stanza is not a list or unicode.')
    if DEBUG_MODE is True:
        print("New policy\n%s" % json.dumps(original_policy_document, indent=2))
    modify_vpc_endpoint(event, context, ec2_client, original_policy_document)
    response_data = {}
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def cloudformation_update(event, context, ec2_client):
    """Cloudformation called us with CreateStack."""
    if DEBUG_MODE is True:
        print("Create Option: Attempting to run update")
    # This should almost never be called for updates, only if a template had a bucket added or removed
    original_policy_document = describe_vpc_endpoints(event, context, ec2_client)
    if event['ResourceProperties']['bucket-arn'] not in original_policy_document[0]['Resource']:
        # Our bucket is not in the policy, add it
        original_policy_document['Statement'][0]['Resource'].append(str(event['ResourceProperties']['bucket-arn']))
        original_policy_document['Statement'][0]['Resource'].append(str(event['ResourceProperties']['bucket-arn'] + '/*'))
        modify_vpc_endpoint(event, context, ec2_client, original_policy_document)
    else:
        # Our bucket is in the policy
        print("Bucket supplied is already in the policy, skipping any actions.")
    response_data = {}
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def cloudformation_delete(event, context, ec2_client):
    """Delete the given bucket from the VPC endpoint policy."""
    if DEBUG_MODE is True:
        print("Create Option: Attempting to run deletion")
    original_policy_document = describe_vpc_endpoints(event, context, ec2_client)
    original_policy_document['Statement'][0]['Resource'].remove(str(event['ResourceProperties']['bucket-arn']))
    original_policy_document['Statement'][0]['Resource'].remove(str(event['ResourceProperties']['bucket-arn'] + '/*'))
    modify_vpc_endpoint(event, context, ec2_client, original_policy_document)
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
    print("event:" + str(event))
    if DEBUG_MODE:
        print("event:" + str(event))
    validate_inputs(event, context)
    ec2_client = connect_to_region(event, context, event['ResourceProperties']['region'])
    if event['RequestType'] == 'Create':
        cloudformation_create(event, context, ec2_client)
    elif event['RequestType'] == 'Update':
        cloudformation_update(event, context, ec2_client)
    elif event['RequestType'] == 'Delete':
        cloudformation_delete(event, context, ec2_client)


if __name__ == '__main__':
    TEST_EVENT = {
        'StackId': '012345678910/fake-stack-id',
        'RequestType': 'Create',
        'ResourceProperties': {
            'vpc-endpoint-id': 'vpce-d6a55bbf',
            'bucket-arn': 'arn:aws:s3:::my_secure_bucket_abc123',
            'region': 'us-west-2'
            }
        }
    TEST_CONTEXT = "bar"
    lambda_handler(TEST_EVENT, TEST_CONTEXT)
