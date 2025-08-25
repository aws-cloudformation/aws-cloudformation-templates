"""
Unit tests for MonitoringStack.

This module contains comprehensive unit tests for the MonitoringStack class,
testing all aspects of the monitoring infrastructure creation including
CloudWatch dashboards, alarms, SNS topics, and outputs.
"""

from unittest.mock import patch

import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from stacksets_blog.monitoring_stack import MonitoringStack


class TestMonitoringStack:
    """Test suite for MonitoringStack class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = App()  # pylint: disable=attribute-defined-outside-init

    def test_monitoring_stack_creation_with_defaults(self):
        """Test MonitoringStack creation with default parameters."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check stack attributes
        assert stack.notification_email == "admin@example.com"
        assert stack.dashboard_name == "StackSets-Blog-Dashboard"
        assert stack.alarm_prefix == "StackSets-Blog"

        # Assert - Check SNS topic creation
        template.has_resource_properties("AWS::SNS::Topic", {
            "TopicName": "StackSets-Blog-Notifications",
            "DisplayName": "StackSets Blog Monitoring Notifications"
        })

        # Assert - Check email subscription
        template.has_resource_properties("AWS::SNS::Subscription", {
            "Protocol": "email",
            "Endpoint": "admin@example.com"
        })

    def test_monitoring_stack_creation_with_custom_parameters(self):
        """Test MonitoringStack creation with custom parameters."""
        # Arrange
        custom_email = "test@example.com"
        custom_dashboard = "CustomDashboard"
        custom_prefix = "CustomAlarms"

        # Act
        stack = MonitoringStack(
            self.app, "TestMonitoringStack",
            notification_email=custom_email,
            dashboard_name=custom_dashboard,
            alarm_prefix=custom_prefix
        )
        template = Template.from_stack(stack)

        # Assert - Check stack attributes
        assert stack.notification_email == custom_email
        assert stack.dashboard_name == custom_dashboard
        assert stack.alarm_prefix == custom_prefix

        # Assert - Check SNS topic with custom prefix
        template.has_resource_properties("AWS::SNS::Topic", {
            "TopicName": f"{custom_prefix}-Notifications"
        })

        # Assert - Check email subscription with custom email
        template.has_resource_properties("AWS::SNS::Subscription", {
            "Endpoint": custom_email
        })

    def test_cloudwatch_dashboard_creation(self):
        """Test CloudWatch dashboard creation."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check dashboard creation
        template.has_resource_properties("AWS::CloudWatch::Dashboard", {
            "DashboardName": "StackSets-Blog-Dashboard"
        })

        # Assert - Check dashboard resource exists
        dashboard_resources = template.find_resources("AWS::CloudWatch::Dashboard")
        assert len(dashboard_resources) == 1

        # Assert - Check dashboard body is properly structured (it's a CloudFormation function)
        dashboard_body = list(dashboard_resources.values())[0]["Properties"]["DashboardBody"]
        assert dashboard_body is not None
        # The dashboard body is a CloudFormation Fn::Join function, so we check its structure
        assert isinstance(dashboard_body, (dict, str))

    def test_cloudwatch_alarms_creation(self):
        """Test CloudWatch alarms creation."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check EC2 CPU alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": "StackSets-Blog-EC2-HighCPU",
            "AlarmDescription": "EC2 instances with high CPU utilization",
            "MetricName": "CPUUtilization",
            "Namespace": "AWS/EC2",
            "Statistic": "Average",
            "Threshold": 80,
            "ComparisonOperator": "GreaterThanThreshold"
        })

        # Assert - Check RDS CPU alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": "StackSets-Blog-RDS-HighCPU",
            "AlarmDescription": "RDS instances with high CPU utilization",
            "MetricName": "CPUUtilization",
            "Namespace": "AWS/RDS",
            "Threshold": 75
        })

        # Assert - Check RDS storage alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": "StackSets-Blog-RDS-LowStorage",
            "AlarmDescription": "RDS instances with low free storage space",
            "MetricName": "FreeStorageSpace",
            "Namespace": "AWS/RDS",
            "Threshold": 2000000000,
            "ComparisonOperator": "LessThanThreshold"
        })

        # Assert - Check Lambda error alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": "StackSets-Blog-Lambda-Errors",
            "AlarmDescription": "Lambda functions with high error rate",
            "MetricName": "Errors",
            "Namespace": "AWS/Lambda",
            "Threshold": 5
        })

        # Assert - Check Lambda duration alarm
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": "StackSets-Blog-Lambda-Duration",
            "AlarmDescription": "Lambda functions with high execution duration",
            "MetricName": "Duration",
            "Namespace": "AWS/Lambda",
            "Threshold": 30000
        })

    def test_alarm_actions_configuration(self):
        """Test that alarms are configured with SNS actions."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check that alarms have SNS actions
        alarm_resources = template.find_resources("AWS::CloudWatch::Alarm")

        for alarm_resource in alarm_resources.values():
            alarm_actions = alarm_resource["Properties"].get("AlarmActions", [])
            assert len(alarm_actions) > 0, "Alarm should have at least one action"

    def test_stack_outputs_creation(self):
        """Test CloudFormation outputs creation."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check dashboard URL output
        template.has_output("DashboardURL", {
            "Description": "CloudWatch Dashboard URL"
        })

        # Assert - Check SNS topic ARN output
        template.has_output("SNSTopicArn", {
            "Description": "SNS Topic ARN for alarm notifications"
        })

        # Assert - Check alarm ARNs output
        template.has_output("AlarmArns", {
            "Description": "CloudWatch Alarm ARNs"
        })

        # Assert - Check deployed region output
        template.has_output("DeployedRegion", {
            "Description": "AWS Region where this stack is deployed"
        })

    def test_sns_topic_attributes(self):
        """Test SNS topic attributes and configuration."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")

        # Assert - Check SNS topic object
        assert stack.sns_topic is not None
        assert hasattr(stack.sns_topic, 'topic_arn')

    def test_dashboard_attributes(self):
        """Test CloudWatch dashboard attributes."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")

        # Assert - Check dashboard object
        assert stack.dashboard is not None

    def test_alarms_list_attributes(self):
        """Test CloudWatch alarms list attributes."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")

        # Assert - Check alarms list
        assert stack.alarms is not None
        assert isinstance(stack.alarms, list)
        # EC2 CPU, RDS CPU, RDS Storage, Lambda Errors, Lambda Duration
        assert len(stack.alarms) == 5

    def test_custom_alarm_prefix_in_alarm_names(self):
        """Test that custom alarm prefix is used in alarm names."""
        # Arrange
        custom_prefix = "TestPrefix"

        # Act
        stack = MonitoringStack(
            self.app, "TestMonitoringStack",
            alarm_prefix=custom_prefix
        )
        template = Template.from_stack(stack)

        # Assert - Check that all alarms use the custom prefix
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": f"{custom_prefix}-EC2-HighCPU"
        })
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": f"{custom_prefix}-RDS-HighCPU"
        })
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": f"{custom_prefix}-RDS-LowStorage"
        })
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": f"{custom_prefix}-Lambda-Errors"
        })
        template.has_resource_properties("AWS::CloudWatch::Alarm", {
            "AlarmName": f"{custom_prefix}-Lambda-Duration"
        })

    def test_resource_count(self):
        """Test the expected number of resources are created."""
        # Arrange & Act
        stack = MonitoringStack(self.app, "TestMonitoringStack")
        template = Template.from_stack(stack)

        # Assert - Check resource counts
        template.resource_count_is("AWS::SNS::Topic", 1)
        template.resource_count_is("AWS::SNS::Subscription", 1)
        template.resource_count_is("AWS::CloudWatch::Dashboard", 1)
        template.resource_count_is("AWS::CloudWatch::Alarm", 5)

    def test_stack_description(self):
        """Test stack description when provided."""
        # Arrange
        description = "Test monitoring infrastructure"

        # Act
        stack = MonitoringStack(
            self.app, "TestMonitoringStack",
            description=description
        )

        # Assert
        assert stack.stack_name == "TestMonitoringStack"

    @pytest.mark.parametrize("email,dashboard,prefix", [
        ("user1@test.com", "Dashboard1", "Prefix1"),
        ("user2@test.com", "Dashboard2", "Prefix2"),
        ("admin@company.com", "ProductionDashboard", "ProdAlarms"),
    ])
    def test_monitoring_stack_with_various_parameters(self, email, dashboard, prefix):
        """Test MonitoringStack with various parameter combinations."""
        # Arrange & Act
        stack = MonitoringStack(
            self.app, f"TestStack-{prefix}",
            notification_email=email,
            dashboard_name=dashboard,
            alarm_prefix=prefix
        )
        template = Template.from_stack(stack)

        # Assert
        assert stack.notification_email == email
        assert stack.dashboard_name == dashboard
        assert stack.alarm_prefix == prefix

        # Check SNS subscription uses correct email
        template.has_resource_properties("AWS::SNS::Subscription", {
            "Endpoint": email
        })

        # Check dashboard uses correct name
        template.has_resource_properties("AWS::CloudWatch::Dashboard", {
            "DashboardName": dashboard
        })

    def test_monitoring_stack_without_sns_topic(self):
        """Test MonitoringStack behavior when sns_topic is None."""
        # Arrange - Mock the create_sns_topic method to return None
        with patch.object(MonitoringStack, 'create_sns_topic', return_value=None):
            # Act - Create stack with mocked sns_topic as None
            test_app = App()
            stack = MonitoringStack(test_app, "TestMonitoringStackNoSNS")

            # Assert - Stack should still be created successfully
            assert stack.sns_topic is None
            assert len(stack.alarms) == 5  # Should still create all alarms

            # Verify alarms are created properly even without SNS topic
            for alarm in stack.alarms:
                assert hasattr(alarm, 'alarm_name')
                # The alarm_name might contain CDK tokens, so just check it exists
                assert alarm.alarm_name is not None

    def test_monitoring_stack_without_alarms(self):
        """Test MonitoringStack behavior when alarms list is empty."""
        # Arrange - Mock the create_alarms method to return empty list
        with patch.object(MonitoringStack, 'create_alarms', return_value=[]):
            # Act - Create stack with mocked empty alarms list
            test_app = App()
            stack = MonitoringStack(test_app, "TestMonitoringStackNoAlarms")

            # Assert - Stack should still be created successfully
            assert len(stack.alarms) == 0

            # Check that outputs are still created (testing the if self.alarms branch)
            template = Template.from_stack(stack)

            # Should still have other outputs even without alarms
            template.has_output("DashboardURL", {
                "Description": "CloudWatch Dashboard URL"
            })
            template.has_output("DeployedRegion", {
                "Description": "AWS Region where this stack is deployed"
            })
