"Implements the Boto3 CloudFormation Macro"
import os

PREFIX = "Boto3::"

LAMBDA_ARN = os.environ["LAMBDA_ARN"]

def handle_template(template):
    "Handle a template, replacing any Boto3::* resources with Custom::Boto3"

    for _, resource in template.get("Resources", {}).items():
        if resource["Type"].startswith(PREFIX):
            resource.update({
                "Type": "Custom::Boto3",
                "Version": "1.0",
                "Properties": {
                    "ServiceToken": LAMBDA_ARN,
                    "Mode": resource.get("Mode", ["Create", "Update"]),
                    "Action": resource["Type"][len(PREFIX):],
                    "Properties": resource.get("Properties", {}),
                },
            })

            if "Mode" in resource:
                del resource["Mode"]

    return template


def handler(event, _):
    "Handle a CloudFormation event"

    fragment = event["fragment"]
    status = "success"

    try:
        fragment = handle_template(event["fragment"])
    except Exception:
        status = "failure"

    return {
        "requestId": event["requestId"],
        "status": status,
        "fragment": fragment,
    }
