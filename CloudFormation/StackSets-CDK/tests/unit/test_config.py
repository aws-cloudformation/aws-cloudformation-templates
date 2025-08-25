"""
Unit tests for configuration classes.

This module contains comprehensive unit tests for the configuration classes
including StackSetConfig, MonitoringConfig, and EnvironmentConfig.
"""

from unittest.mock import patch

import pytest
from stacksets_blog.config import (
    StackSetConfig, MonitoringConfig, EnvironmentConfig, PipelineConfig
)
from tests.conftest import (
    SIMPLE_STACKSET_CONFIG, SINGLE_ACCOUNT_ENV_CONFIG, ENVIRONMENT_CONFIG_PARAMS
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
            dashboard_name="TestDashboard",
            notification_email="test@example.com",
            alarm_thresholds={"CPUUtilization": 80.0},
            alarm_prefix="TestAlarms"
        )

        # Assert
        assert config.dashboard_name == "TestDashboard"
        assert config.notification_email == "test@example.com"
        assert config.alarm_thresholds == {"CPUUtilization": 80.0}
        assert config.alarm_prefix == "TestAlarms"

    def test_monitoring_config_with_default_alarm_prefix(self):
        """Test MonitoringConfig with default alarm prefix."""
        # Arrange & Act
        config = MonitoringConfig(
            dashboard_name="TestDashboard",
            notification_email="test@example.com",
            alarm_thresholds={"CPUUtilization": 80.0}
        )

        # Assert
        assert config.alarm_prefix == "StackSets-Blog"

    def test_monitoring_config_validation_empty_dashboard_name(self):
        """Test MonitoringConfig validation with empty dashboard name."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Dashboard name must be between 1 and 255 characters"):
            MonitoringConfig(
                dashboard_name="",
                notification_email="test@example.com",
                alarm_thresholds={"CPUUtilization": 80.0}
            )

    def test_monitoring_config_validation_long_dashboard_name(self):
        """Test MonitoringConfig validation with too long dashboard name."""
        # Arrange
        long_name = "a" * 256  # 256 characters

        # Act & Assert
        with pytest.raises(ValueError, match="Dashboard name must be between 1 and 255 characters"):
            MonitoringConfig(
                dashboard_name=long_name,
                notification_email="test@example.com",
                alarm_thresholds={"CPUUtilization": 80.0}
            )

    def test_monitoring_config_validation_invalid_email(self):
        """Test MonitoringConfig validation with invalid email format."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid email address format"):
            MonitoringConfig(
                dashboard_name="TestDashboard",
                notification_email="invalid-email",
                alarm_thresholds={"CPUUtilization": 80.0}
            )

    def test_monitoring_config_validation_negative_threshold(self):
        """Test MonitoringConfig validation with negative alarm threshold."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Alarm threshold for CPUUtilization must be a positive number"
        ):
            MonitoringConfig(
                dashboard_name="TestDashboard",
                notification_email="test@example.com",
                alarm_thresholds={"CPUUtilization": -10.0}
            )

    def test_monitoring_config_validation_invalid_threshold_type(self):
        """Test MonitoringConfig validation with invalid threshold type."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValueError, match="Alarm threshold for CPUUtilization must be a positive number"
        ):
            MonitoringConfig(
                dashboard_name="TestDashboard",
                notification_email="test@example.com",
                alarm_thresholds={"CPUUtilization": "invalid"}
            )

    def test_monitoring_config_validation_long_alarm_prefix(self):
        """Test MonitoringConfig validation with too long alarm prefix."""
        # Arrange
        long_prefix = "a" * 65  # 65 characters

        # Act & Assert
        with pytest.raises(ValueError, match="Alarm prefix must be between 1 and 64 characters"):
            MonitoringConfig(
                dashboard_name="TestDashboard",
                notification_email="test@example.com",
                alarm_thresholds={"CPUUtilization": 80.0},
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
            dashboard_name="TestDashboard",
            notification_email=email,
            alarm_thresholds={"CPUUtilization": 80.0}
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
        assert config.notification_email == "test@example.com"
        assert config.dashboard_name == "TestDashboard"
        assert config.alarm_prefix == "TestAlarms"
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
