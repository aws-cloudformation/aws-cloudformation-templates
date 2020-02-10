#!/usr/bin/env python
"""CloudFormation Lambda-backed custom resource that fetches an AMI from the Parameter Store based on the parameter name provided."""
 # Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
            ami_id = client.get_parameter(Name=parameter_name)['Parameter']['Value']
            print ami_id
        elif event['RequestType'] == 'Update':
            print "update"
            client = boto3.client('ssm')
            ami_id = client.get_parameter(Name=parameter_name)['Parameter']['Value']
            print ami_id
        responseStatus = 'SUCCESS'
        responseData = {'AMI': ami_id}
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