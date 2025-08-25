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
from stacksets_blog.config import StackSetConfig
from tests.conftest import STACKSET_CONFIG_PARAMS

# pylint: disable=duplicate-code

class TestStackSetStack:
    """Test suite for StackSetStack class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = App()  # pylint: disable=attribute-defined-outside-init
        # pylint: disable=attribute-defined-outside-init
        self.mock_config = StackSetConfig(**STACKSET_CONFIG_PARAMS)

    def test_stackset_stack_creation(self):
        """Test StackSetStack creation with valid configuration."""
        # Arrange & Act
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
        template = Template.from_stack(stack)

        # Assert - Check stack instances
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        stack_instances_group = stackset_resource["Properties"]["StackInstancesGroup"]
        assert len(stack_instances_group) == 1

        stack_instance = stack_instances_group[0]
        assert stack_instance["DeploymentTargets"]["Accounts"] == ["123456789012", "123456789013"]
        assert stack_instance["Regions"] == ["us-east-1", "us-west-2"]

    def test_administration_role_arn_format(self):
        """Test administration role ARN format."""
        # Arrange & Act
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)

        # Assert - Check ARN structure (may contain CDK tokens)
        arn = stack.administration_role_arn
        assert arn.startswith("arn:aws:iam::")
        assert arn.endswith(":role/AWSCloudFormationStackSetAdministrationRole")
        # The middle part may contain CDK tokens like ${Token[AWS.AccountId.3]}
        assert "role/AWSCloudFormationStackSetAdministrationRole" in arn

    def test_template_bucket_attributes(self):
        """Test S3 template bucket attributes."""
        # Arrange & Act
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)

        # Assert
        assert stack.template_bucket is not None
        assert hasattr(stack.template_bucket, 'bucket_name')

    def test_stackset_attributes(self):
        """Test StackSet resource attributes."""
        # Arrange & Act
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)

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
            stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)

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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=custom_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
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
                "NotificationEmail": "test@example.com",
                "DashboardName": "TestDashboard",
                "AlarmPrefix": "TestAlarms"
            },
            max_concurrent_percentage=concurrent_pct,
            failure_tolerance_percentage=tolerance_pct,
            region_concurrency_type=concurrency_type
        )

        # Act
        stack = StackSetStack(self.app, f"TestStack-{concurrent_pct}", config=config)
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
        stack = StackSetStack(self.app, "SingleStackSetStack", config=config)
        template = Template.from_stack(stack)

        # Assert
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        stack_instance = stackset_resource["Properties"]["StackInstancesGroup"][0]
        assert stack_instance["DeploymentTargets"]["Accounts"] == ["123456789012"]
        assert stack_instance["Regions"] == ["us-east-1"]

    def test_stackset_template_body_json_validation(self):
        """Test that StackSet template body JSON validation works correctly."""
        # Arrange & Act
        stack = StackSetStack(self.app, "TestStackSetStack", config=self.mock_config)
        template = Template.from_stack(stack)

        # Assert - Get template body and validate JSON
        stackset_resources = template.find_resources("AWS::CloudFormation::StackSet")
        stackset_resource = list(stackset_resources.values())[0]

        template_body = stackset_resource["Properties"]["TemplateBody"]

        # This should not raise an exception
        parsed_template = json.loads(template_body)
        assert isinstance(parsed_template, dict)
        assert "Resources" in parsed_template or "AWSTemplateFormatVersion" in parsed_template
