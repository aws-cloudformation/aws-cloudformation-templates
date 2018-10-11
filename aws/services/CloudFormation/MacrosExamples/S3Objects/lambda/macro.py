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

import boto3
import os

LAMBDA_ARN = os.environ["LAMBDA_ARN"]
BUCKET = os.environ["BUCKET"]

s3_client = boto3.client("s3")

def handle_template(request_id, template):
    new_resources = {}

    for name, resource in template.get("Resources", {}).items():
        if resource["Type"] == "AWS::S3::Object":
            props = resource["Properties"]

            target = props["Target"]

            target_bucket = target["Bucket"]
            target_key = target["Key"]
            target_acl = target.get("ACL", "private")

            no_delete = False

            if "Body" in props:
                source_bucket = BUCKET
                source_key = "{}/{}".format(request_id, target_key)

                target.update({
                    "Bucket": source_bucket,
                    "Key": source_key,
                    "ACL": "private",
                    "Body": props["Body"].encode("utf-8"),
                })

                s3_client.put_object(**target)

            elif "Source" in props:
                source_bucket = props["Source"]["Bucket"]
                source_key = props["Source"]["Key"]

                no_delete = True

            new_resources[name] = {
                "Type": "Custom::S3Object",
                "Version": "1.0",
                "Properties": {
                    "ServiceToken": LAMBDA_ARN,
                    "SourceBucket": source_bucket,
                    "SourceKey": source_key,
                    "TargetBucket": target_bucket,
                    "TargetKey": target_key,
                    "ACL": target_acl,
                },
            }

            if no_delete:
                new_resources[name]["Properties"]["NoDelete"] = "true"

    for name, resource in new_resources.items():
        template["Resources"][name] = resource

    return template

def handler(event, context):
    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": handle_template(event["requestId"], event["fragment"]),
    }
