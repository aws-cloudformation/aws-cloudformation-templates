# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from urllib2 import build_opener, HTTPHandler, Request
import boto3
import httplib
import json

s3_client = boto3.client("s3")

def sendResponse(event, context, status, message):
    body = json.dumps({
        "Status": status,
        "Reason": message,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "PhysicalResourceId": "s3://{}/{}".format(
            event["ResourceProperties"].get("TargetBucket"),
            event["ResourceProperties"].get("TargetKey"),
        ),
        "Data": {
            "Bucket": event["ResourceProperties"].get("TargetBucket"),
            "Key": event["ResourceProperties"].get("TargetKey"),
        },
    })

    request = Request(event['ResponseURL'], data=body)
    request.add_header('Content-Type', '')
    request.add_header('Content-Length', len(body))
    request.get_method = lambda: 'PUT'

    opener = build_opener(HTTPHandler)
    response = opener.open(request)

def handler(event, context):
    print("Received request:", json.dumps(event, indent=4))

    request = event["RequestType"]
    properties = event["ResourceProperties"]

    if any(key not in properties for key in ("SourceBucket", "SourceKey", "TargetBucket", "TargetKey")):
        return sendResponse(event, context, "FAILED", "Missing required parameters")

    if request in ("Create", "Update"):
        s3_client.copy_object(
            CopySource={
                "Bucket": properties["SourceBucket"],
                "Key": properties["SourceKey"],
            },
            Bucket=properties["TargetBucket"],
            Key=properties["TargetKey"],
            MetadataDirective="COPY",
            TaggingDirective="COPY",
            ACL=properties["ACL"],
        )

        if not properties.get("NoDelete"):
            s3_client.delete_object(
                Bucket=properties["SourceBucket"],
                Key=properties["SourceKey"],
            )

        return sendResponse(event, context, "SUCCESS", "Created")

    if request == "Delete":
        s3_client.delete_object(
            Bucket=properties["TargetBucket"],
            Key=properties["TargetKey"],
        )

        return sendResponse(event, context, "SUCCESS", "Deleted")

    return sendResponse(event, context, "FAILED", "Unexpected: {}".format(request))
