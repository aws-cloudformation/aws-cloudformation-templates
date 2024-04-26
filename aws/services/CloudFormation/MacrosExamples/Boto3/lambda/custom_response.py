"""
Custom resource cfn-response module.
"""

from __future__ import print_function
import json
import urllib3

SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()

#pylint: disable=too-many-arguments,too-many-locals
def send(event, context, response_status,
         response_data, physical_resource_id=None, no_echo=False, reason=None):
    "Send a response to CloudFormation regarding the status of the custom resource."
    response_url = event['ResponseURL']

    print(response_url)

    default_reason = "See the details in CloudWatch Log Stream: {}"

    response_body = {
        'Status' : response_status,
        'Reason' : reason or default_reason.format(context.log_stream_name),
        'PhysicalResourceId' : physical_resource_id or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : no_echo,
        'Data' : response_data
    }

    json_response_body = json.dumps(response_body)

    print("Response body:")
    print(json_response_body)

    headers = {
        'content-type' : '',
        'content-length' : str(len(json_response_body))
    }

    try:
        response = http.request('PUT', response_url, 
                                headers=headers, body=json_response_body)
        print("Status code:", response.status)


    except Exception as e:
        print("send(..) failed executing http.request(..):", e)

