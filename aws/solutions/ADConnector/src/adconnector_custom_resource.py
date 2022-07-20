"""Create and configure an ADConnector Directory.

Copyright 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
http://aws.amazon.com/agreement or other written agreement between Customer and either
Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
"""
import json
import logging
import os

import boto3
from crhelper import CfnResource

# Setup Default Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.ERROR))

# Initialize the helper
helper = CfnResource(json_logging=False, log_level="DEBUG", boto_level="CRITICAL")

try:
    ds_client = boto3.client("ds")
    secretsmanager_client = boto3.client("secretsmanager")
except Exception as error:
    helper.init_failure(error)


def get_adconnector_parameters(params: dict) -> dict:
    """Creates a parameters dictionary for the ds:connect_directory API call to create AD Connector.

    Args:
        params: event resource properties

    Returns:
        ADConnector Parameters
    """
    # Get AD Domain Join Credentials from Secrets Manager
    response = secretsmanager_client.get_secret_value(SecretId=params["DOMAIN_JOIN_SECRET_ID"])
    secret = json.loads(response["SecretString"])
    # Create DNS Servers List

    return {
        "Name": params["DOMAIN_DNS_NAME"],
        "ShortName": params["DOMAIN_NETBIOS_NAME"],
        "Password": secret.get("password"),
        "Description": params["ADCONNECTOR_DESCRIPTION"],
        "Size": params["ADCONNECTOR_SIZE"],
        "ConnectSettings": {
            "VpcId": params["ADCONNECTOR_VPCID"],
            "SubnetIds": [params["ADCONNECTOR_SUBNET_ID1"], params["ADCONNECTOR_SUBNET_ID2"]],
            "CustomerDnsIps": params["DOMAIN_DNS_SERVERS"].split(", "),
            "CustomerUserName": secret.get("username"),
        },
    }


@helper.create
def create(event, context) -> str:
    """Create Event from AWS CloudFormation.

    Args:
        event: event data
        context: runtime information

    Returns:
        ADConnectorDirectoryResourceID
    """
    logger.info("Create Event")
    logger.info(f"REQUEST RECEIVED: {json.dumps(event, default=str)}")
    adconnector_params = get_adconnector_parameters(event["ResourceProperties"])
    response = ds_client.connect_directory(**adconnector_params)
    logger.info(f"connect_directory_response = {json.dumps(response, default=str)}")
    helper.PhysicalResourceId = response["DirectoryId"]
    return helper.PhysicalResourceId


@helper.update
def update(event, context):
    """Update Event from AWS CloudFormation.

    Args:
        event: event data
        context: runtime information

    """
    logger.info("Update Event")
    logger.info(f"REQUEST RECEIVED: {json.dumps(event, default=str)}")


@helper.delete
def delete(event, context):
    """Delete Event from AWS CloudFormation. Deletes the ADConnector Directory.

    Args:
        event: event data
        context: runtime information

    """
    logger.info("Delete Event")
    logger.info(f"REQUEST RECEIVED: {json.dumps(event, default=str)}")
    helper.PhysicalResourceId = event.get("PhysicalResourceId")
    directory_id = helper.PhysicalResourceId
    logger.info(f"directory_id = {directory_id}")
    response = ds_client.delete_directory(DirectoryId=directory_id)
    logger.info(f"delete_directory_response = {json.dumps(response, default=str)}")


def lambda_handler(event, context):
    """Lambda Handler.

    Args:
        event: event data
        context: runtime information
    """
    logger.info("....Lambda Handler Started....")
    helper(event, context)
