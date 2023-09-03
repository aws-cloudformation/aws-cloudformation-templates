#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0

import urllib3
import json
import traceback

http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
FAILED = "FAILED"

_registered_handlers = {"create": None, "update": None, "delete": None}


class CustomLambdaException(Exception):
    message = "An unknown error occurred."

    def __str__(self):
        return self.message


class InvalidRequestTypeException(CustomLambdaException):
    message = "The provided RequestType is either missing or invalid in the CloudFormation event."


class HookException(CustomLambdaException):
    message = (
        "Missing handler for the specified 'RequestType'. Ensure the handlers are correctly registered. Use either:\n"
        "- @register_handler('create') for def custom_create(event, context) AND @register_handler('update') for def custom_update(event, context)\n"
        "OR\n"
        "- @register_handler('create', 'update') for def custom_create_or_update(event, context)\n"
        "Also ensure:\n"
        "- @register_handler('delete') for def custom_delete(event, context)"
    )


def register_handler(*actions):
    """
    Returns a decorator that registers a user-provided function for multiple CloudFormation actions.

    Parameters:
    - *actions: One or more strings indicating the actions (e.g., 'create', 'update', 'delete').
    """

    def decorator(func):
        for action in actions:
            if action in _registered_handlers:
                _registered_handlers[action] = func
        return func
    return decorator


def send(
    event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False
):
    responseUrl = event["ResponseURL"]

    print(responseUrl)

    responseBody = {}
    responseBody["Status"] = responseStatus
    responseBody["Reason"] = (
        "See the details in CloudWatch Log Stream: " + context.log_stream_name
    )
    responseBody["PhysicalResourceId"] = physicalResourceId or context.log_stream_name
    responseBody["StackId"] = event["StackId"]
    responseBody["RequestId"] = event["RequestId"]
    responseBody["LogicalResourceId"] = event["LogicalResourceId"]
    responseBody["NoEcho"] = noEcho
    responseBody["Data"] = responseData

    json_responseBody = json.dumps(responseBody)

    print("Response body:\n" + json_responseBody)

    headers = {"content-type": "", "content-length": str(len(json_responseBody))}

    try:
        response = http.request(
            "PUT", responseUrl, body=json_responseBody.encode("utf-8"), headers=headers
        )
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))


def lambda_handler(event, context):
    response_status = FAILED
    response_data = {
        "message": CustomLambdaException.message,
        "event": json.dumps(event),
    }

    try:
        request_type = event.get("RequestType")
        if not request_type:
            raise InvalidRequestTypeException

        handler_function = _registered_handlers.get(request_type.lower())
        if not handler_function:
            raise HookException

        response_data = handler_function(event, context)
        response_status = SUCCESS

    except CustomLambdaException as e:
        print(traceback.format_exc())
        response_data = {"message": e.message, "event": json.dumps(event)}
    except Exception as general_exception:
        print(traceback.format_exc())
        response_data = {
            "message": f"Unexpected error occurred: {str(general_exception)}",
            "event": json.dumps(event),
        }
    finally:
        send(event, context, response_status, response_data)
