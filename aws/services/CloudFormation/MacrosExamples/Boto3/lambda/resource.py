"Implements the CloudFormation resource handler for the Boto3 macro"

import json
import boto3

from custom_response import send, FAILED, SUCCESS

def execute(action, properties):
    "Executes the requested action"
    actions = action.split(".")

    if len(actions) != 2:
        return "FAILED", f"Invalid boto3 call: {action}"

    client, function = actions[0], actions[1]

    try:
        client = boto3.client(client.lower())
    except Exception as e:
        return "FAILED", f"boto3 error: {e}"

    try:
        function = getattr(client, function)
    except Exception as e:
        return "FAILED", f"boto3 error: {e}"

    properties = {
        key[0].lower() + key[1:]: value
        for key, value in properties.items()
    }

    try:
        function(**properties)
    except Exception as e:
        return "FAILED", f"boto3 error: {e}"

    return "SUCCESS", "Completed successfully"

def handler(event, context):
    "Handle a CloudFormation event"

    print("Received request:", json.dumps(event, indent=4))

    request = event["RequestType"]
    properties = event["ResourceProperties"]

    if any(prop not in properties for prop in ("Action", "Properties")):
        print("Bad properties", properties)
        return send(event, context, FAILED, {}, reason="Missing required parameters")

    mode = properties["Mode"]

    if request == mode or request in mode:
        status, message = execute(properties["Action"], properties["Properties"])
        return send(event, context, status, {}, reason=message)

    return send(event, context, SUCCESS, {}, reason="No action taken")
