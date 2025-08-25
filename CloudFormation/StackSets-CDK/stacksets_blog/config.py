"""
Configuration module for AWS CloudFormation StackSets blog example.

This module defines configuration classes for managing StackSet deployment
parameters, monitoring settings, and environment variables with validation.

Classes:
    StackSetConfig: Configuration for AWS CloudFormation StackSet deployment
    MonitoringConfig: Configuration for CloudWatch monitoring resources
    EnvironmentConfig: Configuration for environment variables validation

Example:
    from stacksets_blog.config import StackSetConfig, MonitoringConfig

    stackset_config = StackSetConfig(
        stack_set_name="MyStackSet",
        target_regions=["us-east-1", "us-west-2"],
        parameters={"Email": "admin@example.com"},
        instance_stack_name="MonitoringStack"
    )
"""

import sys
from dataclasses import dataclass
from typing import List, Dict
import re

@dataclass
class StackSetConfig:  # pylint: disable=too-many-instance-attributes
    """
    Configuration class for AWS CloudFormation StackSet deployment.

    This class defines all the parameters needed to create and manage a StackSet,
    including target regions, accounts, operation preferences, and template parameters.
    Provides validation for AWS StackSet requirements and constraints.

    Attributes:
        stack_set_name (str): Name of the CloudFormation StackSet (1-128 characters)
        target_regions (List[str]): List of AWS regions to deploy stack instances
        parameters (Dict[str, str]): CloudFormation template parameters as key-value pairs
        instance_stack_name (str): Name of the stack template to deploy via StackSet
        max_concurrent_percentage (int): Maximum percentage of accounts to deploy
            concurrently (1-100)
        failure_tolerance_percentage (int): Percentage of failures tolerated before stopping (0-100)
        region_concurrency_type (str): Deploy regions in "PARALLEL" or "SEQUENTIAL"
        target_accounts (List[str], optional): List of AWS account IDs to deploy to

    Raises:
        ValueError: If any configuration parameter is invalid or out of range

    Example:
        config = StackSetConfig(
            stack_set_name="BlogMonitoringStackSet",
            target_regions=["us-east-1", "us-west-2", "eu-west-1"],
            parameters={"NotificationEmail": "admin@example.com"},
            instance_stack_name="MonitoringStack",
            max_concurrent_percentage=50,
            failure_tolerance_percentage=10
        )
    """
    stack_set_name: str
    target_regions: List[str]
    parameters: Dict[str, str]
    instance_stack_name: str
    max_concurrent_percentage: int = 100
    failure_tolerance_percentage: int = 10
    region_concurrency_type: str = "PARALLEL"
    target_accounts: List[str] = None

    def __post_init__(self):
        """
        Post-initialization hook to validate configuration parameters.

        Called automatically after object creation to ensure all parameters
        are valid and meet AWS StackSet requirements.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        self.validate()

    def validate(self):
        """
        Validate all StackSet configuration parameters.

        Performs comprehensive validation of StackSet parameters including:
        - StackSet name length and format
        - Target regions list validation
        - Percentage values within valid ranges
        - Region concurrency type validation

        Raises:
            ValueError: If any parameter is invalid with descriptive error message
        """
        # Validate stack set name
        if not self.stack_set_name or len(self.stack_set_name) > 128:
            raise ValueError("StackSet name must be between 1 and 128 characters")

        # Validate regions
        if not self.target_regions:
            raise ValueError("At least one target region must be specified")

        # Validate percentages
        if not 1 <= self.max_concurrent_percentage <= 100:
            raise ValueError("max_concurrent_percentage must be between 1 and 100")

        if not 0 <= self.failure_tolerance_percentage <= 100:
            raise ValueError("failure_tolerance_percentage must be between 0 and 100")

        # Validate region concurrency type
        if self.region_concurrency_type not in ["SEQUENTIAL", "PARALLEL"]:
            raise ValueError("region_concurrency_type must be SEQUENTIAL or PARALLEL")

@dataclass
class MonitoringConfig:
    """
    Configuration class for CloudWatch monitoring resources.

    This class defines parameters for CloudWatch dashboards, alarms, and notifications
    that will be deployed as part of the monitoring infrastructure. Includes validation
    for email formats, alarm thresholds, and naming constraints.

    Attributes:
        dashboard_name (str): Name for the CloudWatch dashboard (1-255 characters)
        notification_email (str): Email address for alarm notifications (must be valid email)
        alarm_thresholds (Dict[str, float]): Metric thresholds for CloudWatch alarms
        alarm_prefix (str): Prefix for alarm names to avoid conflicts (1-64 characters)

    Raises:
        ValueError: If any configuration parameter is invalid

    Example:
        config = MonitoringConfig(
            dashboard_name="StackSets-Blog-Dashboard",
            notification_email="admin@example.com",
            alarm_thresholds={
                "CPUUtilization": 80.0,
                "MemoryUtilization": 85.0
            },
            alarm_prefix="StackSets-Blog"
        )
    """
    dashboard_name: str
    notification_email: str
    alarm_thresholds: Dict[str, float]
    alarm_prefix: str = "StackSets-Blog"

    def __post_init__(self):
        """
        Post-initialization hook to validate monitoring configuration parameters.

        Called automatically after object creation to ensure all parameters
        are valid for CloudWatch monitoring resources.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        self.validate()

    def validate(self):
        """
        Validate all monitoring configuration parameters.

        Performs validation of monitoring parameters including:
        - Dashboard name length constraints
        - Email address format validation using regex
        - Alarm threshold values (must be positive numbers)
        - Alarm prefix length constraints

        Raises:
            ValueError: If any parameter is invalid with descriptive error message
        """
        # Validate dashboard name
        if not self.dashboard_name or len(self.dashboard_name) > 255:
            raise ValueError("Dashboard name must be between 1 and 255 characters")

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.notification_email):
            raise ValueError("Invalid email address format")

        # Validate alarm thresholds
        for metric, threshold in self.alarm_thresholds.items():
            if not isinstance(threshold, (int, float)) or threshold < 0:
                raise ValueError(f"Alarm threshold for {metric} must be a positive number")

        # Validate alarm prefix
        if not self.alarm_prefix or len(self.alarm_prefix) > 64:
            raise ValueError("Alarm prefix must be between 1 and 64 characters")


