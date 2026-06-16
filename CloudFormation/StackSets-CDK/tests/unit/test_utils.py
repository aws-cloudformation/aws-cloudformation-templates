"""
Unit tests for utility functions.

This module contains comprehensive unit tests for the utility functions
including environment configuration loading, config file parsing, and
configuration object creation.
"""

import json
import os
from unittest.mock import patch, mock_open

import pytest

from stacksets_blog.config import (
    StackSetConfig, MonitoringConfig, EnvironmentConfig, PipelineConfig
)
from stacksets_blog.utils import (
    get_environment_config,
    load_config_file,
    get_stackset_config,
    get_monitoring_config,
    get_pipelines_config,
    _validate_config_path
)
from tests.conftest import TEST_EMAIL, TEST_DASHBOARD, TEST_ALARM_PREFIX
from tests.conftest import (
    ENVIRONMENT_CONFIG_PARAMS, SINGLE_ACCOUNT_ENV_CONFIG
)


class TestGetEnvironmentConfig:
    """Test suite for get_environment_config function."""

    @patch.dict(os.environ, {
        'CDK_DEFAULT_ACCOUNT': '123456789012',
        'CDK_DEFAULT_REGION': 'us-east-1',
        'NOTIFICATION_EMAIL': 'test@example.com',
        'DASHBOARD_NAME': 'TestDashboard',
        'ALARM_PREFIX': 'TestAlarms',
        'TARGET_ACCOUNTS': '123456789013,123456789014'
    })
    def test_get_environment_config_success(self):
        """Test successful environment configuration loading."""
        # Arrange & Act
        config = get_environment_config()

        # Assert
        assert isinstance(config, EnvironmentConfig)
        assert config.account == '123456789012'
        assert config.region == 'us-east-1'
        assert config.notification_email == 'test@example.com'
        assert config.dashboard_name == 'TestDashboard'
        assert config.alarm_prefix == 'TestAlarms'
        assert config.target_accounts == '123456789013,123456789014'

    @patch.dict(os.environ, {}, clear=True)
    @patch('sys.exit')
    def test_get_environment_config_missing_vars(self, mock_exit):
        """Test environment configuration loading with missing variables."""
        # Arrange
        mock_exit.side_effect = SystemExit(1)
        # Act & Assert
        with pytest.raises(SystemExit):
            get_environment_config()

        mock_exit.assert_called_once_with(1)


class TestValidateConfigPath:
    """Test suite for _validate_config_path function."""

    def test_validate_config_path_success(self):
        """Test successful path validation with valid JSON file."""
        # Arrange & Act
        result = _validate_config_path("config.json")

        # Assert
        assert result.endswith("config.json")
        assert ".." not in result

    def test_validate_config_path_subdirectory(self):
        """Test path validation with file in subdirectory."""
        # Arrange & Act
        result = _validate_config_path("configs/app.json")

        # Assert
        assert "configs/app.json" in result

    def test_validate_config_path_traversal_attempt(self):
        """Test path validation rejects path traversal attempts."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            _validate_config_path("../../../etc/passwd")

    def test_validate_config_path_absolute_path(self):
        """Test path validation rejects absolute paths."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            _validate_config_path("/etc/passwd")

    def test_validate_config_path_non_json_file(self):
        """Test path validation rejects non-JSON files."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Only JSON configuration files are allowed"):
            _validate_config_path("config.txt")

    def test_validate_config_path_hidden_traversal(self):
        """Test path validation rejects hidden path traversal attempts."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Path traversal attempt detected"):
            _validate_config_path("config/../../../etc/passwd.json")


