## Custom Resource Helper

### NOTE
> This implementation has been deprecated in favor of https://github.com/aws-cloudformation/custom-resource-helper which has a richer feature set, is cleaner to implement and can be installed as a pip module.

The crhelper python script can be saved into your lambda zip to simplify best practice Custom Resource creation. It provides exception and timeout trapping, sending responses to CloudFormation and provides detailed, configurable logging.

### Usage
In order to use it in your custom resource function, save crhelper.py in the root of your function zip path. Your handler file will then only need to import crhelper, define any init code and functions for create,update and delete events. For example:

```python
import crhelper

# initialise logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    # Place initialization code here
    logger.info("Container initialization completed")
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e


def create(event, context):
    """
    Place your code to handle Create events here.
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    physical_resource_id = 'myResourceId'
    response_data = {}
    return physical_resource_id, response_data


def update(event, context):
    """
    Place your code to handle Update events here
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    physical_resource_id = event['PhysicalResourceId']
    response_data = {}
    return physical_resource_id, response_data


def delete(event, context):
    """
    Place your code to handle Delete events here
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    return


def handler(event, context):
    """
    Main handler function, passes off it's work to crhelper's cfn_handler
    """
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)
```

### Logging
crhelper includes logging handling, to log a warning to CloudWatch:

```python
logger.warning("My log message")
```

By default log level is set to warning. This can be customized by defining the "loglevel" property in the custom resource resource in your template. For example:
```json
"MyCustomResource": {
    "Type": "AWS::CloudFormation::CustomResource",
    "Properties": {
        "loglevel": "debug",
        "ServiceToken": { "Fn::GetAtt": [ "MyLambdaFunction", "Arn" ] }
    }
}
```
