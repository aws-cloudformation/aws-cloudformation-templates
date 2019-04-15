from __future__ import print_function
import json
import boto3
import urllib
from botocore.vendored import requests


SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']

    print(responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData

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


print('Loading function')
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    responseData={}

    if(event['RequestType'] == 'Create'):
        try:
            print("Request Type:",event['RequestType'])
            VPCID=event['ResourceProperties']['VPCID']
            #Describe Route Tables API call
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
            responseData={'RoutetableID':RouteTableID}
            print("Sending response to custom resource")
            send(event, context, SUCCESS, responseData)
        except Exception as  e:
            print('Failed to process:', e)
            send(event, context, FAILED, responseData)

    elif(event['RequestType']  == 'Update'):
        try:
            print("Request Type:",event['RequestType'])
            VPCID=event['ResourceProperties']['VPCID']
            #Describe Route Tables API call
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
            responseData={'RoutetableID':RouteTableID}
            print("Sending response to custom resource")
            send(event, context, SUCCESS, responseData)
        except Exception as  e:
            print('Failed to process:', e)
            send(event, context, FAILED, responseData)

    elif(event['RequestType'] == 'Delete'):
        print("Request Type:",event['RequestType'])
        print("Delete Request - No Physical resources to delete")
        send(event, context, SUCCESS, responseData)
