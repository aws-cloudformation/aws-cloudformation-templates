"""
AWS CloudFormation StackSet management stack.

This module defines the StackSetStack class which creates and manages
CloudFormation StackSets for deploying monitoring infrastructure across
multiple AWS accounts and regions. Uses SELF_MANAGED permission model
with pre-deployed IAM roles.

Classes:
    StackSetStack: CDK Stack for creating and managing CloudFormation StackSets

Example:
    from stacksets_blog.stackset_stack import StackSetStack
    from stacksets_blog.config import StackSetConfig

    config = StackSetConfig(...)
    stack = StackSetStack(app, "StackSetStack", config=config)
"""

import json
from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    App
)
from aws_cdk.aws_cloudformation import CfnStackSet
from aws_cdk.aws_s3 import (
    Bucket,
    BucketEncryption,
    BlockPublicAccess
)
# from aws_cdk.aws_iam import (
#     PolicyStatement,
#     Effect,
#     AnyPrincipal
# )
from cdk_nag import NagSuppressions
from constructs import Construct
from .config import StackSetConfig
from .monitoring_stack import MonitoringStack

class StackSetStack(Stack):
    """
    AWS CDK Stack for creating and managing CloudFormation StackSets.

    This stack creates a CloudFormation StackSet that deploys monitoring
    infrastructure across multiple AWS accounts and regions. Uses the
    SELF_MANAGED permission model with pre-deployed IAM administration
    and execution roles.

    The stack creates:
    - S3 bucket for storing StackSet templates
    - CloudFormation StackSet with monitoring template
    - Stack instances deployed to target accounts and regions
    - CloudFormation outputs for StackSet information

    Attributes:
        config (StackSetConfig): Configuration object with StackSet parameters
        administration_role_arn (str): ARN of the pre-deployed administration role
        template_bucket (Bucket): S3 bucket for StackSet templates
        stackset (CfnStackSet): The CloudFormation StackSet resource

    Example:
        config = StackSetConfig(
            stack_set_name="MyStackSet",
            target_regions=["us-east-1", "us-west-2"],
            target_accounts=["123456789012", "123456789013"],
            parameters={"Email": "admin@example.com"}
        )
        stack = StackSetStack(app, "StackSetStack", config=config)
    """

    def __init__(
        self, scope: Construct, construct_id: str, config: StackSetConfig, **kwargs
    ) -> None:
        """
        Initialize the StackSetStack.

        Args:
            scope (Construct): The scope in which to define this construct
            construct_id (str): The scoped construct ID
            config (StackSetConfig): StackSet configuration object
            **kwargs: Additional keyword arguments passed to Stack
        """
        super().__init__(scope, construct_id, **kwargs)

        self.config = config
        self.administration_role_arn = (
            f"arn:aws:iam::{self.account}:role/AWSCloudFormationStackSetAdministrationRole"
        )

        self.template_bucket = Bucket(
            self,
            "StackSetTemplateBucket",
            bucket_name=f"stacksets-blog-templates-{self.account}-{self.region}",
            versioned=True,
            encryption=BucketEncryption.S3_MANAGED,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            enforce_ssl=True
        )

        # Suppress CDK Nag rule S1 - server access logs not needed for template storage
        NagSuppressions.add_resource_suppressions(
            self.template_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "Server access logs not required for StackSet template storage bucket"
                }
            ]
        )

        self.stackset = self.create_stackset()
        self.create_outputs()


    def render_instance_template(self) -> str:
        """
        Generate CloudFormation template for StackSet deployment.

        Creates a temporary CDK App with the MonitoringStack to generate
        the CloudFormation template that will be deployed by the StackSet
        to target accounts and regions.

        Returns:
            str: JSON-formatted CloudFormation template as a string

        Example:
            template = self.render_instance_template()
            # Returns JSON string of the monitoring stack template
        """
        temp_app = App()
        # Create monitoring stack for template generation
        # pylint: disable=unused-variable
        monitoring_stack = MonitoringStack(
            temp_app, "TempMonitoringStack",
            notification_email=self.config.parameters["NotificationEmail"],
            dashboard_name=self.config.parameters["DashboardName"],
            alarm_prefix=self.config.parameters["AlarmPrefix"],
            description="Monitoring infrastructure template for StackSet deployment"
        )
        cloud_assembly = temp_app.synth()
        stack_artifact = cloud_assembly.get_stack_by_name("TempMonitoringStack")
        template = stack_artifact.template
        return json.dumps(template, indent=2)


    def create_stackset(self) -> CfnStackSet:
        """
        Create the CloudFormation StackSet resource.

        Creates a CloudFormation StackSet with the monitoring template,
        configured for SELF_MANAGED permissions with pre-deployed IAM roles.
        Includes stack instances for all target accounts and regions.

        Returns:
            CfnStackSet: The created CloudFormation StackSet resource

        Configuration:
            - Uses SELF_MANAGED permission model
            - Deploys to accounts and regions from config
            - Includes operation preferences for deployment control
            - Sets up parameter overrides for customization
        """
        template_body = self.render_instance_template()

        stackset = CfnStackSet(
            self, "MonitoringStackSet",
            stack_set_name=self.config.stack_set_name,
            description="Multi-region monitoring infrastructure deployed via StackSets",
            template_body=template_body,
            capabilities=["CAPABILITY_IAM"],
            permission_model="SELF_MANAGED",
            administration_role_arn=self.administration_role_arn,
            execution_role_name="AWSCloudFormationStackSetExecutionRole",

            operation_preferences=CfnStackSet.OperationPreferencesProperty(
                max_concurrent_percentage=self.config.max_concurrent_percentage,
                failure_tolerance_percentage=self.config.failure_tolerance_percentage,
                region_concurrency_type=self.config.region_concurrency_type
            ),
            stack_instances_group=[
                CfnStackSet.StackInstancesProperty(
                    deployment_targets=CfnStackSet.DeploymentTargetsProperty(
                        accounts=self.config.target_accounts
                    ),
                    regions=self.config.target_regions,

                )
            ]
        )

        return stackset



    def create_outputs(self) -> None:
        """
        Create CloudFormation outputs for StackSet information.

        Creates stack outputs that provide information about the deployed
        StackSet, including ARNs, configuration details, and resource names
        for reference by other stacks or external tools.

        Outputs Created:
            - StackSetArn: ARN of the created StackSet
            - AdministrationRoleArn: ARN of the administration role
            - PermissionModel: Permission model used (SELF_MANAGED)
            - TargetRegions: Comma-separated list of target regions
            - TemplateBucketName: Name of the S3 template bucket
        """
        CfnOutput(
            self, "StackSetArn",
            description="ARN of the created StackSet",
            value=self.stackset.attr_stack_set_id
        )

        CfnOutput(
            self, "AdministrationRoleArn",
            description="ARN of the StackSet administration role",
            value=self.administration_role_arn
        )

        CfnOutput(
            self, "PermissionModel",
            description="StackSet permission model",
            value="SELF_MANAGED"
        )

        CfnOutput(
            self, "TargetRegions",
            description="Regions where StackSet instances are deployed",
            value=",".join(self.config.target_regions)
        )

        CfnOutput(
            self, "TemplateBucketName",
            description="S3 bucket for StackSet templates",
            value=self.template_bucket.bucket_name
        )
