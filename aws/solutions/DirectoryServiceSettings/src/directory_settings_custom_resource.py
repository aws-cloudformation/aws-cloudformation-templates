"""Configure Directory Settings (Directory Monitoring, Directory Alias, & Directory SSO).

Copyright 2021 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
This AWS Content is provided subject to the terms of the AWS Customer Agreement available at
http://aws.amazon.com/agreement or other written agreement between Customer and either
Amazon Web Services, Inc. or Amazon Web Services EMEA SARL or both.
"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

import boto3

# import botocore
from crhelper import CfnResource

# Setup Default Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(os.environ.get("LOG_LEVEL", logging.ERROR))

# Initialize the helper
helper = CfnResource(json_logging=False, log_level="DEBUG", boto_level="CRITICAL")

try:
    ds_client = boto3.client("ds")
except Exception as error:
    helper.init_failure(error)

if TYPE_CHECKING:
    from typing import List, Tuple, Union


def get_directory_alias_and_sso_enabled_status(directory_id: str) -> Union[Tuple[str, bool], None]:
    """Get the existing directory alias, if configured, and get the current directory SSO state.

    Args:
        directory_id: Directory ID

    Returns:
        existing directory alias and current directory SSO state
    """
    paginator = ds_client.get_paginator("describe_directories")
    page_iterator = paginator.paginate(DirectoryIds=[directory_id])
    for page in page_iterator:
        for directory in page["DirectoryDescriptions"]:
            return directory["Alias"], directory["SsoEnabled"]
    return None


def get_registered_topics(directory_id: str) -> List[str]:
    """Get existing list of SNS topics configured for directory monitoring.

    Args:
        directory_id: Directory ID

    Returns:
        Existing SNS Topics configured for directory monitoring
    """
    response = ds_client.describe_event_topics(DirectoryId=directory_id)
    registered_topics: list = []
    for registered_topic in response["EventTopics"]:
        registered_topics.append(registered_topic["TopicName"])
    return registered_topics


def register_directory_monitoring_topic(directory_id: str, topic: str) -> None:
    """Register SNS topic for directory monitoring.

    Args:
        directory_id: Directory ID
        topic: SNS topic name
    """
    registered_topics: list = get_registered_topics(directory_id)
    if topic not in registered_topics:
        response = ds_client.register_event_topic(DirectoryId=directory_id, TopicName=topic)
        logger.info(f"Directory Monitoring registered with Topic '{topic}'")
        logger.debug(f"register_topic_response = {json.dumps(response, default=str)}")


def deregister_directory_monitoring_topic(directory_id: str, topic: str) -> None:
    """Deregister SNS topic for directory monitoring.

    Args:
        directory_id: Directory ID
        topic: SNS topic name
    """
    registered_topics: list = get_registered_topics(directory_id)
    for registered_topic in registered_topics:
        response = ds_client.deregister_event_topic(DirectoryId=directory_id, TopicName=registered_topic)
        logger.info(f"Directory Monitoring deregistered with Topic '{registered_topic}'")
        logger.debug(f"deregister_topic_response = {json.dumps(response, default=str)}")


def create_directory_alias(directory_id: str, alias: str, existing_alias: str) -> str:
    """Create and assigns an alias to the directory.

    Args:
        directory_id: Directory ID
        alias: Requested directory alias
        existing_alias: Existing directory alias

    Raises:
        ValueError: Directory already has a different alias. Use existing alias for the 'DirectoryAlias' CloudFormation parameter.

    Returns:
        The directory alias, either the new alias created, or the existing alias that was already configured.
    """
    if alias == existing_alias:
        return alias
    elif not existing_alias:
        response = ds_client.create_alias(DirectoryId=directory_id, Alias=alias)
        logger.info("Directory alias created")
        logger.debug(f"create_alias_response = {json.dumps(response, default=str)}")
        return alias
    else:
        error_message = f"Directory already has a different alias.  Use '{existing_alias}' for the 'DirectoryAlias' CloudFormation parameter."
        raise ValueError(error_message)


def enable_directory_sso(directory_id: str, existing_sso_enabled: bool) -> None:
    """Enables single sign-on for the directory.

    Args:
        directory_id: Directory ID
        existing_sso_enabled: Status of single sing-on for the directory
    """
    if not existing_sso_enabled:
        response = ds_client.enable_sso(DirectoryId=directory_id)
        logger.info("Directory enabled for SSO")
        logger.debug(f"enable_sso_response = {json.dumps(response, default=str)}")
    else:
        logger.info("Directory was already enabled for SSO")


def disable_directory_sso(directory_id: str, existing_sso_enabled: bool) -> None:
    """Disables single sign-on for the directory.

    Args:
        directory_id: Directory ID
        existing_sso_enabled: Status of single sing-on for the directory
    """
    if existing_sso_enabled:
        response = ds_client.disable_sso(DirectoryId=directory_id)
        logger.info("Directory disabled for SSO")
        logger.debug(f"disable_sso_response = {json.dumps(response, default=str)}")
    else:
        logger.info("Directory was already disabled for SSO")


@helper.create
@helper.update
def create_and_update(event, context):
    """Create/Update Event from AWS CloudFormation.

    Args:
        event: event data
        context: runtime information

    """
    logger.info(f"{event['RequestType']} Event")
    logger.info(f"REQUEST RECEIVED: {json.dumps(event, default=str)}")
    directory_id: str = event["ResourceProperties"]["DirectoryId"]
    create_alias: str = event["ResourceProperties"]["CreateDirectoryAlias"]
    enable_sso: str = event["ResourceProperties"]["EnableDirectorySSO"]
    alias: str = event["ResourceProperties"]["DirectoryAlias"]
    topic: str = event["ResourceProperties"]["DirectoryMonitoringTopicName"]
    # Directory Monitoring
    register_directory_monitoring_topic(directory_id, topic)
    # Existing Alias & SSO Status
    existing_alias, existing_sso_status = get_directory_alias_and_sso_enabled_status(directory_id)
    logger.info(f"existing_alias={existing_alias} --- existing_sso_status={existing_sso_status}")
    # Directory Alias
    if create_alias == "Yes":
        create_directory_alias(directory_id, alias, existing_alias)
        helper.Data.update({"AliasUrl": f"https://{alias}.awsapps.com"})
    else:
        helper.Data.update({"AliasUrl": ""})
    # Directory SSO
    if enable_sso == "Yes":
        enable_directory_sso(directory_id, existing_sso_status)
    else:
        disable_directory_sso(directory_id, existing_sso_status)


@helper.delete
def delete(event, context):
    """Delete Event from AWS CloudFormation. Deletes the ADConnector Directory.

    Args:
        event: event data
        context: runtime information

    """
    logger.info("Delete Event")
    logger.info(f"REQUEST RECEIVED: {json.dumps(event, default=str)}")
    directory_id: str = event["ResourceProperties"]["DirectoryId"]
    topic: str = event["ResourceProperties"]["DirectoryMonitoringTopicName"]
    # Directory Monitoring
    deregister_directory_monitoring_topic(directory_id, topic)
    # Existing Alias & SSO Status
    existing_alias, existing_sso_status = get_directory_alias_and_sso_enabled_status(directory_id)
    # Directory Alias
    if existing_alias:
        logger.info("Directory Alias by design cannot be modified. Skipped!")
    # Directory SSO
    disable_directory_sso(directory_id, existing_sso_status)


def lambda_handler(event, context):
    """Lambda Handler.

    Args:
        event: event data
        context: runtime information
    """
    logger.info("....Lambda Handler Started....")
    helper(event, context)
