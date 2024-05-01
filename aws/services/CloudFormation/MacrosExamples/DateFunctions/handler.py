"Handler lambda code for date function macro"
import traceback
import datetime
import time


def handler(event, _):
    """
    Lambda handler function
    """
    
    print("Received event: " + str(event))

    response = {"requestId": event["requestId"], "status": "success"}
    try:
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)

        # Operation we are being asked to do
        operation = event["params"]["Operation"]

        # Value to work with
        if "Date" in event["params"] and event["params"]["Date"]:
            input_date = datetime.datetime.fromisoformat(event["params"]["Date"])
        else:
            input_date = datetime.datetime.now()

        # Value to work with for deltas
        if "Date2" in event["params"] and event["params"]["Date2"]:
            input_date_2 = datetime.datetime.fromisoformat(event["params"]["Date2"])
        else:
            input_date_2 = datetime.datetime.now()

        # Value for days for subtraction or addition.
        if "Days" in event["params"] and event["params"]["Days"]:
            input_days = event["params"]["Days"]
        else:
            input_days = "0"

        # Make sure the input_days is an integer
        input_days = int(input_days)

        operations = {
            "Current": lambda: input_date,
            "Add": lambda: input_date + datetime.timedelta(days=input_days),
            "Subtract": lambda: input_date - datetime.timedelta(days=input_days),
            "Days": lambda: (input_date.date() - input_date_2.date()).days
        }

        if operation in operations:
            response["fragment"] = str(operations[operation]())
        else:
            # Get the ISO date for the input value
            response["fragment"] = (
                input_date.replace(tzinfo=datetime.timezone(offset=utc_offset))
                .replace(microsecond=0)
                .isoformat()
            )
    except Exception as e:
        traceback.print_exc()
        response["status"] = "failure"
        response["errorMessage"] = str(e)
    return response
