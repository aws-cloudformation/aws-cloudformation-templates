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
    AWS CDK Stack for comprehensive monitoring infrastructure.

    Creates CloudWatch monitoring resources including dashboards, alarms,
    and SNS notifications for EC2, RDS, and Lambda services. Designed for
    deployment via CloudFormation StackSets across multiple accounts and regions.

    The stack creates:
    - CloudWatch dashboard with service metrics widgets
    - CloudWatch alarms for critical thresholds
    - SNS topic with email notifications
    - CloudFormation outputs for resource references

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
            dashboard_name="MyDashboard",
            alarm_prefix="MyAlarms",
            description="Multi-region monitoring infrastructure"
        )
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        scope: Construct,
        construct_id: str,
        notification_email: str = "admin@example.com",
        dashboard_name: str = "StackSets-Blog-Dashboard",
        alarm_prefix: str = "StackSets-Blog",
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
            **kwargs: Additional keyword arguments passed to Stack
        """
        super().__init__(scope, construct_id, **kwargs)

        self.notification_email = notification_email
        self.dashboard_name = dashboard_name
        self.alarm_prefix = alarm_prefix

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
        Create CloudWatch dashboard with widgets for EC2, RDS, and Lambda metrics.

        Creates a comprehensive monitoring dashboard with three main widgets:
        - EC2 metrics: CPU utilization and network traffic
        - RDS metrics: CPU utilization, connections, and storage
        - Lambda metrics: Duration, invocations, errors, and throttles

        Returns:
            Dashboard: The created CloudWatch dashboard
        """
        dashboard = Dashboard(
            self, "MonitoringDashboard",
            dashboard_name=self.dashboard_name
        )

        ec2_widget = GraphWidget(
            title="EC2 Metrics",
            left=[
                Metric(
                    namespace="AWS/EC2",
                    metric_name="CPUUtilization",
                    statistic="Average"
                )
            ],
            right=[
                Metric(
                    namespace="AWS/EC2",
                    metric_name="NetworkIn",
                    statistic="Sum"
                ),
                Metric(
                    namespace="AWS/EC2",
                    metric_name="NetworkOut",
                    statistic="Sum"
                )
            ],
            width=12,
            height=6
        )

        rds_widget = GraphWidget(
            title="RDS Metrics",
            left=[
                Metric(
                    namespace="AWS/RDS",
                    metric_name="CPUUtilization",
                    statistic="Average"
                ),
                Metric(
                    namespace="AWS/RDS",
                    metric_name="DatabaseConnections",
                    statistic="Average"
                )
            ],
            right=[
                Metric(
                    namespace="AWS/RDS",
                    metric_name="FreeStorageSpace",
                    statistic="Average"
                )
            ],
            width=12,
            height=6
        )

        lambda_widget = GraphWidget(
            title="Lambda Metrics",
            left=[
                Metric(
                    namespace="AWS/Lambda",
                    metric_name="Duration",
                    statistic="Average"
                ),
                Metric(
                    namespace="AWS/Lambda",
                    metric_name="Invocations",
                    statistic="Sum"
                )
            ],
            right=[
                Metric(
                    namespace="AWS/Lambda",
                    metric_name="Errors",
                    statistic="Sum"
                ),
                Metric(
                    namespace="AWS/Lambda",
                    metric_name="Throttles",
                    statistic="Sum"
                )
            ],
            width=12,
            height=6
        )

        dashboard.add_widgets(ec2_widget)
        dashboard.add_widgets(rds_widget)
        dashboard.add_widgets(lambda_widget)

        return dashboard

    def create_alarms(self) -> list[Alarm]:
        """
        Create CloudWatch alarms for critical metrics with configurable thresholds.

        Creates comprehensive alarms for monitoring EC2, RDS, and Lambda services:
        - EC2: High CPU utilization (>80%)
        - RDS: High CPU utilization (>75%) and low storage space (<2GB)
        - Lambda: High error rate (>5 errors) and long duration (>30 seconds)

        All alarms are configured with SNS notifications and appropriate
        evaluation periods to reduce false positives.

        Returns:
            list[Alarm]: List of created CloudWatch alarms
        """
        alarms = []

        ec2_cpu_alarm = Alarm(
            self, "EC2HighCPUAlarm",
            alarm_name=f"{self.alarm_prefix}-EC2-HighCPU",
            alarm_description="EC2 instances with high CPU utilization",
            metric=Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                statistic="Average"
            ),
            threshold=80,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            ec2_cpu_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(ec2_cpu_alarm)

        rds_cpu_alarm = Alarm(
            self, "RDSHighCPUAlarm",
            alarm_name=f"{self.alarm_prefix}-RDS-HighCPU",
            alarm_description="RDS instances with high CPU utilization",
            metric=Metric(
                namespace="AWS/RDS",
                metric_name="CPUUtilization",
                statistic="Average"
            ),
            threshold=75,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            rds_cpu_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(rds_cpu_alarm)

        rds_storage_alarm = Alarm(
            self, "RDSLowStorageAlarm",
            alarm_name=f"{self.alarm_prefix}-RDS-LowStorage",
            alarm_description="RDS instances with low free storage space",
            metric=Metric(
                namespace="AWS/RDS",
                metric_name="FreeStorageSpace",
                statistic="Average"
            ),
            threshold=2000000000,
            evaluation_periods=1,
            comparison_operator=ComparisonOperator.LESS_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            rds_storage_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(rds_storage_alarm)

        lambda_error_alarm = Alarm(
            self, "LambdaErrorAlarm",
            alarm_name=f"{self.alarm_prefix}-Lambda-Errors",
            alarm_description="Lambda functions with high error rate",
            metric=Metric(
                namespace="AWS/Lambda",
                metric_name="Errors",
                statistic="Sum"
            ),
            threshold=5,
            evaluation_periods=2,
            datapoints_to_alarm=1,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            lambda_error_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(lambda_error_alarm)

        lambda_duration_alarm = Alarm(
            self, "LambdaDurationAlarm",
            alarm_name=f"{self.alarm_prefix}-Lambda-Duration",
            alarm_description="Lambda functions with high execution duration",
            metric=Metric(
                namespace="AWS/Lambda",
                metric_name="Duration",
                statistic="Average"
            ),
            threshold=30000,
            evaluation_periods=3,
            datapoints_to_alarm=2,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=TreatMissingData.NOT_BREACHING
        )

        if self.sns_topic:
            lambda_duration_alarm.add_alarm_action(SnsAction(self.sns_topic))
        alarms.append(lambda_duration_alarm)

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
