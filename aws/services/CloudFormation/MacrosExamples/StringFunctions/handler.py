"StringFunctions macro handler"

import traceback


def handler(event, _):
    "Process the template fragment"

    response = {"requestId": event["requestId"], "status": "success"}
    try:
        operation = event["params"]["Operation"]
        input_string = event["params"]["InputString"]
        no_param_string_funcs = ["Upper", "Lower", "Capitalize", "Title", "SwapCase"]
        if operation in no_param_string_funcs:
            response["fragment"] = getattr(input_string, operation.lower())()
        elif operation == "Strip":
            chars = None
            if "Chars" in event["params"]:
                chars = event["params"]["Chars"]
            response["fragment"] = input_string.strip(chars)
        elif operation == "Replace":
            old = event["params"]["Old"]
            new = event["params"]["New"]
            response["fragment"] = input_string.replace(old, new)
        elif operation == "MaxLength":
            length = int(event["params"]["Length"])
            if len(input_string) <= length:
                response["fragment"] = input_string
            elif "StripFrom" in event["params"]:
                if event["params"]["StripFrom"] == "Left":
                    response["fragment"] = input_string[len(input_string) - length :]
                elif event["params"]["StripFrom"] != "Right":
                    response["status"] = "failure"
            else:
                response["fragment"] = input_string[:length]
        else:
            response["status"] = "failure"
    except Exception as e:
        traceback.print_exc()
        response["status"] = "failure"
        response["errorMessage"] = str(e)
    return response
