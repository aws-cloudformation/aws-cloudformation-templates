"S3Object macro custom resource lambda handler"

import base64
import json
import urllib
import boto3
from custom_response import send, FAILED, SUCCESS

s3_client = boto3.client("s3")

def handler(event, context):
    "Lambda handler"
    try:
        return handle_event(event, context)
    except Exception as e:
        print(str(e))
        return send(event, context, FAILED, {}, str(e))

def handle_event(event, context):
    "Handle the event from CloudFormation"

    print("Received request:", json.dumps(event, indent=4))

    request = event["RequestType"]
    properties = event["ResourceProperties"]

    if "Target" not in properties or all(
        prop not in properties for prop in ["Body", "URL", "Base64Body", "Source"]
    ):
        return send(event, context, FAILED, {}, "Missing required parameters")

    target = properties["Target"]

    data = {
        "Bucket": target["Bucket"],
        "Key": target["Key"],
    }

    if request in ("Create", "Update"):
        if "Body" in properties:
            target.update(
                {
                    "Body": properties["Body"],
                }
            )

            s3_client.put_object(**target)

        elif "URL" in properties:
            with urllib.request.urlopen(properties["URL"]) as f:
                content = f.read().decode("utf-8")

            target.update(
                {
                    "Body": content,
                }
            )

            s3_client.put_object(**target)

        elif "Base64Body" in properties:
            try:
                body = base64.b64decode(properties["Base64Body"])
            except Exception:
                return send(event, context, FAILED, {}, "Malformed Base64Body")

            target.update({"Body": body})

            s3_client.put_object(**target)

        elif "Source" in properties:
            source = properties["Source"]

            s3_client.copy_object(
                CopySource=source,
                Bucket=target["Bucket"],
                Key=target["Key"],
                MetadataDirective="COPY",
                TaggingDirective="COPY",
            )

        else:
            return send(event, context, FAILED, {}, "Malformed body")

        return send(event, context, SUCCESS, data, "Created")

    if request == "Delete":
        s3_client.delete_object(
            Bucket=target["Bucket"],
            Key=target["Key"],
        )

        return send(event, context, SUCCESS, data, "Deleted")

    return send(event, context, FAILED, {}, f"Unexpected: {request}")