class TestLoadConfigFile:
    """Test suite for load_config_file function."""

    @patch('stacksets_blog.utils._validate_config_path')
    def test_load_config_file_success(self, mock_validate):
        """Test successful config file loading."""
        # Arrange
        config_data = {
            "stackset": {"stack_set_name": "TestStackSet"},
            "monitoring": {"alarm_thresholds": {"CPUUtilization": 80.0}}
        }
        config_json = json.dumps(config_data)
        mock_validate.return_value = "config.json"

        with patch("builtins.open", mock_open(read_data=config_json)):
            # Act
            result = load_config_file("config.json")

            # Assert
            assert result == config_data
            mock_validate.assert_called_once_with("config.json")

    @patch('sys.exit')
    def test_load_config_file_not_found(self, mock_exit):
        """Test config file loading when file doesn't exist."""
        # Arrange
        with patch("builtins.open", side_effect=FileNotFoundError):
            # Act
            load_config_file("nonexistent.json")

            # Assert
            mock_exit.assert_called_once_with(1)

    @patch('stacksets_blog.utils._validate_config_path')
    def test_load_config_file_invalid_json(self, mock_validate):
        """Test config file loading with invalid JSON."""
        # Arrange
        invalid_json = "{ invalid json }"
        mock_validate.return_value = "config.json"

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            # Act & Assert
            with pytest.raises(json.JSONDecodeError):
                load_config_file("config.json")

    @patch('sys.exit')
    @patch('stacksets_blog.utils._validate_config_path')
    def test_load_config_file_path_traversal_attempt(self, mock_validate, mock_exit):
        """Test config file loading with path traversal attempt."""
        # Arrange
        mock_validate.side_effect = ValueError("Path traversal attempt detected")

        # Act
        load_config_file("../../../etc/passwd")

        # Assert
        mock_exit.assert_called_once_with(1)


class TestGetStacksetConfig:
    """Test suite for get_stackset_config function."""

    def setup_method(self):
        """Set up test fixtures."""
        # pylint: disable=attribute-defined-outside-init
        self.env_config = EnvironmentConfig(**ENVIRONMENT_CONFIG_PARAMS)

        self.config_data = {  # pylint: disable=attribute-defined-outside-init
            "stackset": {
                "stack_set_name": "TestStackSet",
                "target_regions": ["us-east-1", "us-west-2"],
                "instance_stack_name": "TestStack",
                "max_concurrent_percentage": 50,
                "failure_tolerance_percentage": 10,
                "region_concurrency_type": "SEQUENTIAL"
            }
        }

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_stackset_config_success(self, mock_load_config):
        """Test successful StackSet configuration creation."""
        # Arrange
        mock_load_config.return_value = self.config_data

        # Act
        result = get_stackset_config("config.json", self.env_config)

        # Assert
        assert isinstance(result, StackSetConfig)
        assert result.stack_set_name == "TestStackSet"
        assert result.target_regions == ["us-east-1", "us-west-2"]
        assert result.target_accounts == ["123456789013", "123456789014"]
        assert result.instance_stack_name == "TestStack"
        assert result.parameters["NotificationEmail"] == TEST_EMAIL
        assert result.parameters["DashboardName"] == TEST_DASHBOARD
        assert result.parameters["AlarmPrefix"] == TEST_ALARM_PREFIX

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_stackset_config_missing_stackset_section(self, mock_load_config):
        """Test StackSet configuration creation with missing stackset section."""
        # Arrange
        mock_load_config.return_value = {"monitoring": {}}

        # Act & Assert
        with pytest.raises(KeyError):
            get_stackset_config("config.json", self.env_config)

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_stackset_config_target_accounts_parsing(self, mock_load_config):
        """Test target accounts parsing from comma-separated string."""
        # Arrange
        mock_load_config.return_value = self.config_data
        env_config_single = EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email=TEST_EMAIL,
            dashboard_name=TEST_DASHBOARD,
            alarm_prefix=TEST_ALARM_PREFIX,
            target_accounts="123456789013"  # Single account
        )

        # Act
        result = get_stackset_config("config.json", env_config_single)

        # Assert
        assert result.target_accounts == ["123456789013"]

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_stackset_config_target_accounts_with_spaces(self, mock_load_config):
        """Test target accounts parsing with spaces in the string."""
        # Arrange
        mock_load_config.return_value = self.config_data
        env_config_spaces = EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email=TEST_EMAIL,
            dashboard_name=TEST_DASHBOARD,
            alarm_prefix=TEST_ALARM_PREFIX,
            target_accounts=" 123456789013 , 123456789014 "  # With spaces
        )

        # Act
        result = get_stackset_config("config.json", env_config_spaces)

        # Assert
        assert result.target_accounts == ["123456789013", "123456789014"]


