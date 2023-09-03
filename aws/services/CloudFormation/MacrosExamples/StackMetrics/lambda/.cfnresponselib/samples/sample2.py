from cfnresponse import register_handler, lambda_handler

@register_handler("create", "update")
def custom_create_or_update(event, context):
    # Your custom logic for handling both 'create' and 'update' actions
    response_data = {"message": "Resource creation or update successful"}
    return response_data

@register_handler("delete")
def custom_delete(event, context):
    # Your custom logic for handling the 'delete' action
    response_data = {"message": "Resource deletion successful"}
    return response_data