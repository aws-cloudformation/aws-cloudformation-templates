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
from pathlib import Path
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
    with validation. Validates that all required variables are set before creating
    the object to provide better error messages and fail-fast behavior.

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
            (exits with code 1)

    Example:
        # Set environment variables first
        # export CDK_DEFAULT_ACCOUNT=account_id_1
        # export CDK_DEFAULT_REGION=us-east-1
        # export NOTIFICATION_EMAIL=admin@example.com
        # export DASHBOARD_NAME=MyDashboard
        # export ALARM_PREFIX=MyAlarms
        # export TARGET_ACCOUNTS=account_id_2,account_id_3

        env_config = get_environment_config()
        print(f"Account: {env_config.account}")
    """
    # Define required environment variables with their descriptions
    required_env_vars = {
        "CDK_DEFAULT_ACCOUNT": "AWS account ID for deployment",
        "CDK_DEFAULT_REGION": "AWS region for deployment",
        "NOTIFICATION_EMAIL": "Email address for alarm notifications",
        "DASHBOARD_NAME": "Name for CloudWatch dashboard",
        "ALARM_PREFIX": "Prefix for alarm names",
        "TARGET_ACCOUNTS": "Comma-separated list of target account IDs"
    }

    # Collect environment variable values and validate them
    env_values = {}
    missing_vars = []

    for var_name, description in required_env_vars.items():
        value = os.getenv(var_name)

        if value is None:
            missing_vars.append((var_name, description))
        else:
            # Store the value (EnvironmentConfig will do additional validation)
            env_values[var_name] = value

    # If any variables are missing, provide detailed error message and exit
    if missing_vars:
        print("❌ Required environment variables are not set.")
        print("Please set the following environment variables before running:")
        print()

        for var_name, description in missing_vars:
            print(f"  export {var_name}=<value>  # {description}")

        print()
        print("Example configuration:")
        print("  export CDK_DEFAULT_ACCOUNT=account_id_1")
        print("  export CDK_DEFAULT_REGION=us-east-1")
        print("  export NOTIFICATION_EMAIL=admin@example.com")
        print("  export DASHBOARD_NAME=MyDashboard")
        print("  export ALARM_PREFIX=MyAlarms")
        print("  export TARGET_ACCOUNTS=account_id_2,account_id_3")

        sys.exit(1)

    # Create EnvironmentConfig with validated non-None values
    # EnvironmentConfig will perform additional validation (empty strings, whitespace, etc.)
    return EnvironmentConfig(
        account=env_values["CDK_DEFAULT_ACCOUNT"],
        region=env_values["CDK_DEFAULT_REGION"],
        notification_email=env_values["NOTIFICATION_EMAIL"],
        dashboard_name=env_values["DASHBOARD_NAME"],
        alarm_prefix=env_values["ALARM_PREFIX"],
        target_accounts=env_values["TARGET_ACCOUNTS"]
    )

def _validate_config_path(config_file_path: str) -> str:
    """
    Validate and sanitize the configuration file path to prevent path traversal attacks.
    
    Args:
        config_file_path (str): The input file path to validate
        
    Returns:
        str: The validated and resolved file path
        
    Raises:
        ValueError: If the path contains path traversal attempts or is outside allowed directory
    """
    # Convert to Path object for safer handling
    path = Path(config_file_path)

    # Get the current working directory as the base allowed directory
    base_dir = Path.cwd()

    # Additional check: ensure the filename doesn't contain suspicious characters
    if '..' in str(path) or path.is_absolute():
        raise ValueError("Path traversal attempt detected")

    try:
        # Resolve the path to get absolute path and eliminate any .. components
        resolved_path = path.resolve()

        # Check if the resolved path is within the current working directory or its subdirectories
        resolved_path.relative_to(base_dir)

        # Only allow .json files for additional security
        if resolved_path.suffix.lower() != '.json':
            raise ValueError("Only JSON configuration files are allowed")

        return str(resolved_path)

    except ValueError as e:
        if "is not in the subpath of" in str(e):
            raise ValueError(f"Path traversal attempt detected: {config_file_path} "
                           f"is outside allowed directory") from e
        raise

def load_config_file(config_file_path: str) -> Dict[str, Any]:
    """
    Load and parse JSON configuration file with error handling and path validation.

    Reads a JSON configuration file and parses it into a dictionary.
    Provides user-friendly error messages for common issues like missing
    files or invalid JSON syntax. Includes security validation to prevent
    path traversal attacks.

    Args:
        config_file_path (str): Path to the JSON configuration file (relative to current directory)

    Returns:
        Dict[str, Any]: Parsed configuration data as a dictionary

    Raises:
        SystemExit: If the configuration file is not found (exits with code 1)
        ValueError: If the path contains path traversal attempts
        json.JSONDecodeError: If the JSON file has invalid syntax

    Example:
        config_data = load_config_file("config.json")
        stackset_config = config_data["stackset"]
        monitoring_config = config_data["monitoring"]
    """
    try:
        # Validate the path to prevent path traversal attacks
        safe_path = _validate_config_path(config_file_path)
        with open(safe_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file {config_file_path}: {e}")
        raise
    except ValueError as e:
        print(f"❌ Security error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Config file {config_file_path} not found!")
        print(
            "Please create the config file with the required configuration. "
            "Check the README.md for more detail"
        )
        sys.exit(1)

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
        SystemExit: If required environment variables are missing (exits with code 1)
        ValueError: If any pipeline configuration parameter is invalid
            (via PipelineConfig validation)

    Required Environment Variables:
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

    # Get and validate required environment variables
    connection_arn = os.getenv("CODE_CONNECTION_ARN")
    repository_name = os.getenv("REPOSITORY")

    # Validate that required environment variables are set
    missing_vars = []
    if connection_arn is None:
        missing_vars.append("CODE_CONNECTION_ARN")
    if repository_name is None:
        missing_vars.append("REPOSITORY")

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"  export {var}=<value>")
        sys.exit(1)

    # Get the pipelines configuration
    pipelines_config = []
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
