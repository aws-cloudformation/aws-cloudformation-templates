"""
Utility functions for AWS CloudFormation StackSets blog example.

This module provides utility functions for loading configuration files,
parsing environment variables, and creating configuration objects for
the StackSets deployment. Handles error cases and provides user-friendly
error messages for configuration issues.

Functions:
    get_environment_config: Load and validate environment variables
    load_config_file: Load and parse JSON configuration file
    get_stackset_config: Create StackSetConfig from file and environment
    get_monitoring_config: Create MonitoringConfig from file and environment

Example:
    from stacksets_blog.utils import get_environment_config, get_stackset_config

    # Load environment configuration
    env_config = get_environment_config()

    # Load StackSet configuration
    stackset_config = get_stackset_config("config.json", env_config)
"""

import sys
import os
import json
from typing import (
    Dict,
    Any,
    Sequence
)
from .config import (
    StackSetConfig,
    MonitoringConfig,
    EnvironmentConfig,
    PipelineConfig
)

def get_environment_config() -> EnvironmentConfig:
    """
    Load and validate environment configuration from environment variables.

    Retrieves required environment variables and creates an EnvironmentConfig object
    with validation. The EnvironmentConfig constructor will automatically validate
    that all required variables are set and exit the application if any are missing.

    Required Environment Variables:
        CDK_DEFAULT_ACCOUNT: AWS account ID for deployment
        CDK_DEFAULT_REGION: AWS region for deployment
        NOTIFICATION_EMAIL: Email address for alarm notifications
        DASHBOARD_NAME: Name for CloudWatch dashboard
        ALARM_PREFIX: Prefix for alarm names
        TARGET_ACCOUNTS: Comma-separated list of target account IDs

    Returns:
        EnvironmentConfig: Validated environment configuration object

    Raises:
        SystemExit: If any required environment variable is missing
            (via EnvironmentConfig validation)

    Example:
        # Set environment variables first
        # export CDK_DEFAULT_ACCOUNT=123456789012
        # export CDK_DEFAULT_REGION=us-east-1
        # export NOTIFICATION_EMAIL=admin@example.com
        # export DASHBOARD_NAME=MyDashboard
        # export ALARM_PREFIX=MyAlarms
        # export TARGET_ACCOUNTS=123456789013,123456789014

        env_config = get_environment_config()
        print(f"Account: {env_config.account}")
    """
    return EnvironmentConfig(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
        notification_email=os.getenv("NOTIFICATION_EMAIL"),
        dashboard_name=os.getenv("DASHBOARD_NAME"),
        alarm_prefix=os.getenv("ALARM_PREFIX"),
        target_accounts=os.getenv("TARGET_ACCOUNTS")
    )