class TestGetMonitoringConfig:
    """Test suite for get_monitoring_config function."""

    def setup_method(self):
        """Set up test fixtures."""
        # pylint: disable=attribute-defined-outside-init
        self.env_config = EnvironmentConfig(**SINGLE_ACCOUNT_ENV_CONFIG)

        self.config_data = {  # pylint: disable=attribute-defined-outside-init
            "monitoring": {
                "alarm_thresholds": {
                    "CPUUtilization": 80.0,
                    "MemoryUtilization": 85.0,
                    "DiskSpaceUtilization": 90.0
                }
            }
        }

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_monitoring_config_success(self, mock_load_config):
        """Test successful monitoring configuration creation."""
        # Arrange
        mock_load_config.return_value = self.config_data

        # Act
        result = get_monitoring_config("config.json", self.env_config)

        # Assert
        assert isinstance(result, MonitoringConfig)
        assert result.dashboard_name == TEST_DASHBOARD
        assert result.notification_email == TEST_EMAIL
        assert result.alarm_prefix == TEST_ALARM_PREFIX
        assert result.alarm_thresholds == {
            "CPUUtilization": 80.0,
            "MemoryUtilization": 85.0,
            "DiskSpaceUtilization": 90.0
        }

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_monitoring_config_missing_monitoring_section(self, mock_load_config):
        """Test monitoring configuration creation with missing monitoring section."""
        # Arrange
        mock_load_config.return_value = {"stackset": {}}

        # Act & Assert
        with pytest.raises(KeyError):
            get_monitoring_config("config.json", self.env_config)

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_monitoring_config_empty_thresholds(self, mock_load_config):
        """Test monitoring configuration creation with empty alarm thresholds."""
        # Arrange
        config_data = {
            "monitoring": {
                "alarm_thresholds": {}
            }
        }
        mock_load_config.return_value = config_data

        # Act
        result = get_monitoring_config("config.json", self.env_config)

        # Assert
        assert not result.alarm_thresholds

    @pytest.mark.parametrize("dashboard_name,email,prefix", [
        ("Dashboard1", "user1@test.com", "Prefix1"),
        ("Dashboard2", "user2@test.com", "Prefix2"),
        ("ProductionDashboard", "admin@company.com", "ProdAlarms"),
    ])
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_monitoring_config_various_env_configs(
        self, mock_load_config, dashboard_name, email, prefix
    ):
        """Test monitoring configuration with various environment configurations."""
        # Arrange
        mock_load_config.return_value = self.config_data
        env_config = EnvironmentConfig(
            account="123456789012",
            region="us-east-1",
            notification_email=email,
            dashboard_name=dashboard_name,
            alarm_prefix=prefix,
            target_accounts="123456789013"
        )

        # Act
        result = get_monitoring_config("config.json", env_config)

        # Assert
        assert result.dashboard_name == dashboard_name
        assert result.notification_email == email
        assert result.alarm_prefix == prefix


