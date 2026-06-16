"""
Unit tests for configuration classes.

This module contains comprehensive unit tests for the configuration classes
including StackSetConfig, MonitoringConfig, and EnvironmentConfig.
"""

from unittest.mock import patch
import re

import pytest
from stacksets_blog.config import (
    StackSetConfig, MonitoringConfig, EnvironmentConfig, PipelineConfig
)
from tests.conftest import (
    SIMPLE_STACKSET_CONFIG, SINGLE_ACCOUNT_ENV_CONFIG, ENVIRONMENT_CONFIG_PARAMS,
    TEST_EMAIL, TEST_DASHBOARD, TEST_ALARM_PREFIX, SIMPLE_ALARM_THRESHOLDS
)


class TestStackSetConfig:
    """Test suite for StackSetConfig class."""

    def test_stackset_config_creation_with_valid_data(self):
        """Test StackSetConfig creation with valid data."""
        # Arrange & Act
        config = StackSetConfig(
            stack_set_name="TestStackSet",
            target_regions=["us-east-1", "us-west-2"],
            target_accounts=["123456789012", "123456789013"],
            instance_stack_name="TestStack",
            parameters={"Email": "test@example.com"}
        )

        # Assert
        assert config.stack_set_name == "TestStackSet"
        assert config.target_regions == ["us-east-1", "us-west-2"]
        assert config.target_accounts == ["123456789012", "123456789013"]
        assert config.instance_stack_name == "TestStack"
        assert config.parameters == {"Email": "test@example.com"}
        assert config.max_concurrent_percentage == 100  # default
        assert config.failure_tolerance_percentage == 10  # default
        assert config.region_concurrency_type == "PARALLEL"  # default

    def test_stackset_config_with_custom_operation_preferences(self):
        """Test StackSetConfig with custom operation preferences."""
        # Arrange & Act
        config_params = SIMPLE_STACKSET_CONFIG.copy()
        config_params.update({
            "parameters": {},
            "max_concurrent_percentage": 50,
            "failure_tolerance_percentage": 25,
            "region_concurrency_type": "SEQUENTIAL"
        })
        config = StackSetConfig(**config_params)

        # Assert
        assert config.max_concurrent_percentage == 50
        assert config.failure_tolerance_percentage == 25
        assert config.region_concurrency_type == "SEQUENTIAL"

    def test_stackset_config_validation_empty_name(self):
        """Test StackSetConfig validation with empty stack set name."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="StackSet name must be between 1 and 128 characters"):
            StackSetConfig(
                stack_set_name="",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={}
            )

    def test_stackset_config_validation_long_name(self):
        """Test StackSetConfig validation with too long stack set name."""
        # Arrange
        long_name = "a" * 129  # 129 characters

        # Act & Assert
        with pytest.raises(ValueError, match="StackSet name must be between 1 and 128 characters"):
            StackSetConfig(
                stack_set_name=long_name,
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={}
            )

    def test_stackset_config_validation_empty_regions(self):
        """Test StackSetConfig validation with empty target regions."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="At least one target region must be specified"):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=[],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={}
            )

    def test_stackset_config_validation_invalid_concurrent_percentage(self):
        """Test StackSetConfig validation with invalid concurrent percentage."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="max_concurrent_percentage must be between 1 and 100"):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={},
                max_concurrent_percentage=0
            )

        with pytest.raises(ValueError, match="max_concurrent_percentage must be between 1 and 100"):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={},
                max_concurrent_percentage=101
            )

    def test_stackset_config_validation_invalid_failure_tolerance(self):
        """Test StackSetConfig validation with invalid failure tolerance percentage."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="failure_tolerance_percentage must be between 0 and 100"
        ):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={},
                failure_tolerance_percentage=-1
            )

        with pytest.raises(
            ValueError, match="failure_tolerance_percentage must be between 0 and 100"
        ):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={},
                failure_tolerance_percentage=101
            )

    def test_stackset_config_validation_invalid_concurrency_type(self):
        """Test StackSetConfig validation with invalid region concurrency type."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="region_concurrency_type must be SEQUENTIAL or PARALLEL"
        ):
            StackSetConfig(
                stack_set_name="TestStackSet",
                target_regions=["us-east-1"],
                target_accounts=["123456789012"],
                instance_stack_name="TestStack",
                parameters={},
                region_concurrency_type="INVALID"
            )


class TestMonitoringConfig:
    """Test suite for MonitoringConfig class."""

    def test_monitoring_config_creation_with_valid_data(self):
        """Test MonitoringConfig creation with valid data."""
        # Arrange & Act
        config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )

        # Assert
        assert config.dashboard_name == TEST_DASHBOARD
        assert config.notification_email == TEST_EMAIL
        assert config.alarm_thresholds == SIMPLE_ALARM_THRESHOLDS
        assert config.alarm_prefix == TEST_ALARM_PREFIX

    def test_monitoring_config_with_default_alarm_prefix(self):
        """Test MonitoringConfig with default alarm prefix."""
        # Arrange & Act
        config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS
        )

        # Assert
        assert config.alarm_prefix == "StackSets-Blog"

    def test_monitoring_config_validation_empty_dashboard_name(self):
        """Test MonitoringConfig validation with empty dashboard name."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Dashboard name must be between 1 and 255 characters"):
            MonitoringConfig(
                dashboard_name="",
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS
            )

    def test_monitoring_config_validation_long_dashboard_name(self):
        """Test MonitoringConfig validation with too long dashboard name."""
        # Arrange
        long_name = "a" * 256  # 256 characters

        # Act & Assert
        with pytest.raises(ValueError, match="Dashboard name must be between 1 and 255 characters"):
            MonitoringConfig(
                dashboard_name=long_name,
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS
            )

    def test_monitoring_config_validation_invalid_email(self):
        """Test MonitoringConfig validation with invalid email format."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid email address format"):
            MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email="invalid-email",
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS
            )

    def test_monitoring_config_validation_negative_threshold(self):
        """Test MonitoringConfig validation with negative alarm threshold."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Alarm threshold for CPUUtilization must be a positive number"
        ):
            MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds={"CPUUtilization": -10.0}
            )

    def test_monitoring_config_validation_invalid_threshold_type(self):
        """Test MonitoringConfig validation with invalid threshold type."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Alarm threshold for CPUUtilization must be a positive number"
        ):
            MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds={"CPUUtilization": "invalid"}
            )

    def test_monitoring_config_validation_long_alarm_prefix(self):
        """Test MonitoringConfig validation with too long alarm prefix."""
        # Arrange
        long_prefix = "a" * 65  # 65 characters

        # Act & Assert
        with pytest.raises(ValueError, match="Alarm prefix must be between 1 and 64 characters"):
            MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
                alarm_prefix=long_prefix
            )

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.user@domain.co.uk",
        "admin+alerts@company.org",
        "user123@test-domain.com"
    ])
    def test_monitoring_config_valid_emails(self, email):
        """Test MonitoringConfig with various valid email formats."""
        # Arrange & Act
        config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=email,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS
        )

        # Assert
        assert config.notification_email == email


class TestEnvironmentConfig:
    """Test suite for EnvironmentConfig class."""

    def test_environment_config_creation_with_valid_data(self):
        """Test EnvironmentConfig creation with valid data."""
        # Arrange & Act
        config = EnvironmentConfig(**ENVIRONMENT_CONFIG_PARAMS)

        # Assert
        assert config.account == "123456789012"
        assert config.region == "us-east-1"
        assert config.notification_email == TEST_EMAIL
        assert config.dashboard_name == TEST_DASHBOARD
        assert config.alarm_prefix == TEST_ALARM_PREFIX
        assert config.target_accounts == "123456789013,123456789014"

    @patch('sys.exit')
    def test_environment_config_validation_missing_account(self, mock_exit):
        """Test EnvironmentConfig validation with missing account."""
        # Arrange & Act
        config_params = SINGLE_ACCOUNT_ENV_CONFIG.copy()
        config_params["account"] = None
        EnvironmentConfig(**config_params)

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_environment_config_validation_missing_region(self, mock_exit):
        """Test EnvironmentConfig validation with missing region."""
        # Arrange & Act
        EnvironmentConfig(
            account="123456789012",
            region=None,
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_environment_config_validation_missing_email(self, mock_exit):
        """Test EnvironmentConfig validation with missing email."""
        # Arrange & Act
        EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email=None,
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_environment_config_validation_missing_dashboard_name(self, mock_exit):
        """Test EnvironmentConfig validation with missing dashboard name."""
        # Arrange & Act
        EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email="test@example.com",
            dashboard_name=None,
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_environment_config_validation_missing_alarm_prefix(self, mock_exit):
        """Test EnvironmentConfig validation with missing alarm prefix."""
        # Arrange & Act
        EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix=None,
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_environment_config_validation_missing_target_accounts(self, mock_exit):
        """Test EnvironmentConfig validation with missing target accounts."""
        # Arrange & Act
        config_params = SINGLE_ACCOUNT_ENV_CONFIG.copy()
        config_params["target_accounts"] = None
        EnvironmentConfig(**config_params)

        # Assert
        mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    @patch('builtins.print')
    def test_environment_config_validation_multiple_missing_vars(self, mock_print, mock_exit):
        """Test EnvironmentConfig validation with multiple missing variables."""
        # Arrange & Act
        EnvironmentConfig(
            account=None,
            region=None,
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)
        # Check that error messages were printed
        assert mock_print.call_count >= 2  # At least the main error message and missing vars

    @patch('sys.exit')
    @patch('builtins.print')
    def test_environment_config_validation_empty_strings(self, mock_print, mock_exit):
        """Test EnvironmentConfig validation with empty string values."""
        # Arrange & Act
        EnvironmentConfig(
            account="",  # Empty string
            region="us-east-1",
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)
        # Verify that empty string error message was printed
        mock_print.assert_any_call("Empty environment variables:")
        mock_print.assert_any_call("  export CDK_DEFAULT_ACCOUNT=<value>")

    @patch('sys.exit')
    @patch('builtins.print')
    def test_environment_config_validation_whitespace_only(self, mock_print, mock_exit):
        """Test EnvironmentConfig validation with whitespace-only values."""
        # Arrange & Act
        EnvironmentConfig(
            account="123456789012",
            region="   ",  # Whitespace only
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)
        # Verify that whitespace-only error message was printed
        mock_print.assert_any_call("Empty environment variables:")
        mock_print.assert_any_call("  export CDK_DEFAULT_REGION=<value>")

    @patch('sys.exit')
    @patch('builtins.print')
    def test_environment_config_validation_mixed_empty_and_none(self, mock_print, mock_exit):
        """Test EnvironmentConfig validation with mix of None and empty values."""
        # Arrange & Act
        EnvironmentConfig(
            account=None,  # None value
            region="",     # Empty string
            notification_email="  \t  ",  # Whitespace only
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)
        # Verify that both types of error messages were printed
        mock_print.assert_any_call("Missing environment variables:")
        mock_print.assert_any_call("  export CDK_DEFAULT_ACCOUNT=<value>")
        mock_print.assert_any_call("Empty environment variables:")
        mock_print.assert_any_call("  export CDK_DEFAULT_REGION=<value>")
        mock_print.assert_any_call("  export NOTIFICATION_EMAIL=<value>")

    @patch('sys.exit')
    @patch('builtins.print')
    def test_environment_config_validation_all_empty_variations(self, mock_print, mock_exit):
        """Test EnvironmentConfig validation with all types of empty variations."""
        # Arrange & Act
        EnvironmentConfig(
            account="",           # Empty string
            region="   ",         # Spaces only
            notification_email="\t\n",  # Tabs and newlines
            dashboard_name=None,  # None value
            alarm_prefix="  \t  \n  ",  # Mixed whitespace
            target_accounts=""    # Empty string
        )

        # Assert
        mock_exit.assert_called_once_with(1)
        # Verify comprehensive error reporting

        # Check for missing environment variables section
        mock_print.assert_any_call("Missing environment variables:")
        mock_print.assert_any_call("  export DASHBOARD_NAME=<value>")

        # Check for empty environment variables section
        mock_print.assert_any_call("Empty environment variables:")
        mock_print.assert_any_call("  export CDK_DEFAULT_ACCOUNT=<value>")
        mock_print.assert_any_call("  export CDK_DEFAULT_REGION=<value>")
        mock_print.assert_any_call("  export NOTIFICATION_EMAIL=<value>")
        mock_print.assert_any_call("  export ALARM_PREFIX=<value>")
        mock_print.assert_any_call("  export TARGET_ACCOUNTS=<value>")

    def test_environment_config_validation_valid_with_leading_trailing_spaces(self):
        """Test that values with leading/trailing spaces are accepted.
        
        Since they contain valid content after stripping.
        """
        # Note: The validation checks if the stripped value is not empty, so values with
        # leading/trailing spaces but valid content should be accepted

        # Arrange & Act - This should succeed because the values have valid content after stripping
        config = EnvironmentConfig(
            account="  123456789012  ",  # Valid content with spaces
            region="  us-east-1  ",
            notification_email="  test@example.com  ",
            dashboard_name="  TestDashboard  ",
            alarm_prefix="  TestAlarms  ",
            target_accounts="  123456789013  "
        )

        # Assert - Config should be created successfully
        assert config.account == "  123456789012  "
        assert config.region == "  us-east-1  "
        assert config.notification_email == "  test@example.com  "
        assert config.dashboard_name == "  TestDashboard  "
        assert config.alarm_prefix == "  TestAlarms  "
        assert config.target_accounts == "  123456789013  "

    @pytest.mark.parametrize("invalid_value,description", [
        ("", "empty string"),
        ("   ", "spaces only"),
        ("\t", "tab only"),
        ("\n", "newline only"),
        ("\t\n  ", "mixed whitespace"),
        ("  \t  \n  \r  ", "all whitespace types"),
    ])
    @patch('sys.exit')
    def test_environment_config_validation_whitespace_variations(self, mock_exit,
                                                                 invalid_value, description):
        """Test various whitespace-only values are properly rejected."""
        # Arrange & Act
        # Note: description parameter is used by pytest for test identification
        # pylint: disable=unused-argument
        EnvironmentConfig(
            account=invalid_value,
            region="us-east-1",
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
            target_accounts="123456789013"
        )

        # Assert
        mock_exit.assert_called_once_with(1)


class TestPipelineConfig:
    """Test suite for PipelineConfig class."""

    def test_pipeline_config_creation_with_valid_data(self):  # pylint: disable=duplicate-code
        """Test PipelineConfig creation with valid data."""
        # Arrange & Act
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name="main",
            environment="production"
        )

        # Assert
        assert config.connection_arn == (
            "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
        )
        assert config.repository_name == "test-owner/test-repo"
        assert config.branch_name == "main"
        assert config.environment == "production"
        assert config.pipeline_name == "test-repo-production-pipeline"

    def test_pipeline_config_with_custom_values(self):
        """Test PipelineConfig creation with custom values."""
        # Arrange & Act
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-west-2:987654321098:connection/custom-connection"
            ),
            repository_name="myorg/myrepo",
            branch_name="develop",
            environment="staging"
        )

        # Assert
        assert config.connection_arn == (
            "arn:aws:codeconnections:us-west-2:987654321098:connection/custom-connection"
        )
        assert config.repository_name == "myorg/myrepo"
        assert config.branch_name == "develop"
        assert config.environment == "staging"
        assert config.pipeline_name == "myrepo-staging-pipeline"

    def test_pipeline_config_validation_invalid_connection_arn(self):
        """Test PipelineConfig validation with invalid connection ARN."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Invalid CodeConnections ARN format"
        ):
            PipelineConfig(
                connection_arn="invalid-arn",
                repository_name="test-owner/test-repo",
                branch_name="main",
                environment="production"
            )

    def test_pipeline_config_validation_invalid_repository_name(self):
        """Test PipelineConfig validation with invalid repository name."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Repository name must be in 'owner/repo' format"
        ):
            PipelineConfig(
                connection_arn=(
                    "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
                ),
                repository_name="invalid-repo-name",
                branch_name="main",
                environment="production"
            )

    def test_pipeline_config_validation_invalid_environment(self):
        """Test PipelineConfig validation with invalid environment."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Environment name must be alphanumeric"
        ):
            PipelineConfig(
                connection_arn=(
                    "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
                ),
                repository_name="test-owner/test-repo",
                branch_name="main",
                environment="invalid environment!"
            )

    def test_pipeline_config_validation_invalid_branch_name(self):
        """Test PipelineConfig validation with invalid branch name."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Invalid Git branch name format"
        ):
            PipelineConfig(
                connection_arn=(
                    "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
                ),
                repository_name="test-owner/test-repo",
                branch_name="invalid branch name",
                environment="production"
            )

    def test_pipeline_config_validation_invalid_branch_empty(self):
        """Test PipelineConfig validation with empty branch name."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Branch name is required"):
            PipelineConfig(
                connection_arn=(
                    "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
                ),
                repository_name="test-owner/test-repo",
                branch_name="",
                environment="production"
            )

    def test_pipeline_config_helper_methods(self):
        """Test PipelineConfig helper methods."""
        # Arrange & Act
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name="main",
            environment="production"
        )

        # Assert
        assert config.get_repository_name() == "test-repo"
        assert config.get_repository_owner() == "test-owner"
        assert config.get_pipeline_name() == "test-repo-production-pipeline"

    def test_pipeline_config_validation_repository_edge_cases(self):
        """Test PipelineConfig repository name validation edge cases."""
        # Test with minimal valid repository name
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="a/b",
            branch_name="main",
            environment="production"
        )
        assert config.get_repository_owner() == "a"
        assert config.get_repository_name() == "b"

    def test_pipeline_config_connection_arn_validation(self):
        """Test PipelineConfig connection ARN validation."""
        # Test valid connection ARN formats
        valid_arns = [
            "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id",
            "arn:aws:codeconnections:us-west-2:987654321098:connection/another-connection",
            "arn:aws:codeconnections:eu-west-1:111111111111:connection/connection-123"
        ]

        for arn in valid_arns:
            config = PipelineConfig(
                connection_arn=arn,
                repository_name="test-owner/test-repo",
                branch_name="main",
                environment="production"
            )
            assert config.connection_arn == arn

    def test_pipeline_config_generated_pipeline_name(self):
        """Test PipelineConfig generated pipeline name."""
        # Arrange
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name="main",
            environment="production"
        )

        # Act & Assert
        assert config.get_repository_owner() == "test-owner"
        assert config.get_repository_name() == "test-repo"
        assert config.get_pipeline_name() == "test-repo-production-pipeline"

    def test_pipeline_config_different_environments(self):
        """Test PipelineConfig with different environment names."""
        # Test various valid environment names
        environments = ["production", "staging", "development", "test", "prod", "dev"]

        for env in environments:
            config = PipelineConfig(
                connection_arn=(
                    "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
                ),
                repository_name="test-owner/test-repo",
                branch_name="main",
                environment=env
            )
            assert config.environment == env
            assert config.get_pipeline_name() == f"test-repo-{env}-pipeline"

    @pytest.mark.parametrize("branch_name", [
        "main",
        "develop",
        "feature/new-feature",
        "hotfix/bug-fix",
        "release/v1.0.0",
        "feature_branch",
        "test-branch",
        "a",  # Single character
        "feature123"
    ])
    def test_pipeline_config_valid_branch_names(self, branch_name):
        """Test PipelineConfig with various valid branch names."""
        # Arrange & Act
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name=branch_name,
            environment="production"
        )

        # Assert
        assert config.branch_name == branch_name

    @pytest.mark.parametrize("repo_name", [
        "owner/repo",
        "my-org/my-repo",
        "test-owner/test-repo-name",
        "a/b",
        "organization123/project456"
    ])
    def test_pipeline_config_valid_repository_names(self, repo_name):
        """Test PipelineConfig with various valid repository names."""
        # Arrange & Act
        config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name=repo_name,
            branch_name="main",
            environment="production"
        )

        # Assert
        assert config.repository_name == repo_name
        owner, repo = repo_name.split('/')
        assert config.get_repository_owner() == owner
        assert config.get_repository_name() == repo

    def test_pipeline_config_xss_prevention_sanitization(self):
        """Test that pipeline names are properly sanitized to prevent XSS."""
        # Arrange - Use valid inputs that will pass validation but test sanitization
        config = PipelineConfig(
            connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                           "connection/test-connection",
            repository_name="owner/repo-with-special_chars",
            branch_name="main",
            environment="prod-test"
        )

        # Act - Test the sanitization method directly with malicious input
        malicious_repo = "repo<script>alert('xss')</script>"
        malicious_env = "prod<img src=x onerror=alert('xss')>"

        # pylint: disable=protected-access
        sanitized_repo = config._sanitize_for_aws_resource_name(malicious_repo)
        sanitized_env = config._sanitize_for_aws_resource_name(malicious_env)

        # Assert - Dangerous characters should be removed
        assert "<" not in sanitized_repo
        assert ">" not in sanitized_repo
        assert "(" not in sanitized_repo
        assert ")" not in sanitized_repo
        assert "'" not in sanitized_repo
        assert "<" not in sanitized_env
        assert ">" not in sanitized_env
        assert "=" not in sanitized_env

        # Should contain only safe characters
        safe_pattern = r'^[a-zA-Z0-9\-_]*$'
        assert re.match(safe_pattern, sanitized_repo)
        assert re.match(safe_pattern, sanitized_env)

        # Verify expected sanitized output
        assert sanitized_repo == "reposcriptalertxssscript"
        assert sanitized_env == "prodimgsrcxonerroralertxss"

    def test_pipeline_config_html_escape_for_display(self):
        """Test that display methods properly escape HTML characters."""
        # Arrange - Use valid config but test display methods with HTML-like content
        config = PipelineConfig(
            connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                           "connection/test-connection",
            repository_name="owner/repo-test",
            branch_name="main",
            environment="prod-test"
        )

        # Test HTML escaping by directly testing with HTML content
        # (In real scenarios, this would come from user input that needs escaping)
        test_repo_with_html = "repo<test>"
        test_env_with_html = "prod&test"

        # Mock the repository name temporarily for testing display
        original_repo = config.repository_name
        config.repository_name = f"owner/{test_repo_with_html}"
        config.environment = test_env_with_html

        # Act
        repo_display = config.get_repository_name_for_display()
        env_display = config.get_environment_for_display()

        # Restore original values
        config.repository_name = original_repo
        config.environment = "prod-test"

        # Assert - HTML characters should be escaped
        assert "&lt;test&gt;" in repo_display
        assert "&amp;test" in env_display

    def test_pipeline_config_sanitize_aws_resource_name(self):
        """Test the _sanitize_for_aws_resource_name method directly."""
        # Arrange
        config = PipelineConfig(
            connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                           "connection/test-connection",
            repository_name="owner/repo",
            branch_name="main",
            environment="production"
        )

        # Test various dangerous inputs
        test_cases = [
            ("<script>alert('xss')</script>", "scriptalertxssscript"),
            ("repo<img src=x>", "repoimgsrcx"),
            ("test&amp;name", "testampname"),
            ("name with spaces", "namewithspaces"),
            ("name/with/slashes", "namewithslashes"),
            ("", "default"),
            ("123-valid_name", "123-valid_name"),
            ("a" * 60, "a" * 50),  # Test length limit
            ("!@#$%^&*()", "default"),  # All special chars should result in default
        ]

        for input_name, expected_output in test_cases:
            # Act
            # pylint: disable=protected-access
            result = config._sanitize_for_aws_resource_name(input_name)

            # Assert
            expected_msg = (f"Input '{input_name}' should produce "
                           f"'{expected_output}', got '{result}'")
            assert result == expected_output, expected_msg

            # Ensure result contains only safe characters
            if result != "default":
                safe_pattern = r'^[a-zA-Z0-9\-_]*$'
                assert re.match(safe_pattern, result), \
                    f"Result '{result}' contains unsafe characters"

    def test_pipeline_config_validation_dangerous_characters(self):
        """Test that validation rejects inputs with dangerous characters."""
        dangerous_environments = [
            "prod<script>",
            "test'alert()",
            'env"injection',
            "name&lt;script&gt;",
            "env`command`",
            "test(function)",
            "env{code}",
            "test[array]"
        ]

        for dangerous_env in dangerous_environments:
            # The validation will catch these as invalid format first, which is good security
            with pytest.raises(ValueError):
                PipelineConfig(
                    connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                                   "connection/test-connection",
                    repository_name="owner/repo",
                    branch_name="main",
                    environment=dangerous_env
                )

    def test_pipeline_config_validation_unsafe_repository_names(self):
        """Test that validation rejects repository names with unsafe characters."""
        unsafe_repositories = [
            "owner/repo<script>",
            "owner/repo'alert()",
            'owner/repo"injection',
            "owner/repo`command`",
            "owner/repo(function)",
            "owner/repo{code}",
            "owner/repo[array]"
        ]

        for unsafe_repo in unsafe_repositories:
            # The validation will catch these as containing unsafe characters
            with pytest.raises(ValueError, match="unsafe characters"):
                PipelineConfig(
                    connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                                   "connection/test-connection",
                    repository_name=unsafe_repo,
                    branch_name="main",
                    environment="production"
                )

    def test_pipeline_config_safe_characters_allowed(self):
        """Test that safe characters are still allowed in repository names and environments."""
        # These should all be valid (environments can't have dots due to validation)
        safe_configs = [
            ("owner/repo-name", "prod-env"),
            ("owner/repo_name", "test_env"),
            ("owner/repo.name", "dev-env"),  # Changed from dev.env
            ("owner123/repo456", "env789"),
            ("my-org/my-repo", "staging-2"),
        ]

        for repo_name, env_name in safe_configs:
            # Should not raise any exceptions
            config = PipelineConfig(
                connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                               "connection/test-connection",
                repository_name=repo_name,
                branch_name="main",
                environment=env_name
            )

            # Verify the config was created successfully
            assert config.repository_name == repo_name
            assert config.environment == env_name

            # Verify pipeline name generation works
            pipeline_name = config.get_pipeline_name()
            assert pipeline_name.endswith("-pipeline")

    @pytest.mark.parametrize("malicious_input,expected_sanitized", [
        ("<script>alert('XSS')</script>", "scriptalertXSSscript"),
        ("repo<img src=x onerror=alert(1)>", "repoimgsrcxonerroralert1"),
        ("test&lt;script&gt;", "testltscriptgt"),
        ("name with spaces and <tags>", "namewithspacesandtags"),
        ("javascript:alert('xss')", "javascriptalertxss"),
        ("data:text/html,<script>alert(1)</script>",
         "datatexthtmlscriptalert1script"),
    ])
    def test_pipeline_config_xss_attack_vectors(self, malicious_input,
                                                expected_sanitized):
        """Test various XSS attack vectors are properly sanitized."""
        # Arrange
        config = PipelineConfig(
            connection_arn="arn:aws:codeconnections:us-east-1:123456789012:"
                           "connection/test-connection",
            repository_name="owner/repo",
            branch_name="main",
            environment="production"
        )

        # Act
        # pylint: disable=protected-access
        sanitized = config._sanitize_for_aws_resource_name(malicious_input)

        # Assert
        assert sanitized == expected_sanitized

        # Ensure no dangerous patterns remain
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'alert(', 'src=x']
        for pattern in dangerous_patterns:
            assert pattern not in sanitized.lower()
