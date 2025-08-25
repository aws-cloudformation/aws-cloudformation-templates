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

from stacksets_blog.config import StackSetConfig, MonitoringConfig, EnvironmentConfig
from stacksets_blog.utils import (
    get_environment_config,
    load_config_file,
    get_stackset_config,
    get_monitoring_config
)
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
        # Arrange & Act
        get_environment_config()

        # Assert
        mock_exit.assert_called_once_with(1)


class TestLoadConfigFile:
    """Test suite for load_config_file function."""

    def test_load_config_file_success(self):
        """Test successful config file loading."""
        # Arrange
        config_data = {
            "stackset": {"stack_set_name": "TestStackSet"},
            "monitoring": {"alarm_thresholds": {"CPUUtilization": 80.0}}
        }
        config_json = json.dumps(config_data)

        with patch("builtins.open", mock_open(read_data=config_json)):
            # Act
            result = load_config_file("config.json")

            # Assert
            assert result == config_data

    @patch('sys.exit')
    def test_load_config_file_not_found(self, mock_exit):
        """Test config file loading when file doesn't exist."""
        # Arrange
        with patch("builtins.open", side_effect=FileNotFoundError):
            # Act
            load_config_file("nonexistent.json")

            # Assert
            mock_exit.assert_called_once_with(1)

    def test_load_config_file_invalid_json(self):
        """Test config file loading with invalid JSON."""
        # Arrange
        invalid_json = "{ invalid json }"

        with patch("builtins.open", mock_open(read_data=invalid_json)):
            # Act & Assert
            with pytest.raises(json.JSONDecodeError):
                load_config_file("config.json")


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
        assert result.parameters["NotificationEmail"] == "test@example.com"
        assert result.parameters["DashboardName"] == "TestDashboard"
        assert result.parameters["AlarmPrefix"] == "TestAlarms"

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
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
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
            notification_email="test@example.com",
            dashboard_name="TestDashboard",
            alarm_prefix="TestAlarms",
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
        assert result.dashboard_name == "TestDashboard"
        assert result.notification_email == "test@example.com"
        assert result.alarm_prefix == "TestAlarms"
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
