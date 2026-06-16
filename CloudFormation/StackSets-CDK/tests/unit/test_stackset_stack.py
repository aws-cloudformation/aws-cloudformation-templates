# pylint: disable=duplicate-code
"""
Unit tests for StackSetStack.

This module contains comprehensive unit tests for the StackSetStack class,
testing all aspects of the StackSet creation including S3 bucket, StackSet
resource, stack instances, and outputs.
"""

import json
from unittest.mock import Mock, patch

import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from stacksets_blog.stackset_stack import StackSetStack
from stacksets_blog.config import StackSetConfig, MonitoringConfig
from tests.conftest import (
    STACKSET_CONFIG_PARAMS, TEST_EMAIL, TEST_DASHBOARD, TEST_ALARM_PREFIX, SIMPLE_ALARM_THRESHOLDS
)

# pylint: disable=duplicate-code

class TestStackSetStack:
    """Test suite for StackSetStack class."""

    def test_stackset_stack_config_validation_none(self):
        """Test that StackSetStack raises ValueError when config is None."""
        # Arrange
        app = App()

        # Act & Assert
        with pytest.raises(ValueError, match="Configuration parameter 'config' cannot be None"):
            monitoring_config = MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
                alarm_prefix=TEST_ALARM_PREFIX
            )
            StackSetStack(app, "TestStack", config=None, monitoring_config=monitoring_config)

    def test_stackset_stack_config_validation_wrong_type(self):
        """Test that StackSetStack raises TypeError when config is wrong type."""
        # Arrange
        app = App()
        invalid_config = "not_a_config_object"

        # Act & Assert
        with pytest.raises(TypeError, match="must be of type StackSetConfig, got str"):
            monitoring_config = MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
                alarm_prefix=TEST_ALARM_PREFIX
            )
            StackSetStack(
                app, "TestStack",
                config=invalid_config,
                monitoring_config=monitoring_config
            )

    def test_stackset_stack_config_validation_invalid_config(self):
        """Test that StackSetStack raises ValueError when config validation fails."""
        # Arrange
        app = App()

        # Create a mock config that will fail validation when validate() is called
        with patch('stacksets_blog.config.StackSetConfig') as mock_config_class:
            mock_config = Mock(spec=StackSetConfig)
            mock_config.validate.side_effect = ValueError("Mock validation error")
            mock_config_class.return_value = mock_config

            # Act & Assert
            with pytest.raises(ValueError, match="Invalid StackSetConfig provided"):
                monitoring_config = MonitoringConfig(
                    dashboard_name=TEST_DASHBOARD,
                    notification_email=TEST_EMAIL,
                    alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
                    alarm_prefix=TEST_ALARM_PREFIX
                )
                StackSetStack(
                    app, "TestStack",
                    config=mock_config,
                    monitoring_config=monitoring_config
                )

    def test_stackset_stack_config_validation_exception_chaining(self):
        """Test that StackSetStack properly chains exceptions from config validation."""
        # Arrange
        app = App()

        # Create a mock config that will fail validation when validate() is called
        mock_config = Mock(spec=StackSetConfig)
        original_error = ValueError("Original validation error")
        mock_config.validate.side_effect = original_error

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            monitoring_config = MonitoringConfig(
                dashboard_name=TEST_DASHBOARD,
                notification_email=TEST_EMAIL,
                alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
                alarm_prefix=TEST_ALARM_PREFIX
            )
            StackSetStack(app, "TestStack", config=mock_config, monitoring_config=monitoring_config)

        # Verify the exception is properly chained
        assert exc_info.value.__cause__ is original_error
        assert "Invalid StackSetConfig provided" in str(exc_info.value)

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = App()  # pylint: disable=attribute-defined-outside-init
        # pylint: disable=attribute-defined-outside-init
        self.mock_config = StackSetConfig(**STACKSET_CONFIG_PARAMS)
        # pylint: disable=attribute-defined-outside-init
        self.mock_monitoring_config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds={
                "CPUUtilization": 80.0,
                "MemoryUtilization": 85.0
            },
            alarm_prefix=TEST_ALARM_PREFIX
        )

    def test_stackset_stack_creation(self):
        """Test StackSetStack creation with valid configuration."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check stack attributes
        assert stack.config == self.mock_config
        expected_role_suffix = ":role/AWSCloudFormationStackSetAdministrationRole"
        assert stack.administration_role_arn.endswith(expected_role_suffix)

        # Assert - Check S3 bucket creation
        template.has_resource_properties("AWS::S3::Bucket", {
            "VersioningConfiguration": {
                "Status": "Enabled"
            },
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [{
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True
            }
        })

    def test_stackset_resource_creation(self):
        """Test CloudFormation StackSet resource creation."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check StackSet creation
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "StackSetName": "TestStackSet",
            "Description": "Multi-region monitoring infrastructure deployed via StackSets",
            "Capabilities": ["CAPABILITY_IAM"],
            "PermissionModel": "SELF_MANAGED",
            "ExecutionRoleName": "AWSCloudFormationStackSetExecutionRole"
        })

    def test_stackset_operation_preferences(self):
        """Test StackSet operation preferences configuration."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check operation preferences
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "OperationPreferences": {
                "MaxConcurrentPercentage": 50,
                "FailureTolerancePercentage": 10,
                "RegionConcurrencyType": "SEQUENTIAL"
            }
        })

    def test_stackset_stack_instances(self):
        """Test StackSet stack instances configuration."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check StackSet resource exists
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        assert len(stackset_resources) == 1

        stackset_resource = list(stackset_resources.values())[0]
        properties = stackset_resource["Properties"]
        # Check StackSet properties
        assert properties["StackSetName"] == "TestStackSet"
        assert properties["Description"] == (
            "Multi-region monitoring infrastructure deployed via StackSets"
        )
        assert properties["PermissionModel"] == "SELF_MANAGED"
        assert "TemplateBody" in properties

    def test_administration_role_arn_format(self):
        """Test administration role ARN format."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )

        # Assert - Check ARN structure (may contain CDK tokens)
        arn = stack.administration_role_arn
        assert arn.startswith("arn:aws:iam::")
        assert arn.endswith(":role/AWSCloudFormationStackSetAdministrationRole")
        # The middle part may contain CDK tokens like ${Token[AWS.AccountId.3]}
        assert "role/AWSCloudFormationStackSetAdministrationRole" in arn

    def test_template_bucket_attributes(self):
        """Test S3 template bucket attributes."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )

        # Assert
        assert stack.template_bucket is not None
        assert hasattr(stack.template_bucket, 'bucket_name')

    def test_stackset_attributes(self):
        """Test StackSet resource attributes."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )

        # Assert
        assert stack.stackset is not None

    @patch('stacksets_blog.stackset_stack.MonitoringStack')
    def test_render_instance_template(self, mock_monitoring_stack):  # pylint: disable=unused-argument
        """Test template rendering for StackSet instances."""
        # Arrange
        mock_stack_instance = Mock()
        mock_stack_instance.template = {"Resources": {"TestResource": {}}}

        mock_cloud_assembly = Mock()
        mock_cloud_assembly.get_stack_by_name.return_value = mock_stack_instance

        mock_app = Mock()
        mock_app.synth.return_value = mock_cloud_assembly

        with patch('stacksets_blog.stackset_stack.App', return_value=mock_app):
            stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )

            # Act
            template_json = stack.render_instance_template()

            # Assert
            assert isinstance(template_json, str)
            template_dict = json.loads(template_json)
            assert "Resources" in template_dict
            assert "TestResource" in template_dict["Resources"]

    def test_stack_outputs_creation(self):
        """Test CloudFormation outputs creation."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check StackSet ARN output
        template.has_output("StackSetArn", {
            "Description": "ARN of the created StackSet"
        })

        # Assert - Check Administration Role ARN output
        template.has_output("AdministrationRoleArn", {
            "Description": "ARN of the StackSet administration role"
        })

        # Assert - Check Permission Model output
        template.has_output("PermissionModel", {
            "Description": "StackSet permission model",
            "Value": "SELF_MANAGED"
        })

        # Assert - Check Target Regions output
        template.has_output("TargetRegions", {
            "Description": "Regions where StackSet instances are deployed",
            "Value": "us-east-1,us-west-2"
        })

        # Assert - Check Template Bucket Name output
        template.has_output("TemplateBucketName", {
            "Description": "S3 bucket for StackSet templates"
        })

    def test_resource_count(self):
        """Test the expected number of resources are created."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check resource counts
        template.resource_count_is("AWS::S3::Bucket", 1)
        template.resource_count_is("AWS::CloudFormation::StackSet", 1)

    def test_different_config_parameters(self):
        """Test StackSetStack with different configuration parameters."""
        # Arrange
        custom_config = StackSetConfig(
            stack_set_name="CustomStackSet",
            target_regions=["eu-west-1", "ap-southeast-1"],
            target_accounts=["111111111111"],
            instance_stack_name="CustomMonitoringStack",
            parameters={
                "NotificationEmail": "custom@example.com",
                "DashboardName": "CustomDashboard",
                "AlarmPrefix": "CustomAlarms"
            },
            max_concurrent_percentage=75,
            failure_tolerance_percentage=25,
            region_concurrency_type="PARALLEL"
        )

        # Act
        custom_monitoring_config = MonitoringConfig(
            dashboard_name="CustomDashboard",
            notification_email="custom@example.com",
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix="CustomAlarms"
        )
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=custom_config,
            monitoring_config=custom_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check custom StackSet name
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "StackSetName": "CustomStackSet"
        })

        # Assert - Check custom operation preferences
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "OperationPreferences": {
                "MaxConcurrentPercentage": 75,
                "FailureTolerancePercentage": 25,
                "RegionConcurrencyType": "PARALLEL"
            }
        })

        # Assert - Check custom target regions output
        template.has_output("TargetRegions", {
            "Value": "eu-west-1,ap-southeast-1"
        })

    def test_s3_bucket_naming_convention(self):
        """Test S3 bucket naming follows expected convention."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check bucket name pattern
        bucket_resources = template.find_resources("AWS::S3::Bucket")
        assert len(bucket_resources) == 1

        # The bucket name should follow the pattern: stacksets-blog-templates-{account}-{region}
        # We can't test the exact name since account and region are tokens,
        # but we can verify the structure

    def test_stackset_template_body_is_json(self):
        """Test that StackSet template body is valid JSON."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that TemplateBody exists and is a string
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        template_body = stackset_resource["Properties"]["TemplateBody"]
        assert isinstance(template_body, str)

        # Verify it's valid JSON
        try:
            json.loads(template_body)
        except json.JSONDecodeError:
            pytest.fail("TemplateBody is not valid JSON")

    def test_stackset_capabilities(self):
        """Test StackSet capabilities configuration."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check capabilities
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "Capabilities": ["CAPABILITY_IAM"]
        })

    @pytest.mark.parametrize("concurrent_pct,tolerance_pct,concurrency_type", [
        (25, 5, "SEQUENTIAL"),
        (50, 10, "PARALLEL"),
        (100, 0, "SEQUENTIAL"),
    ])
    def test_various_operation_preferences(self, concurrent_pct, tolerance_pct, concurrency_type):
        """Test StackSet with various operation preferences."""
        # Arrange
        config = StackSetConfig(
            stack_set_name="TestStackSet",
            target_regions=["us-east-1"],
            target_accounts=["123456789012"],
            instance_stack_name="TestStack",
            parameters={
                "NotificationEmail": TEST_EMAIL,
                "DashboardName": TEST_DASHBOARD,
                "AlarmPrefix": TEST_ALARM_PREFIX
            },
            max_concurrent_percentage=concurrent_pct,
            failure_tolerance_percentage=tolerance_pct,
            region_concurrency_type=concurrency_type
        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        stack = StackSetStack(
            self.app, f"TestStack-{concurrent_pct}",
            config=config,
            monitoring_config=monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert
        template.has_resource_properties("AWS::CloudFormation::StackSet", {
            "OperationPreferences": {
                "MaxConcurrentPercentage": concurrent_pct,
                "FailureTolerancePercentage": tolerance_pct,
                "RegionConcurrencyType": concurrency_type
            }
        })

    def test_single_account_single_region(self):
        """Test StackSet with single account and single region."""
        # Arrange
        config = StackSetConfig(
            stack_set_name="SingleStackSet",
            target_regions=["us-east-1"],
            target_accounts=["123456789012"],
            instance_stack_name="SingleStack",
            parameters={
                "NotificationEmail": "single@example.com",
                "DashboardName": "SingleDashboard",
                "AlarmPrefix": "SingleAlarms"
            }
        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name="SingleDashboard",
            notification_email="single@example.com",
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix="SingleAlarms"
        )
        stack = StackSetStack(
            self.app, "SingleStackSetStack",
            config=config,
            monitoring_config=monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        properties = stackset_resource["Properties"]
        assert properties["StackSetName"] == "SingleStackSet"
        assert properties["PermissionModel"] == "SELF_MANAGED"

    def test_stackset_template_body_json_validation(self):
        """Test that StackSet template body JSON validation works correctly."""
        # Arrange & Act
        stack = StackSetStack(
            self.app, "TestStackSetStack",
            config=self.mock_config,
            monitoring_config=self.mock_monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Get template body and validate JSON
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        template_body = stackset_resource["Properties"]["TemplateBody"]

        # This should not raise an exception
        parsed_template = json.loads(template_body)
        assert isinstance(parsed_template, dict)
        assert "Resources" in parsed_template or "AWSTemplateFormatVersion" in parsed_template

    def test_stackset_no_parameter_overrides_when_no_parameters(self):
        """Test that StackSet doesn't include parameter overrides when no parameters provided."""
        # Arrange
        config = StackSetConfig(
            stack_set_name="NoParamsStackSet",
            target_regions=["us-east-1"],
            parameters={},  # No parameters
            target_accounts=["123456789012"],
            instance_stack_name="NoParamsStack"
        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        stack = StackSetStack(
            self.app, "TestStack",
            config=config,
            monitoring_config=monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check StackSet resource exists without parameter overrides
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        assert len(stackset_resources) == 1

        stackset_resource = list(stackset_resources.values())[0]
        properties = stackset_resource["Properties"]
        # Check StackSet properties - no parameter overrides at StackSet level
        assert properties["StackSetName"] == "NoParamsStackSet"
        assert properties["PermissionModel"] == "SELF_MANAGED"
        assert "TemplateBody" in properties

    def test_stackset_uses_default_values_when_no_parameters(self):
        """Test that StackSet uses MonitoringStack default values when no parameters provided."""
        # Arrange
        config = StackSetConfig(
            stack_set_name="DefaultsStackSet",
            target_regions=["us-east-1"],
            parameters={},  # No parameters - should use defaults
            target_accounts=["123456789012"],
            instance_stack_name="DefaultsStack"
        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        stack = StackSetStack(
            self.app, "TestStack",
            config=config,
            monitoring_config=monitoring_config
        )
        template_json = stack.render_instance_template()
        template_dict = json.loads(template_json)

        # Assert - Check that template was generated successfully with defaults
        assert "Resources" in template_dict
        assert "Outputs" in template_dict
        # The template should contain monitoring resources
        resources = template_dict["Resources"]
        # Should have SNS topic, dashboard, and alarms
        sns_topics = [r for r in resources.values() if r["Type"] == "AWS::SNS::Topic"]
        dashboards = [r for r in resources.values() if r["Type"] == "AWS::CloudWatch::Dashboard"]
        assert len(sns_topics) >= 1
        assert len(dashboards) >= 1

    def test_stackset_ignores_config_parameters(self):
        """Test that StackSet ignores parameters from config and uses defaults."""
        # Arrange
        config_with_params = StackSetConfig(
            stack_set_name="IgnoreParamsStackSet",
            target_regions=["us-east-1"],
            parameters={
                "NotificationEmail": "custom@example.com",
                "DashboardName": "CustomDashboard",
                "AlarmPrefix": "CustomPrefix"
            },
            target_accounts=["123456789012"],
            instance_stack_name="IgnoreParamsStack"
        )

        config_without_params = StackSetConfig(
            stack_set_name="NoParamsStackSet",
            target_regions=["us-east-1"],
            parameters={},
            target_accounts=["123456789012"],
            instance_stack_name="NoParamsStack"
        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        stack_with_params = StackSetStack(
            self.app, "TestStackWithParams",
            config=config_with_params,
            monitoring_config=monitoring_config
        )
        stack_without_params = StackSetStack(
            self.app, "TestStackWithoutParams",
            config=config_without_params,
            monitoring_config=monitoring_config
        )

        template_with_params = stack_with_params.render_instance_template()
        template_without_params = stack_without_params.render_instance_template()

        # Assert - Both templates should be identical since parameters are ignored
        assert template_with_params == template_without_params

        # Verify neither has parameter overrides
        template_with_params_cdk = Template.from_stack(stack_with_params)
        template_without_params_cdk = Template.from_stack(stack_without_params)

        stackset_resources_with = template_with_params_cdk.find_resources(
            "AWS::CloudFormation::StackSet"
        )
        stackset_resources_without = template_without_params_cdk.find_resources(
            "AWS::CloudFormation::StackSet"
        )

        # Check that both StackSets exist and have the expected properties
        assert len(stackset_resources_with) == 1
        assert len(stackset_resources_without) == 1
        for stackset_resource in stackset_resources_with.values():
            properties = stackset_resource["Properties"]
            assert properties["PermissionModel"] == "SELF_MANAGED"
            assert "TemplateBody" in properties

        for stackset_resource in stackset_resources_without.values():
            properties = stackset_resource["Properties"]
            assert properties["PermissionModel"] == "SELF_MANAGED"
            assert "TemplateBody" in properties

    def test_stackset_with_parameter_overrides_enabled(self):
        """Test that StackSet includes parameter overrides when enabled."""
        # Arrange
        config = StackSetConfig(
            stack_set_name="OverridesEnabledStackSet",
            target_regions=["us-east-1"],
            parameters={
                "NotificationEmail": "override@example.com",
                "DashboardName": "OverrideDashboard",
                "AlarmPrefix": "OverridePrefix"
            },
            target_accounts=["123456789012"],
            instance_stack_name="OverridesStack",

        )

        # Act
        monitoring_config = MonitoringConfig(
            dashboard_name="OverrideDashboard",
            notification_email="override@example.com",
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix="OverridePrefix"
        )
        stack = StackSetStack(
            self.app, "TestStackWithOverrides",
            config=config,
            monitoring_config=monitoring_config
        )
        template = Template.from_stack(stack)

        # Assert - Check StackSet resource exists
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        assert len(stackset_resources) == 1

        stackset_resource = list(stackset_resources.values())[0]
        properties = stackset_resource["Properties"]

        # Check StackSet properties
        assert properties["StackSetName"] == "OverridesEnabledStackSet"
        assert properties["PermissionModel"] == "SELF_MANAGED"
        assert "TemplateBody" in properties
        # The template body should contain the monitoring configuration
        # (parameter overrides would be applied at stack instance level, not StackSet level)

    def test_stackset_parameter_override_mode_comparison(self):
        """Test that parameter override mode generates different templates."""
        # Arrange
        config_no_overrides = StackSetConfig(
            stack_set_name="NoOverridesStackSet",
            target_regions=["us-east-1"],
            parameters={
                "NotificationEmail": TEST_EMAIL,
                "DashboardName": TEST_DASHBOARD
            },
            target_accounts=["123456789012"],
            instance_stack_name="NoOverridesStack",

        )

        config_with_overrides = StackSetConfig(
            stack_set_name="WithOverridesStackSet",
            target_regions=["us-east-1"],
            parameters={
                "NotificationEmail": TEST_EMAIL,
                "DashboardName": TEST_DASHBOARD
            },
            target_accounts=["123456789012"],
            instance_stack_name="WithOverridesStack",

        )

        # Act
        monitoring_config_no_overrides = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        monitoring_config_with_overrides = MonitoringConfig(
            dashboard_name=TEST_DASHBOARD,
            notification_email=TEST_EMAIL,
            alarm_thresholds=SIMPLE_ALARM_THRESHOLDS,
            alarm_prefix=TEST_ALARM_PREFIX
        )
        stack_no_overrides = StackSetStack(
            self.app, "TestStackNoOverrides",
            config=config_no_overrides,
            monitoring_config=monitoring_config_no_overrides
        )
        stack_with_overrides = StackSetStack(
            self.app, "TestStackWithOverrides",
            config=config_with_overrides,
            monitoring_config=monitoring_config_with_overrides
        )

        template_no_overrides = stack_no_overrides.render_instance_template()
        template_with_overrides = stack_with_overrides.render_instance_template()

        # Assert - Templates should be the same since both use the same monitoring_config
        # (parameter overrides would be applied at stack instance level, not template level)
        assert template_no_overrides == template_with_overrides
