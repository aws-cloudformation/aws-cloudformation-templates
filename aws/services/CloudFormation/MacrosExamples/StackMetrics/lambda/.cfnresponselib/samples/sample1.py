from cfnresponse import register_handler, lambda_handler

@register_handler("create")
def custom_create(event, context):
    # Your custom logic for handling the 'create' action
    response_data = {"message": "Resource creation successful"}
    return response_data

@register_handler("update")
def custom_update(event, context):
    # Your custom logic for handling the 'update' action
    response_data = {"message": "Resource update successful"}
    return response_data

@register_handler("delete")
def custom_delete(event, context):
    # Your custom logic for handling the 'delete' action
    response_data = {"message": "Resource deletion successful"}
    return response_data