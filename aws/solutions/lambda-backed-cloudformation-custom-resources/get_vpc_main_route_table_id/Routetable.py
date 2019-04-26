from __future__ import print_function
import json
import boto3
import urllib
from botocore.vendored import requests

SUCCESS = "SUCCESS"
FAILED = "FAILED"

print('Loading function')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}
    try:
        if event['RequestType'] == 'Delete':
            print("Request Type:",event['RequestType'])
            print("Delete Request - No Physical resources to delete")
        elif event['RequestType'] == 'Create':
            print("Request Type:",event['RequestType'])
            VPCID=event['ResourceProperties']['VPCID']
            RouteTableID=get_vpc(VPCID)
            responseData={'RoutetableID':RouteTableID}
            print("Sending response to custom resource")
        elif event['RequestType'] == 'Update':
            print("Request Type:",event['RequestType'])
            VPCID=event['ResourceProperties']['VPCID']
            RouteTableID=get_vpc(VPCID)
            responseData={'RoutetableID':RouteTableID}
            print("Sending response to custom resource")
        responseStatus = 'SUCCESS'
    except Exception as e:
        print('Failed to process:', e)
        responseStatus = 'FAILURE'
        responseData = {'Failure': 'Something bad happened.'}
    send(event, context, responseStatus, responseData)

def get_vpc(VPCID):
    response = ec2.describe_route_tables (
      Filters=[
        {
          'Name': 'association.main',
          'Values': [ 'true' ]
        },
        {
          'Name': 'vpc-id',
          'Values': [ VPCID ]
        }
      ]
    )
    print("Printing the VPC Route Table ID ....")
    RouteTableID=response['RouteTables'][0]['RouteTableId']
    print(RouteTableID)
    return RouteTableID

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']
    print(responseUrl)
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': physicalResourceId or context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    json_responseBody = json.dumps(responseBody)
    print("Response body:\n" + json_responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
