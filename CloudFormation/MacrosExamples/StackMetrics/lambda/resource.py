"StackMetrics lambda handler"

from datetime import datetime
import json
import boto3

from custom_response import SUCCESS, FAILED, send

client = boto3.client("cloudwatch")

def log(stack, metric, value):
    "Put metrics into CloudWatch"

    client.put_metric_data(
        Namespace="CloudFormation",
        MetricData=[
            {
                "MetricName": metric,
                "Unit": "Count",
                "Value": value,
                "Timestamp": datetime.now(),
                "Dimensions": [
                    {
                        "Name": "By Stack Name",
                        "Value": stack,
                    },
                ],
            },
        ],
    )

    client.put_metric_data(
        Namespace="CloudFormation",
        MetricData=[
            {
                "MetricName": metric,
                "Unit": "Count",
                "Value": value,
                "Timestamp": datetime.now(),
            },
        ],
    )

def handler(event, context):
    "Lambda handler"

    print("Received request:", json.dumps(event, indent=4))

    action = event["RequestType"]

    stack = event["ResourceProperties"]["StackName"]
    resources = int(event["ResourceProperties"]["ResourceCount"])

    try:
        log(stack, action, 1)

        if action == "Create":
            log(stack, "ResourceCount", resources)

        send(event, context, SUCCESS, {}, f"{stack} metrics")
    except Exception as e:
        send(event, context, FAILED, {
            "Data": str(e),
        }, f"{stack} metrics")

