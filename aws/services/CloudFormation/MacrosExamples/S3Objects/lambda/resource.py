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
import base64
import boto3
import httplib
import json

s3_client = boto3.client("s3")

def sendResponse(event, context, status, message):
    bucket = event["ResourceProperties"].get("Target", {}).get("Bucket")
    key = event["ResourceProperties"].get("Target", {}).get("Key")

    body = json.dumps({
        "Status": status,
        "Reason": message,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "PhysicalResourceId": "s3://{}/{}".format(bucket, key),
        "Data": {
            "Bucket": bucket,
            "Key": key,
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

    if "Target" not in properties or all(prop not in properties for prop in ["Body", "Base64Body", "Source"]):
        return sendResponse(event, context, "FAILED", "Missing required parameters")

    target = properties["Target"]

    if request in ("Create", "Update"):
        if "Body" in properties:
            target.update({
                "Body": properties["Body"],
            })

            s3_client.put_object(**target)

        elif "Base64Body" in properties:
            try:
                body = base64.b64decode(properties["Base64Body"])
            except:
                return sendResponse(event, context, "FAILED", "Malformed Base64Body")

            target.update({
                "Body": body
            })

            s3_client.put_object(**target)

        elif "Source" in properties:
            source = properties["Source"]

            s3_client.copy_object(
                CopySource=source,
                Bucket=target["Bucket"],
                Key=target["Key"],
                MetadataDirective="COPY",
                TaggingDirective="COPY",
                ACL=target["ACL"],
            )

        else:
            return sendResponse(event, context, "FAILED", "Malformed body")

        return sendResponse(event, context, "SUCCESS", "Created")

    if request == "Delete":
        s3_client.delete_object(
            Bucket=target["Bucket"],
            Key=target["Key"],
        )

        return sendResponse(event, context, "SUCCESS", "Deleted")

    return sendResponse(event, context, "FAILED", "Unexpected: {}".format(request))