class TestGetPipelinesConfig:
    """Test suite for get_pipelines_config function."""

    def setup_method(self):
        """Set up test fixtures."""
        # pylint: disable=attribute-defined-outside-init
        self.config_data = {
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

    @patch.dict(os.environ, {
        'CODE_CONNECTION_ARN': 'arn:aws:codeconnections:us-east-1:123456789012:'
                               'connection/test-connection',
        'REPOSITORY': 'owner/repo'
    })
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_success(self, mock_load_config):
        """Test successful pipeline configuration creation."""
        # Arrange
        mock_load_config.return_value = self.config_data

        # Act
        result = get_pipelines_config("config.json")

        # Assert
        assert len(result) == 2
        assert all(isinstance(pipeline, PipelineConfig) for pipeline in result)

        # Check first pipeline
        expected_arn = 'arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection'
        assert result[0].connection_arn == expected_arn
        assert result[0].repository_name == 'owner/repo'
        assert result[0].branch_name == 'main'
        assert result[0].environment == 'production'

        # Check second pipeline
        assert result[1].connection_arn == expected_arn
        assert result[1].repository_name == 'owner/repo'
        assert result[1].branch_name == 'develop'
        assert result[1].environment == 'staging'

    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_missing_pipelines_section(self, mock_load_config):
        """Test pipeline configuration creation with missing pipelines section."""
        # Arrange
        mock_load_config.return_value = {"monitoring": {}}

        # Act & Assert
        with pytest.raises(KeyError):
            get_pipelines_config("config.json")

    @patch.dict(os.environ, {}, clear=True)
    @patch('sys.exit')
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_missing_connection_arn(self, mock_load_config, mock_exit):
        """Test pipeline configuration creation with missing CODE_CONNECTION_ARN."""
        # Arrange
        mock_load_config.return_value = self.config_data
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually raise SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            get_pipelines_config("config.json")

        mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {
        'CODE_CONNECTION_ARN': 'arn:aws:codeconnections:us-east-1:123456789012:'
                               'connection/test-connection'
    })
    @patch('sys.exit')
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_missing_repository(self, mock_load_config, mock_exit):
        """Test pipeline configuration creation with missing REPOSITORY."""
        # Arrange
        mock_load_config.return_value = self.config_data
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually raise SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            get_pipelines_config("config.json")

        mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {}, clear=True)
    @patch('sys.exit')
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_missing_both_env_vars(self, mock_load_config, mock_exit):
        """Test pipeline configuration creation with both environment variables missing."""
        # Arrange
        mock_load_config.return_value = self.config_data
        mock_exit.side_effect = SystemExit(1)  # Make sys.exit actually raise SystemExit

        # Act & Assert
        with pytest.raises(SystemExit):
            get_pipelines_config("config.json")

        mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {
        'CODE_CONNECTION_ARN': 'arn:aws:codeconnections:us-west-2:987654321098:'
                               'connection/prod-connection',
        'REPOSITORY': 'myorg/myrepo'
    })
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_single_pipeline(self, mock_load_config):
        """Test pipeline configuration creation with single pipeline."""
        # Arrange
        single_pipeline_config = {
            "pipelines": [
                {
                    "branch_name": "main",
                    "environment": "production"
                }
            ]
        }
        mock_load_config.return_value = single_pipeline_config

        # Act
        result = get_pipelines_config("config.json")

        # Assert
        assert len(result) == 1
        expected_arn = 'arn:aws:codeconnections:us-west-2:987654321098:connection/prod-connection'
        assert result[0].connection_arn == expected_arn
        assert result[0].repository_name == 'myorg/myrepo'
        assert result[0].branch_name == 'main'
        assert result[0].environment == 'production'

    @patch.dict(os.environ, {
        'CODE_CONNECTION_ARN': 'arn:aws:codeconnections:us-east-1:123456789012:'
                               'connection/test-connection',
        'REPOSITORY': 'owner/repo'
    })
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_empty_pipelines_list(self, mock_load_config):
        """Test pipeline configuration creation with empty pipelines list."""
        # Arrange
        empty_config = {"pipelines": []}
        mock_load_config.return_value = empty_config

        # Act
        result = get_pipelines_config("config.json")

        # Assert
        assert len(result) == 0
        assert not result

    @pytest.mark.parametrize("connection_arn,repository", [
        ("arn:aws:codeconnections:us-east-1:123456789012:connection/conn1",
         "org1/repo1"),
        ("arn:aws:codeconnections:us-west-2:987654321098:connection/conn2",
         "org2/repo2"),
        ("arn:aws:codeconnections:eu-west-1:111122223333:connection/conn3",
         "myorg/myrepo"),
    ])
    @patch('stacksets_blog.utils.load_config_file')
    def test_get_pipelines_config_various_env_values(self, mock_load_config,
                                                      connection_arn, repository):
        """Test pipeline configuration with various environment variable values."""
        # Arrange
        mock_load_config.return_value = self.config_data

        with patch.dict(os.environ, {
            'CODE_CONNECTION_ARN': connection_arn,
            'REPOSITORY': repository
        }):
            # Act
            result = get_pipelines_config("config.json")

            # Assert
            assert len(result) == 2
            for pipeline in result:
                assert pipeline.connection_arn == connection_arn
                assert pipeline.repository_name == repository
