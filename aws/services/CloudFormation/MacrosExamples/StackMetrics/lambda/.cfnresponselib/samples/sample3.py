from cfnresponse import send

def lambda_handler(event, context):
    response_status = "FAILED"
    response_data = {"message": "An unknown error occurred."}

    try:
        request_type = event.get("RequestType")
        if not request_type:
            raise ValueError("Invalid CloudFormation event. Missing RequestType.")

        if request_type == "Create":
            print("Executing action for Create...")
        elif request_type == "Update":
            print("Executing action for Update...")
        elif request_type == "Delete":
            print("Executing action for Delete...")

        response_status = "SUCCESS"
        response_data = {"message": "Action completed successfully."}

    except Exception as e:
        response_data["message"] = str(e)

    send(event, context, response_status, response_data)