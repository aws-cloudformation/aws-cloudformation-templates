###################################################################################################
#### Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
####
#### Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
#### except in compliance with the License. A copy of the License is located at
####
####     http://aws.amazon.com/apache2.0/
####
#### or in the "license" file accompanying this file. This file is distributed on an "AS IS"
#### BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#### License for the specific language governing permissions and limitations under the License.
###################################################################################################

from __future__ import print_function
import traceback
import logging
import threading
from time import sleep
from datetime import datetime
from botocore.vendored import requests
import json


def log_config(event, loglevel=None, botolevel=None):
    if 'ResourceProperties' in event.keys():
        if 'loglevel' in event['ResourceProperties'] and not loglevel:
            loglevel = event['ResourceProperties']['loglevel']
        if 'botolevel' in event['ResourceProperties'] and not botolevel:
            loglevel = event['ResourceProperties']['botolevel']
    if not loglevel:
        loglevel = 'warning'
    if not botolevel:
        botolevel = 'error'
    # Set log verbosity levels
    loglevel = getattr(logging, loglevel.upper(), 20)
    botolevel = getattr(logging, botolevel.upper(), 40)
    mainlogger = logging.getLogger()
    mainlogger.setLevel(loglevel)
    logging.getLogger('boto3').setLevel(botolevel)
    logging.getLogger('botocore').setLevel(botolevel)
    # Set log message format
    logfmt = '[%(requestid)s][%(asctime)s][%(levelname)s] %(message)s \n'
    mainlogger.handlers[0].setFormatter(logging.Formatter(logfmt))
    return logging.LoggerAdapter(mainlogger, {'requestid': event['RequestId']})


def send(event, context, responseStatus, responseData, physicalResourceId,
         logger, reason=None):

    responseUrl = event['ResponseURL']
    logger.debug("CFN response URL: " + responseUrl)

    responseBody = {}
    responseBody['Status'] = responseStatus
    msg = 'See CloudWatch Log Stream: ' + context.log_stream_name
    if not reason:
        responseBody['Reason'] = msg
    else:
        responseBody['Reason'] = str(reason)[0:255] + ' (' + msg + ')'
    responseBody['PhysicalResourceId'] = physicalResourceId or 'NONE'
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    if responseData and responseData != {} and responseData != [] and isinstance(responseData, dict):
        responseBody['Data'] = responseData

    json_responseBody = json.dumps(responseBody)

    logger.debug("Response body:\n" + json_responseBody)

    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }

    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        logger.info("CloudFormation returned status code: " + response.reason)
    except Exception as e:
        logger.error("send(..) failed executing requests.put(..): " + str(e))
        raise


# Function that executes just before lambda excecution times out
def timeout(event, context, logger):
    logger.error("Execution is about to time out, sending failure message")
    send(event, context, "FAILED", None, None, reason="Execution timed out",
         logger=logger)


# Handler function
def cfn_handler(event, context, create, update, delete, logger, init_failed):

    logger.info("Lambda RequestId: %s CloudFormation RequestId: %s" %
                (context.aws_request_id, event['RequestId']))

    # Define an object to place any response information you would like to send
    # back to CloudFormation (these keys can then be used by Fn::GetAttr)
    responseData = {}

    # Define a physicalId for the resource, if the event is an update and the
    # returned phyiscalid changes, cloudformation will then issue a delete
    # against the old id
    physicalResourceId = None

    logger.debug("EVENT: " + str(event))
    # handle init failures
    if init_failed:
        send(event, context, "FAILED", responseData, physicalResourceId,
             init_failed, logger=logger)
        raise

    # Setup timer to catch timeouts
    t = threading.Timer((context.get_remaining_time_in_millis()/1000.00)-0.5,
                        timeout, args=[event, context, logger])
    t.start()

    try:
        # Execute custom resource handlers
        logger.info("Received a %s Request" % event['RequestType'])
        if event['RequestType'] == 'Create':
            physicalResourceId, responseData = create(event, context)
        elif event['RequestType'] == 'Update':
            physicalResourceId, responseData = update(event, context)
        elif event['RequestType'] == 'Delete':
            delete(event, context)

        # Send response back to CloudFormation
        logger.info("Completed successfully, sending response to cfn")
        send(event, context, "SUCCESS", responseData, physicalResourceId,
             logger=logger)

    # Catch any exceptions, log the stacktrace, send a failure back to
    # CloudFormation and then raise an exception
    except Exception as e:
        logger.error(e, exc_info=True)
        send(event, context, "FAILED", responseData, physicalResourceId,
             reason=e, logger=logger)
        raise