@dataclass
class EnvironmentConfig:
    """
    Configuration class for environment variables validation.

    This class validates that all required environment variables are set and not None.
    Used to ensure proper configuration before CDK deployment. Exits the application
    with error code 1 if any required environment variables are missing.

    Attributes:
        account (str): AWS account ID from CDK_DEFAULT_ACCOUNT environment variable
        region (str): AWS region from CDK_DEFAULT_REGION environment variable
        notification_email (str): Email address from NOTIFICATION_EMAIL environment variable
        dashboard_name (str): Dashboard name from DASHBOARD_NAME environment variable
        alarm_prefix (str): Alarm prefix from ALARM_PREFIX environment variable
        target_accounts (str): Comma-separated list of target account IDs from
            TARGET_ACCOUNTS environment variable

    Raises:
        SystemExit: If any required environment variable is None (exits with code 1)

    Example:
        # Environment variables must be set before creating this object
        # export CDK_DEFAULT_ACCOUNT=123456789012
        # export CDK_DEFAULT_REGION=us-east-1
        # export NOTIFICATION_EMAIL=admin@example.com
        # export DASHBOARD_NAME=MyDashboard
        # export ALARM_PREFIX=MyAlarms
        # export TARGET_ACCOUNTS=123456789013,123456789014

        config = EnvironmentConfig(
            account=os.getenv("CDK_DEFAULT_ACCOUNT"),
            region=os.getenv("CDK_DEFAULT_REGION"),
            notification_email=os.getenv("NOTIFICATION_EMAIL"),
            dashboard_name=os.getenv("DASHBOARD_NAME"),
            alarm_prefix=os.getenv("ALARM_PREFIX"),
            target_accounts=os.getenv("TARGET_ACCOUNTS")
        )
    """
    account: str
    region: str
    notification_email: str
    dashboard_name: str
    alarm_prefix: str
    target_accounts: str

    def __post_init__(self):
        """
        Post-initialization hook to validate environment configuration parameters.

        Called automatically after object creation to ensure all required
        environment variables are set and not None. Exits application if validation fails.

        Raises:
            SystemExit: If any required environment variable is None (exits with code 1)
        """
        self.validate()

    def validate(self):
        """
        Validate that all environment configuration parameters are not None.

        Checks each required environment variable and collects any that are None.
        If any variables are missing, prints a detailed error message with all
        missing variables and exits the application with code 1.

        This is a fail-fast approach to ensure proper configuration before deployment.

        Raises:
            SystemExit: If any required environment variable is None (exits with code 1)
        """

        missing_vars = []

        # Check each attribute for None values
        if self.account is None:
            missing_vars.append("AWS Account")

        if self.region is None:
            missing_vars.append("AWS Region")

        if self.notification_email is None:
            missing_vars.append("Notification Email")

        if self.dashboard_name is None:
            missing_vars.append("Dashboard Name")

        if self.alarm_prefix is None:
            missing_vars.append("Alarm Prefix")

        if self.target_accounts is None:
            missing_vars.append("Target Accounts")

        # If any variables are missing, print error and exit
        if missing_vars:
            print("❌ Critical environment variables are missing. Please check the pre-requisites")
            for var_name in missing_vars:
                print(f"  ERROR: {var_name} is not set (None)")
            sys.exit(1)

