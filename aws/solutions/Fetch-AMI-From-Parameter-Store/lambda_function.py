#!/usr/bin/env python
"""CloudFormation Lambda-backed custom resource that fetches an AMI from the Parameter Store based on the parameter name provided."""
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
import json
import time
import boto3
from botocore.vendored import requests
def lambda_handler(event, context):
    print 'REQUEST BODY:n' + str(event)
    parameter_name = (event['ResourceProperties']['Parameter'])
    print parameter_name
    try:
        if event['RequestType'] == 'Delete':
            print "delete"
        elif event['RequestType'] == 'Create':
            print "create"
            client = boto3.client('ssm')
            ami_id = json.loads(client.get_parameter(Name=parameter_name)['Parameter']['Value'])['image_id']
            print ami_id
        elif event['RequestType'] == 'Update':
            print "update"
            client = boto3.client('ssm')
            ami_id = json.loads(client.get_parameter(Name=parameter_name)['Parameter']['Value'])['image_id']
            print ami_id
        responseStatus = 'SUCCESS'
        responseData = {'AMI': ami_id}
        break
    except Exception as e:
        print e
        responseStatus = 'FAILURE'
        responseData = {'Failure': 'Something bad happened.'}
    sendResponse(event, context, responseStatus, responseData)

def sendResponse(event, context, responseStatus, responseData, reason=None, physical_resource_id=None):
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': physical_resource_id or context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    print 'RESPONSE BODY:n' + json.dumps(responseBody)
    responseUrl = event['ResponseURL']
    json_responseBody = json.dumps(responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print "Status code: " + response.reason
    except Exception as e:
        print "send(..) failed executing requests.put(..): " + str(e)

