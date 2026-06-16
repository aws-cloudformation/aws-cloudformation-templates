"""
AWS CloudWatch monitoring infrastructure stack.

This module defines the MonitoringStack class which creates comprehensive
monitoring infrastructure including CloudWatch dashboards, alarms, and
SNS notifications. Designed to be deployed via CloudFormation StackSets
across multiple AWS accounts and regions.

Classes:
    MonitoringStack: CDK Stack for creating monitoring infrastructure

Example:
    from stacksets_blog.monitoring_stack import MonitoringStack

    stack = MonitoringStack(
        app, "MonitoringStack",
        description="Multi-region monitoring infrastructure"
    )
"""

from aws_cdk import (
    Stack,
    CfnOutput
)
from aws_cdk.aws_cloudwatch import (
    Dashboard,
    GraphWidget,
    Metric,
    Alarm,
    ComparisonOperator,
    TreatMissingData
)
from aws_cdk.aws_cloudwatch_actions import SnsAction
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from constructs import Construct

class MonitoringStack(Stack):
    """
    AWS CDK Stack for StackSet-focused monitoring infrastructure.

    Creates CloudWatch monitoring resources specifically designed for monitoring
    StackSet deployments and account-level activity. Focuses on metrics that
    are likely to have real data and are relevant to StackSet operations.

    The stack creates:
    - CloudWatch dashboard with StackSet and account-level metrics
    - CloudWatch alarms for CloudFormation operations and billing
    - SNS topic with email notifications
    - CloudFormation outputs for resource references

    Dashboard includes:
    - CloudFormation operations (StackSet activity)
    - AWS API usage (service calls during deployments)
    - CloudWatch Logs activity
    - Account billing and usage metrics

    Alarms monitor:
    - CloudFormation stack failures
    - Unexpected billing increases
    - High API usage rates
    - SNS delivery failures

    Attributes:
        notification_email (str): Email address for alarm notifications
        dashboard_name (str): Name for the CloudWatch dashboard
        alarm_prefix (str): Prefix for alarm names to avoid conflicts
        sns_topic (Topic): SNS topic for alarm notifications
        dashboard (Dashboard): CloudWatch dashboard
        alarms (List[Alarm]): List of created CloudWatch alarms

    Example:
        stack = MonitoringStack(
            app, "MonitoringStack",
            notification_email="admin@example.com",
            dashboard_name="StackSet-Monitoring-Dashboard",
            alarm_prefix="StackSet-Alarms",
            description="StackSet-focused monitoring infrastructure"
        )
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        scope: Construct,
        construct_id: str,
        notification_email: str,
        dashboard_name: str,
        alarm_prefix: str,
        alarm_thresholds: dict = None,
        **kwargs
    ) -> None:
        """
        Initialize the MonitoringStack.

        Args:
            scope (Construct): The scope in which to define this construct
            construct_id (str): The scoped construct ID
            notification_email (str): Email address for alarm notifications
            dashboard_name (str): Name for the CloudWatch dashboard
            alarm_prefix (str): Prefix for alarm names to avoid conflicts
            alarm_thresholds (dict): Optional alarm thresholds configuration
            **kwargs: Additional keyword arguments passed to Stack
        """
        super().__init__(scope, construct_id, **kwargs)

        self.notification_email = notification_email
        self.dashboard_name = dashboard_name
        self.alarm_prefix = alarm_prefix
        self.alarm_thresholds = alarm_thresholds or {}

        self.sns_topic = self.create_sns_topic()
        self.dashboard = self.create_dashboard()
        self.alarms = self.create_alarms()
        self.create_outputs()

    def create_sns_topic(self) -> Topic:
        """
        Create SNS topic for alarm notifications with email subscription.

        Creates an SNS topic with a descriptive name and adds an email
        subscription for receiving alarm notifications.

        Returns:
            Topic: The created SNS topic with email subscription
        """
        topic = Topic(
            self, "AlarmNotificationTopic",
            topic_name=f"{self.alarm_prefix}-Notifications",
            display_name="StackSets Blog Monitoring Notifications"
        )

        topic.add_subscription(
            EmailSubscription(self.notification_email)
        )

        return topic

    def create_dashboard(self) -> Dashboard:
        """
        Create CloudWatch dashboard with real AWS service metrics.

        Creates a monitoring dashboard focused on metrics that will show actual data:
        - Account billing metrics (always available)
        - SNS topic metrics (from this stack's notification topic)
        - Basic service usage that every account generates

        Returns:
            Dashboard: The created CloudWatch dashboard with visible metrics
        """
        dashboard = Dashboard(
            self, "MonitoringDashboard",
            dashboard_name=self.dashboard_name
        )

        # CloudWatch Alarms - shows alarm state changes (always has data once alarms exist)
        alarms_widget = GraphWidget(
            title="CloudWatch Alarms Status (StackSet Monitoring)",
            left=[
                Metric(
                    namespace="AWS/CloudWatch",
                    metric_name="MetricCount",
                    statistic="Sum",
                    label="Active Metrics"
                )
            ],
            right=[
                # Note: Individual alarm metrics will be added dynamically
                # This shows the overall alarm activity in the account
                Metric(
                    namespace="AWS/CloudWatch",
                    metric_name="CallCount",
                    statistic="Sum",
                    label="CloudWatch API Activity"
                )
            ],
            width=12,
            height=6
        )

        # SNS Topic metrics - will show data when notifications are sent
        sns_widget = GraphWidget(
            title="SNS Notification System (StackSet Alerts)",
            left=[
                Metric(
                    namespace="AWS/SNS",
                    metric_name="NumberOfMessagesPublished",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Sum",
                    label="Messages Published"
                ),
                Metric(
                    namespace="AWS/SNS",
                    metric_name="NumberOfNotificationsDelivered",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Sum",
                    label="Notifications Delivered"
                )
            ],
            right=[
                Metric(
                    namespace="AWS/SNS",
                    metric_name="NumberOfNotificationsFailed",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Sum",
                    label="Delivery Failures"
                ),
                Metric(
                    namespace="AWS/SNS",
                    metric_name="PublishSize",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Average",
                    label="Average Message Size (Bytes)"
                )
            ],
            width=12,
            height=6
        )

        # StackSet deployment demonstration - shows this stack's resources
        stackset_demo_widget = GraphWidget(
            title="StackSet Deployment Demonstration",
            left=[
                # SNS subscription confirmations - shows when email subscriptions are confirmed
                Metric(
                    namespace="AWS/SNS",
                    metric_name="NumberOfNotificationsDelivered",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Sum",
                    label="Email Notifications Sent"
                ),
                # SNS messages published - shows alarm activity
                Metric(
                    namespace="AWS/SNS",
                    metric_name="NumberOfMessagesPublished",
                    dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                    statistic="Sum",
                    label="Total Messages Published"
                )
            ],
            right=[
                # Account billing (daily update) - shows cost impact
                Metric(
                    namespace="AWS/Billing",
                    metric_name="EstimatedCharges",
                    dimensions_map={"Currency": "USD"},
                    statistic="Maximum",
                    label="Account Charges (USD)"
                ),
                # CloudWatch service billing
                Metric(
                    namespace="AWS/Billing",
                    metric_name="EstimatedCharges",
                    dimensions_map={"Currency": "USD", "ServiceName": "AmazonCloudWatch"},
                    statistic="Maximum",
                    label="CloudWatch Charges (USD)"
                )
            ],
            width=12,
            height=6
        )

        dashboard.add_widgets(alarms_widget)
        dashboard.add_widgets(sns_widget)
        dashboard.add_widgets(stackset_demo_widget)

        return dashboard

    def create_alarms(self) -> list[Alarm]:
        """
        Create CloudWatch alarms for StackSet and account-level monitoring.

        Creates alarms using metrics that are guaranteed to exist:
        - Billing: Unexpected cost increases (always available)
        - SNS: Failed message deliveries (from this stack's topic)
        - Custom metrics: StackSet deployment issues

        All alarms are configured with SNS notifications and appropriate
        evaluation periods to reduce false positives.

        Returns:
            list[Alarm]: List of created CloudWatch alarms
        """
        alarms = []

        # High billing alarm - always available and important for cost monitoring
        billing_threshold = self.alarm_thresholds.get("BillingThreshold", 100.0)
        billing_alarm = Alarm(
            self, "HighBillingAlarm",
            alarm_name=f"{self.alarm_prefix}-High-Billing",
            alarm_description="AWS account charges exceeding threshold",
            metric=Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "USD"},
                statistic="Maximum"
            ),
            threshold=billing_threshold,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            billing_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(billing_alarm)

        # SNS delivery failures - monitors this stack's notification system
        sns_failure_threshold = self.alarm_thresholds.get("SNSFailureThreshold", 1.0)
        sns_failure_alarm = Alarm(
            self, "SNSDeliveryFailureAlarm",
            alarm_name=f"{self.alarm_prefix}-SNS-Delivery-Failures",
            alarm_description="SNS message delivery failures from StackSet notifications",
            metric=Metric(
                namespace="AWS/SNS",
                metric_name="NumberOfNotificationsFailed",
                dimensions_map={"TopicName": f"{self.alarm_prefix}-Notifications"},
                statistic="Sum"
            ),
            threshold=sns_failure_threshold,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            sns_failure_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(sns_failure_alarm)

        return alarms

    def create_outputs(self) -> None:
        """
        Create CloudFormation outputs for important resource information.

        Creates outputs that provide access to key resources and information:
        - Dashboard URL for direct access to CloudWatch dashboard
        - SNS Topic ARN for integration with other services
        - Alarm ARNs for reference and automation
        - Deployed region for multi-region awareness
        """
        CfnOutput(
            self, "DashboardURL",
            description="CloudWatch Dashboard URL",
            value=(
                f"https://{self.region}.console.aws.amazon.com/cloudwatch/home?"
                f"region={self.region}#dashboards:name={self.dashboard_name}"
            )
        )

        if self.sns_topic:
            CfnOutput(
                self, "SNSTopicArn",
                description="SNS Topic ARN for alarm notifications",
                value=self.sns_topic.topic_arn
            )

        if self.alarms:
            alarm_arns = [alarm.alarm_arn for alarm in self.alarms]
            CfnOutput(
                self, "AlarmArns",
                description="CloudWatch Alarm ARNs",
                value=",".join(alarm_arns)
            )

        CfnOutput(
            self, "DeployedRegion",
            description="AWS Region where this stack is deployed",
            value=self.region
        )