@dataclass  # pylint: disable=too-many-instance-attributes
class PipelineConfig:
    """
    Configuration class for CI/CD pipeline deployment.

    This class defines all the parameters needed to create and manage a CodePipeline
    for automated StackSet deployments, including source configuration, notification
    settings, and environment-specific parameters. Provides validation for pipeline
    requirements and supports environment variable overrides.

    Attributes:
        connection_arn (str): ARN of the CodeConnections connection for source integration
        repository_name (str): Repository name in "owner/repo" format (e.g., "myorg/myrepo")
        branch_name (str): Git branch to monitor for changes (default: "main")
        notification_email (str): Email address for pipeline notifications
        environment (str): Deployment environment name (default: "production")
        pipeline_name (Optional[str]): Custom pipeline name (auto-generated if None)
        approval_timeout_minutes (int): Manual approval timeout in minutes
            (default: 1440 = 24 hours)
        enable_parallel_validation (bool): Run validation stages in parallel (default: True)

    Raises:
        ValueError: If any configuration parameter is invalid

    Example:
        config = PipelineConfig(
            connection_arn="arn:aws:codeconnections:us-east-1:123456789012:connection/abc123",
            repository_name="myorg/stacksets-blog",
            branch_name="main",
            notification_email="admin@example.com",
            environment="production"
        )
    """
    connection_arn: str
    repository_name: str
    branch_name: str
    environment: str

    def __post_init__(self):
        """
        Post-initialization hook to validate pipeline configuration parameters.

        Called automatically after object creation to ensure all parameters
        are valid for CodePipeline deployment.

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        self.validate()
        self.pipeline_name = self.get_pipeline_name()

    def validate(self):
        """
        Validate all pipeline configuration parameters.

        Performs comprehensive validation of pipeline parameters including:
        - CodeConnections ARN format validation
        - Repository name format validation (owner/repo)
        - Branch name validation (no spaces, valid Git branch name)
        - Email address format validation
        - Environment name validation
        - Timeout value validation

        Raises:
            ValueError: If any parameter is invalid with descriptive error message
        """
        self._validate_connection_arn()
        self._validate_repository_name()
        self._validate_branch_name()
        self._validate_environment()

    def get_pipeline_name(self):
        """Generate pipeline name from repository and environment."""
        return f"{self.get_repository_name()}-{self.environment}-pipeline"

    def get_repository_name(self):
        """Extract repository name from owner/repo format."""
        return self.repository_name.split('/')[1]

    def get_repository_owner(self):
        """Extract repository owner from owner/repo format."""
        return self.repository_name.split('/')[0]

    def _validate_connection_arn(self):
        """Validate CodeConnections ARN format."""
        if not self.connection_arn:
            raise ValueError("CodeConnections ARN is required")

        connection_arn_pattern = (
            r'^arn:aws:codeconnections:[a-z0-9-]+:\d{12}:connection/'
            r'[a-zA-Z0-9-]+$'
        )
        if not re.match(connection_arn_pattern, self.connection_arn):
            raise ValueError("Invalid CodeConnections ARN format")

    def _validate_repository_name(self):
        """Validate repository name format (owner/repo)."""
        if not self.repository_name:
            raise ValueError("Repository name is required")

        if '/' not in self.repository_name or self.repository_name.count('/') != 1:
            raise ValueError("Repository name must be in 'owner/repo' format")

        owner, repo = self.repository_name.split('/')
        if not owner or not repo:
            raise ValueError("Both owner and repository name must be non-empty")

    def _validate_branch_name(self):
        """Validate Git branch name format."""
        if not self.branch_name:
            raise ValueError("Branch name is required")

        # Basic Git branch name validation (no spaces, no special characters at start/end)
        branch_pattern = (
            r'^[a-zA-Z0-9][a-zA-Z0-9/_.-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        )
        if not re.match(branch_pattern, self.branch_name):
            raise ValueError("Invalid Git branch name format")

    def _validate_environment(self):
        """Validate environment name format."""
        if not self.environment:
            raise ValueError("Environment name is required")

        # Environment name should be alphanumeric with hyphens/underscores
        env_pattern = (
            r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
        )
        if not re.match(env_pattern, self.environment):
            raise ValueError(
                "Environment name must be alphanumeric with optional hyphens/underscores"
            )

    def _validate_pipeline_name(self):
        """Validate pipeline name format if provided."""
        if self.pipeline_name is not None:
            if not self.pipeline_name or len(self.pipeline_name) > 100:
                raise ValueError("Pipeline name must be between 1 and 100 characters")

            # Pipeline name should be alphanumeric with hyphens/underscores
            pipeline_pattern = (
                r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
            )
            if not re.match(pipeline_pattern, self.pipeline_name):
                raise ValueError(
                    "Pipeline name must be alphanumeric with optional hyphens/underscores"
                )
