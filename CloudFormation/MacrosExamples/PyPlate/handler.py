"""
Lamda handler for the PyPlate macro

Package the CloudFormation template using CloudFormation Rain.
(If you don't want to use Rain, simply embed the contents of
this file to replace the !Rain::Embed directive in the template)
"""

#pylint: disable=exec-used

import traceback
import json


def obj_iterate(obj, params):
    "Iterate over template resources and execute any PyPlate directives"
    if isinstance(obj, dict):
        for k in obj:
            obj[k] = obj_iterate(obj[k], params)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = obj_iterate(v, params)
    elif isinstance(obj, str):
        if obj.startswith("#!PyPlate"):
            params["output"] = None
            exec(obj, params)
            obj = params["output"]
    return obj


def handler(event, _):
    "Lambda handler"

    print(json.dumps(event))

    macro_response = {"requestId": event["requestId"], "status": "success"}
    try:
        params = {
            "params": event["templateParameterValues"],
            "template": event["fragment"],
            "account_id": event["accountId"],
            "region": event["region"],
        }
        response = event["fragment"]
        macro_response["fragment"] = obj_iterate(response, params)
    except Exception as e:
        traceback.print_exc()
        macro_response["status"] = "failure"
        macro_response["errorMessage"] = str(e)
    return macro_response
