"""
Get PrefixListID based on PrefixListName
"""

from boto3 import client
from botocore.exceptions import ClientError
import os

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


def get_pl_id(pl_name, region):
    """
    Get PrefixListID for given PrefixListName
    """

    logger.info("Get PrefixListId for PrefixListName: %s in %s" % (pl_name, region)) 
    try:
        ec2 = client('ec2', region_name=region)
        response = ec2.describe_prefix_lists(
            Filters=[
                {
                    'Name': 'prefix-list-name',
                    'Values': [
                        pl_name
                    ]
                }
            ]
        )
    except ClientError as e:
        raise Exception("Error retrieving prefix list: %s" % e)
    prefix_list_id = response['PrefixLists'][0]['PrefixListId']
    logger.info("Got %s" % prefix_list_id)
    resp = {'PrefixListID': prefix_list_id}
    return resp


def create(event, context):
    """
    Place your code to handle Create events here.
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    region = os.environ['AWS_REGION']
    prefix_list_name = event['ResourceProperties']['PrefixListName']
    physical_resource_id = 'RetrievedPrefixList'
    response_data = get_pl_id(prefix_list_name, region)
    return physical_resource_id, response_data


def update(event, context):
    """
    Place your code to handle Update events here
    
    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    region = os.environ['AWS_REGION']
    prefix_list_name = event['ResourceProperties']['PrefixListName']
    physical_resource_id = 'RetrievedPrefixList'
    response_data = get_pl_id(prefix_list_name, region)
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
