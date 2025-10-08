"""
Pytest configuration and shared fixtures for stacksets_blog tests.

This module contains pytest configuration and shared fixtures that can be
used across all test modules in the stacksets_blog test suite.
"""

import json
import os

import pytest
from aws_cdk import App
from stacksets_blog.config import StackSetConfig, MonitoringConfig, EnvironmentConfig

# Shared test constants to reduce code duplication
TEST_ACCOUNT = "123456789012"
TEST_REGION = "us-east-1"
TEST_EMAIL = "test@example.com"
TEST_DASHBOARD = "TestDashboard"
TEST_ALARM_PREFIX = "TestAlarms"
TEST_TARGET_ACCOUNTS = "123456789013,123456789014"

# Common test alarm thresholds
SIMPLE_ALARM_THRESHOLDS = {"CPUUtilization": 80.0}

STACKSET_CONFIG_PARAMS = {
    "stack_set_name": "TestStackSet",
    "target_regions": ["us-east-1", "us-west-2"],
    "target_accounts": ["123456789012", "123456789013"],
    "instance_stack_name": "TestMonitoringStack",
    "parameters": {
        "NotificationEmail": TEST_EMAIL,
        "DashboardName": TEST_DASHBOARD,
        "AlarmPrefix": TEST_ALARM_PREFIX
    },
    "max_concurrent_percentage": 50,
    "failure_tolerance_percentage": 10,
    "region_concurrency_type": "SEQUENTIAL"
}

ENVIRONMENT_CONFIG_PARAMS = {
    "account": TEST_ACCOUNT,
    "region": TEST_REGION,
    "notification_email": TEST_EMAIL,
    "dashboard_name": TEST_DASHBOARD,
    "alarm_prefix": TEST_ALARM_PREFIX,
    "target_accounts": TEST_TARGET_ACCOUNTS
}

# Additional shared config variants
SINGLE_ACCOUNT_ENV_CONFIG = {
    "account": TEST_ACCOUNT,
    "region": TEST_REGION,
    "notification_email": TEST_EMAIL,
    "dashboard_name": TEST_DASHBOARD,
    "alarm_prefix": TEST_ALARM_PREFIX,
    "target_accounts": "123456789013"
}

SIMPLE_STACKSET_CONFIG = {
    "stack_set_name": "TestStackSet",
    "target_regions": ["us-east-1"],
    "target_accounts": ["123456789012"],
    "instance_stack_name": "TestStack",
    "parameters": {"NotificationEmail": TEST_EMAIL}
}


@pytest.fixture
def cdk_app():
    """Fixture that provides a CDK App instance for testing."""
    return App()


@pytest.fixture
def sample_stackset_config():
    """Fixture that provides a sample StackSetConfig for testing."""
    return StackSetConfig(**STACKSET_CONFIG_PARAMS)


@pytest.fixture
def sample_monitoring_config():
    """Fixture that provides a sample MonitoringConfig for testing."""
    return MonitoringConfig(
        dashboard_name="TestDashboard",
        notification_email="test@example.com",
        alarm_thresholds={
            "CPUUtilization": 80.0,
            "MemoryUtilization": 85.0,
            "DiskSpaceUtilization": 90.0,
            "RDSCPUUtilization": 75.0,
            "RDSFreeStorageSpace": 2000000000,
            "LambdaErrors": 5.0,
            "LambdaDuration": 30000.0
        },
        alarm_prefix="TestAlarms"
    )


@pytest.fixture
def sample_environment_config():
    """Fixture that provides a sample EnvironmentConfig for testing."""
    return EnvironmentConfig(**ENVIRONMENT_CONFIG_PARAMS)


@pytest.fixture
def mock_environment_variables():
    """Fixture that sets up mock environment variables for testing."""
    original_env = {}
    test_env_vars = {
        "CDK_DEFAULT_ACCOUNT": "123456789012",
        "CDK_DEFAULT_REGION": "us-east-1",
        "NOTIFICATION_EMAIL": "test@example.com",
        "DASHBOARD_NAME": "TestDashboard",
        "ALARM_PREFIX": "TestAlarms",
        "TARGET_ACCOUNTS": "123456789013,123456789014"
    }

    # Store original values
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_env_vars

    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture that creates a temporary config.json file for testing."""
    config_content = {
        "stackset": {
            "stack_set_name": "TestStackSet",
            "target_regions": ["us-east-1", "us-west-2"],
            "instance_stack_name": "TestMonitoringStack",
            "max_concurrent_percentage": 50,
            "failure_tolerance_percentage": 10,
            "region_concurrency_type": "SEQUENTIAL"
        },
        "monitoring": {
            "alarm_thresholds": {
                "CPUUtilization": 80.0,
                "MemoryUtilization": 85.0,
                "DiskSpaceUtilization": 90.0,
                "RDSCPUUtilization": 75.0,
                "RDSFreeStorageSpace": 2000000000,
                "LambdaErrors": 5.0,
                "LambdaDuration": 30000.0
            }
        }
    }

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_content, indent=2), encoding='utf-8')
    return str(config_file)


# Test the fixtures to ensure they work correctly
def test_sample_stackset_config_fixture(sample_stackset_config):
    """Test that the sample_stackset_config fixture works correctly."""
    # pylint: disable=redefined-outer-name
    assert sample_stackset_config.stack_set_name == "TestStackSet"
    assert len(sample_stackset_config.target_regions) == 2
    assert len(sample_stackset_config.target_accounts) == 2


def test_sample_monitoring_config_fixture(sample_monitoring_config):
    """Test that the sample_monitoring_config fixture works correctly."""
    # pylint: disable=redefined-outer-name
    assert sample_monitoring_config.dashboard_name == "TestDashboard"
    assert sample_monitoring_config.notification_email == "test@example.com"
    assert "CPUUtilization" in sample_monitoring_config.alarm_thresholds


def test_sample_environment_config_fixture(sample_environment_config):
    """Test that the sample_environment_config fixture works correctly."""
    # pylint: disable=redefined-outer-name
    assert sample_environment_config.account == "123456789012"
    assert sample_environment_config.region == "us-east-1"
    assert sample_environment_config.notification_email == "test@example.com"


def test_mock_environment_variables_fixture(mock_environment_variables):
    """Test that the mock_environment_variables fixture works correctly."""
    # pylint: disable=redefined-outer-name
    assert os.environ.get("CDK_DEFAULT_ACCOUNT") == "123456789012"
    assert os.environ.get("NOTIFICATION_EMAIL") == "test@example.com"
    assert len(mock_environment_variables) == 6


def test_temp_config_file_fixture(temp_config_file):
    """Test that the temp_config_file fixture works correctly."""
    # pylint: disable=redefined-outer-name
    assert os.path.exists(temp_config_file)

    with open(temp_config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    assert "stackset" in config
    assert "monitoring" in config
    assert config["stackset"]["stack_set_name"] == "TestStackSet"
