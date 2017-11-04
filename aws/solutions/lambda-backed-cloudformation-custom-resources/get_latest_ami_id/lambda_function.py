#!/usr/bin/env python
"""ClooudFormation custom Lambda backed resource that returns the latest AMI with the given parameters."""
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
import time
import boto3
from botocore.vendored import requests


DEBUG_MODE = True  # Manually change when debugging
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


def describe_images(event, context):
    """Perform the API call and lookup the AMIs that meet our search criteria."""
    ec2_client = connect_to_region(event, context, event['ResourceProperties']['region'])
    if event['ResourceProperties']['owners'] in (None, ''):
        owners = []
    else:
        owners = event['ResourceProperties']['owners'].split(' ')
    if event['ResourceProperties']['executable-users'] in (None, ''):
        executable_users = []
    else:
        executable_users = event['ResourceProperties']['executable-users'].split(' ')
    try:
        filters = json.loads(event['ResourceProperties']['filters'])
    except Exception as error:  # pylint: disable=W0703
        print("Failed to parse 'filters' parameter from JSON string to python dict, aborting.")
        custom_raise_exception(event, context, error)
    try:
        response = ec2_client.describe_images(
            ExecutableUsers=executable_users,
            Filters=filters,
            Owners=owners
            )
    except Exception as error:  # pylint: disable=W0703
        print("Failed to search AMIs, aborting.")
        custom_raise_exception(event, context, error)
    return response


def validate_inputs(event, context):
    """Evaluate our inputs and error if they are incorrect."""
    if DEBUG_MODE is True:
        print("Received event: \n%s" % json.dumps(event, indent=2))
    if 'StackId' not in event or 'ResourceProperties' not in event:
        custom_raise_exception(event, context, 'Malformed CloudFormation request, missing StackId or ResourceProperties.')
    for parameter in ['owners', 'filters', 'executable-users', 'region']:
        if parameter not in event['ResourceProperties']:
            custom_raise_exception(event, context, 'Malformed CloudFormation request, missing one or more ResourceProperties.')
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping CloudFormation role validation due to local testing.")
    else:
        validate_role_on_create(event, context)
    if DEBUG_MODE is True:
        print("Stack ID : %s" % event['StackId'])
        print("Stack Name : %s" % str(event['StackId']).split('/')[1])


def cloudformation_create(event, context):
    """Cloudformation called us with CreateStack."""
    if DEBUG_MODE is True:
        print("Create Option: Attempting to run creation")
    image_dict = describe_images(event, context)
    if DEBUG_MODE is True:
        print(json.dumps(image_dict, indent=2))
    if len(image_dict['Images']) < 1:
        custom_raise_exception(event, context, 'AMI Search returned no results.')
    newest_entry = {"CreationDate": "1980-01-01T01:01:01.000Z"}
    counter = 0
    for image in image_dict['Images']:
        counter = counter + 1
        if DEBUG_MODE is True:
            print("Loop count: %d" % counter)
        if time.strptime(image['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z") > time.strptime(newest_entry['CreationDate'], "%Y-%m-%dT%H:%M:%S.000Z"):
            newest_entry = image
            if DEBUG_MODE is True:
                print("Found newer entry time of %s" % str(newest_entry['CreationDate']))
    if DEBUG_MODE is True:
        print(json.dumps(newest_entry, indent=2))
    response_data = {
        'ami-id': newest_entry['ImageId']
        }
    if event['StackId'] == '012345678910/fake-stack-id':
        print("Skipping sending CloudFormation response due to local testing.")
        return
    send(event, context, 'SUCCESS', response_data, event['StackId'])
    if DEBUG_MODE is True:
        print("Exiting successfully")
    return


def cloudformation_update(event, context):
    """Cloudformation called us with CreateStack."""
    # For updates we run a new search, maybe the AMI has changed since the last time we ran?
    cloudformation_create(event, context)
    return


def lambda_handler(event, context):
    """Main Lambda function."""
    validate_inputs(event, context)
    if event['RequestType'] == 'Create':
        cloudformation_create(event, context)
    elif event['RequestType'] == 'Update':
        cloudformation_update(event, context)
    elif event['RequestType'] == 'Delete':
        # This resource never truely creates anything so for deletes it just sends a success.
        send(event, context, 'SUCCESS', {}, event['StackId'])
        if DEBUG_MODE is True:
            print("Exiting successfully")
        return


if __name__ == '__main__':
    # Example Linux/Mac CLI command we are replicating
    #   aws ec2 describe-images --owners self amazon --filters "Name=root-device-type,Values=ebs,Name=name,Values=amzn-ami-hvm-????.??.?.*ebs" --query 'Images[*].[CreationDate, ImageId, Name, Description]' --output text | sort -nr | head -n1 | awk '{print $2}'

    # Note: The filters entry must use double quotes inside with encapsulating single quotes
    TEST_EVENT = {
        'StackId': '012345678910/fake-stack-id',
        'RequestType': 'Create',
        'ResourceProperties': {
            'owners': 'self amazon',
            'filters': '[{"Name":"root-device-type","Values":["ebs"]},{"Name":"name","Values":["amzn-ami-hvm-????.??.?.*gp2"]}]',
            'executable-users': '',
            'region': 'us-west-2'
            }
        }
    TEST_CONTEXT = "bar"
    lambda_handler(TEST_EVENT, TEST_CONTEXT)
