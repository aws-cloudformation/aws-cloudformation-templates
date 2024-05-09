"S3Objects macro handler. Replaces AWS::S3::Object with a custom resource."

import os

import boto3

LAMBDA_ARN = os.environ["LAMBDA_ARN"]

s3_client = boto3.client("s3")


def handle_template(request_id, template):
    "Process the template and modify instances of AWS::S3::Object"

    print(request_id)

    new_resources = {}

    for name, resource in list(template.get("Resources", {}).items()):
        if resource["Type"] == "AWS::S3::Object":
            props = resource["Properties"]

            if (
                len(
                    [
                        prop
                        for prop in resource["Properties"]
                        if prop in ["Body", "URL", "Base64Body", "Source"]
                    ]
                )
                != 1
            ):
                raise Exception(
                    "You must specify exactly one of: Body, URL, Base64Body, Source"
                )

            target = props["Target"]

            resource_props = {
                "ServiceToken": LAMBDA_ARN,
                "Target": target,
            }

            if "Body" in props:
                resource_props["Body"] = props["Body"]

            elif "URL" in props:
                resource_props["URL"] = props["URL"]

            elif "Base64Body" in props:
                resource_props["Base64Body"] = props["Base64Body"]

            elif "Source" in props:
                resource_props["Source"] = props["Source"]

            resource_props["ServiceTimeout"] = 120

            new_resources[name] = {
                "Type": "Custom::S3Object",
                "Version": "1.0",
                "Properties": resource_props,
            }

    for name, resource in list(new_resources.items()):
        template["Resources"][name] = resource

    return template


def handler(event, _):
    "Macro handler"
    try:
        template = handle_template(event["requestId"], event["fragment"])
    except Exception:
        return {
            "requestId": event["requestId"],
            "status": "failure",
            "fragment": event["fragment"],
        }

    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": template,
    }