def load_config_file(config_file_path: str) -> Dict[str, Any]:
    """
    Load and parse JSON configuration file with error handling.

    Reads a JSON configuration file and parses it into a dictionary.
    Provides user-friendly error messages for common issues like missing
    files or invalid JSON syntax.

    Args:
        config_file_path (str): Path to the JSON configuration file

    Returns:
        Dict[str, Any]: Parsed configuration data as a dictionary

    Raises:
        SystemExit: If the configuration file is not found (exits with code 1)
        json.JSONDecodeError: If the JSON file has invalid syntax

    Example:
        config_data = load_config_file("config.json")
        stackset_config = config_data["stackset"]
        monitoring_config = config_data["monitoring"]
    """
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file {config_file_path} not found!")
        print(
            "Please create the config file with the required configuration. "
            "Check the README.md for more detail"
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file {config_file_path}: {e}")
        raise

def get_stackset_config(config_file_path: str, env_config: EnvironmentConfig) -> StackSetConfig:
    """
    Create StackSetConfig from configuration file and environment variables.

    Loads the StackSet configuration from a JSON file and merges it with
    environment variables to create a complete StackSetConfig object.
    Handles missing configuration sections with descriptive error messages.

    Args:
        config_file_path (str): Path to the JSON configuration file
        env_config (EnvironmentConfig): Environment configuration object

    Returns:
        StackSetConfig: Complete StackSet configuration object with validation

    Raises:
        KeyError: If the 'stackset' section is missing from the configuration file
        ValueError: If any StackSet configuration parameter is invalid
            (via StackSetConfig validation)

    Configuration File Structure:
        The JSON file must contain a 'stackset' section with:
        - stack_set_name: Name of the StackSet
        - target_regions: List of AWS regions
        - instance_stack_name: Name of the stack template
        - target_accounts: List of target account IDs (from TARGET_ACCOUNTS environment variable)
        - max_concurrent_percentage: Concurrent deployment percentage
        - failure_tolerance_percentage: Failure tolerance percentage
        - region_concurrency_type: "PARALLEL" or "SEQUENTIAL"

    Example:
        env_config = get_environment_config()
        stackset_config = get_stackset_config("config.json", env_config)
        print(f"StackSet: {stackset_config.stack_set_name}")
    """

    # Load configuration from file
    full_config = load_config_file(config_file_path)

    # Get stackset section
    try:
        context_config = full_config["stackset"]
    except KeyError as e:
        print(f"❌ Missing 'stackset' section in config file {config_file_path}: {e}")
        raise

    # Merge parameters from environment variables
    parameters = {
        "NotificationEmail": env_config.notification_email,
        "DashboardName": env_config.dashboard_name,
        "AlarmPrefix": env_config.alarm_prefix
    }

    # Parse target accounts from environment variable
    # (comma-separated string to list)
    target_accounts = [
        account.strip()
        for account in env_config.target_accounts.split(",")
        if account.strip()
    ]

    return StackSetConfig(
        stack_set_name=context_config["stack_set_name"],
        target_regions=context_config["target_regions"],
        instance_stack_name=context_config["instance_stack_name"],
        target_accounts=target_accounts,
        parameters=parameters,
        max_concurrent_percentage=context_config["max_concurrent_percentage"],
        failure_tolerance_percentage=context_config["failure_tolerance_percentage"],
        region_concurrency_type=context_config["region_concurrency_type"]
    )

def get_monitoring_config(config_file_path: str, env_config: EnvironmentConfig) -> MonitoringConfig:
    """
    Create MonitoringConfig from configuration file and environment variables.

    Loads the monitoring configuration from a JSON file and merges it with
    environment variables to create a complete MonitoringConfig object.
    Handles missing configuration sections with descriptive error messages.

    Args:
        config_file_path (str): Path to the JSON configuration file
        env_config (EnvironmentConfig): Environment configuration object

    Returns:
        MonitoringConfig: Complete monitoring configuration object with
            validation

    Raises:
        KeyError: If the 'monitoring' section is missing from the configuration file
        ValueError: If any monitoring configuration parameter is invalid
            (via MonitoringConfig validation)

    Configuration File Structure:
        The JSON file must contain a 'monitoring' section with:
        - alarm_thresholds: Dictionary of metric names to threshold values
          Example: {"CPUUtilization": 80.0, "MemoryUtilization": 85.0}

    Environment Variables Used:
        - DASHBOARD_NAME: Name for the CloudWatch dashboard
        - NOTIFICATION_EMAIL: Email address for alarm notifications
        - ALARM_PREFIX: Prefix for alarm names

    Example:
        env_config = get_environment_config()
        monitoring_config = get_monitoring_config("config.json", env_config)
        print(f"Dashboard: {monitoring_config.dashboard_name}")
        print(f"Thresholds: {monitoring_config.alarm_thresholds}")
    """

    # Load configuration from file
    full_config = load_config_file(config_file_path)

    # Get monitoring section
    try:
        context_config = full_config["monitoring"]
    except KeyError as e:
        print(f"❌ Missing 'monitoring' section in config file {config_file_path}: {e}")
        raise

    return MonitoringConfig(
        dashboard_name=env_config.dashboard_name,
        notification_email=env_config.notification_email,
        alarm_thresholds=context_config["alarm_thresholds"],
        alarm_prefix=env_config.alarm_prefix
    )

def get_pipelines_config(config_file_path: str) -> Sequence[PipelineConfig]:
    """
    Create PipelineConfig objects from configuration file and environment variables.

    Loads the pipeline configurations from a JSON file and merges them with
    environment variables to create complete PipelineConfig objects for each
    pipeline defined in the configuration.

    Args:
        config_file_path (str): Path to the JSON configuration file

    Returns:
        Sequence[PipelineConfig]: List of complete pipeline configuration objects

    Raises:
        KeyError: If the 'pipelines' section is missing from the configuration file
        ValueError: If any pipeline configuration parameter is invalid
            (via PipelineConfig validation)

    Environment Variables Used:
        - CODE_CONNECTION_ARN: ARN of the CodeConnections connection
        - REPOSITORY: Repository name in "owner/repo" format

    Configuration File Structure:
        The JSON file must contain a 'pipelines' section with a list of pipeline configs:
        {
            "pipelines": [
                {
                    "branch_name": "main",
                    "environment": "production"
                },
                {
                    "branch_name": "develop", 
                    "environment": "staging"
                }
            ]
        }

    Example:
        pipelines = get_pipelines_config("config.json")
        for pipeline in pipelines:
            print(f"Pipeline: {pipeline.get_pipeline_name()}")
    """
    # Load configuration from file
    full_config = load_config_file(config_file_path)

    # Get pipelines section
    try:
        config = full_config["pipelines"]
    except KeyError as e:
        print(f"❌ Missing 'pipelines' section in config file {config_file_path}: {e}")
        raise

    # Get the pipelines configuration
    pipelines_config = []
    connection_arn = os.getenv("CODE_CONNECTION_ARN")
    repository_name = os.getenv("REPOSITORY")
    for pipeline_config in config:
        pipelines_config.append(
            PipelineConfig(
                connection_arn=connection_arn,
                repository_name=repository_name,
                branch_name=pipeline_config["branch_name"],
                environment=pipeline_config["environment"],
            )
        )
    return pipelines_config
