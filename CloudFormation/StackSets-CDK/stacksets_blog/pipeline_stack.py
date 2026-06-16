"""
AWS CDK Pipeline Stack for automated StackSet deployments.

This module defines the PipelineStack class which implements CI/CD automation
for updating CloudFormation StackSets when code changes occur. The pipeline
includes CodePipeline, CodeBuild, and the necessary IAM roles for StackSet
operations.

Classes:
    PipelineStack: CDK Stack for creating CI/CD pipeline infrastructure

Example:
    from stacksets_blog.pipeline_stack import PipelineStack

    pipeline_stack = PipelineStack(
        app, "PipelineStack",
        description="CI/CD pipeline for automated StackSet updates"
    )
"""



from aws_cdk import Stack, Duration, RemovalPolicy
from aws_cdk.aws_s3 import Bucket, BucketEncryption, BlockPublicAccess, LifecycleRule
from aws_cdk.aws_iam import (
    Role, ServicePrincipal, PolicyDocument, PolicyStatement
)
from aws_cdk.aws_codepipeline import Pipeline, StageProps, Artifact
from aws_cdk.aws_codepipeline_actions import (
    CodeStarConnectionsSourceAction, CodeBuildAction, ManualApprovalAction
)
from aws_cdk.aws_codebuild import (
    Project, BuildSpec, BuildEnvironment, LinuxBuildImage, ComputeType,
    BuildEnvironmentVariable
)
from aws_cdk.aws_kms import Key
from constructs import Construct
from cdk_nag import NagSuppressions

from .config import PipelineConfig, StackSetConfig


class PipelineStack(Stack):  # pylint: disable=too-many-instance-attributes
    """
    PipelineStack implements the CI/CD automation that updates the StackSet
    when code changes. This includes CodePipeline, CodeBuild, and the necessary
    IAM roles for StackSet operations.
    """

    # Runtime versions for CodeBuild environments
    PYTHON_VERSION = "3.12"
    NODEJS_VERSION = "22"

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        pipeline_config: PipelineConfig,
        deployment_config: StackSetConfig,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Initialize pipeline configuration
        self.pipeline_config = pipeline_config
        self.deployment_config = deployment_config

        # Extract deployment parameters for convenience
        self.notification_email = deployment_config.parameters["NotificationEmail"]
        self.dashboard_name = deployment_config.parameters["DashboardName"]
        self.alarm_prefix = deployment_config.parameters["AlarmPrefix"]
        self.target_accounts = deployment_config.target_accounts

        # Create S3 artifact bucket with encryption and lifecycle policies
        self.artifact_bucket = Bucket(
            self, "ArtifactBucket",
            bucket_name=f"pipeline-artifacts-{self.account}-{self.region}",
            encryption=BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            enforce_ssl=True,
            lifecycle_rules=[
                LifecycleRule(
                    id="DeleteOldArtifacts",
                    enabled=True,
                    expiration=Duration.days(30),
                    noncurrent_version_expiration=Duration.days(7)
                )
            ]
        )

        # Create roles for the Pipeline
        self.create_roles()

        # Define build environment for AWS CodeBuild projects
        self.build_environment = BuildEnvironment(
            build_image=LinuxBuildImage.STANDARD_7_0,
            compute_type=ComputeType.SMALL
        )

        # Create encryption key for AWS CodeBuild projects
        self.encryption_key = Key(
            self, "PipelineEncryptionKey",
            description="KMS key for encrypting CI/CD pipeline artifacts and CodeBuild resources",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create CodeBuild projects
        self.pylint_project = self.create_pylint_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-pylint"
        )
        self.pytest_project = self.create_pytest_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-pytest"
        )
        self.bandit_project = self.create_bandit_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-bandit"
        )
        self.pip_audit_project = self.create_pip_audit_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-pip-audit"
        )
        self.cdk_diff_project = self.create_cdk_diff_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-diff"
        )
        self.cdk_deploy_project = self.create_cdk_deploy_project(
            project_name=f"{pipeline_config.get_pipeline_name()}-deploy"
        )

        # Create the CodePipeline with source stage
        self.pipeline = self.create_pipeline()

        # Add cdk-nag suppressions for exceptions
        self.add_cdk_nag_suppressions()

    def _get_common_environment_variables(self) -> dict[str, BuildEnvironmentVariable]:
        """
        Get common environment variables used across all CodeBuild projects.
        
        Returns:
            dict[str, BuildEnvironmentVariable]: Dictionary of environment variables
                that are common to all CodeBuild projects in the pipeline
        """
        return {
            "CDK_DEFAULT_ACCOUNT": BuildEnvironmentVariable(value=self.account),
            "CDK_DEFAULT_REGION": BuildEnvironmentVariable(value=self.region),
            "NOTIFICATION_EMAIL": BuildEnvironmentVariable(value=self.notification_email),
            "DASHBOARD_NAME": BuildEnvironmentVariable(value=self.dashboard_name),
            "ALARM_PREFIX": BuildEnvironmentVariable(value=self.alarm_prefix),
            "TARGET_ACCOUNTS": BuildEnvironmentVariable(value=",".join(self.target_accounts))
        }

    def create_roles(self) -> None:
        """
        Create IAM service roles for CodePipeline and CodeBuild projects.

        Creates the necessary IAM roles with appropriate permissions for:
        - CodePipeline service role with S3, CodeBuild, and CodeConnections permissions
        - CodeBuild service role with CloudWatch Logs, S3, and CDK deployment permissions

        The roles follow the principle of least privilege and include only the
        permissions necessary for the pipeline operations.
        """
        # Create IAM service roles for CodePipeline
        self.codepipeline_role = Role(
            self,
            "CodePipelineServiceRole",
            assumed_by=ServicePrincipal("codepipeline.amazonaws.com"),
            description="Service role for CodePipeline to access AWS resources",
            inline_policies={
                "PipelineExecutionPolicy": PolicyDocument(
                    statements=[
                        # S3 permissions for artifact bucket
                        PolicyStatement(
                            actions=[
                                "s3:GetBucketVersioning",
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "s3:PutObject",
                                "s3:PutObjectAcl"
                            ],
                            resources=[
                                self.artifact_bucket.bucket_arn,
                                f"{self.artifact_bucket.bucket_arn}/*"
                            ]
                        ),
                        # CodeBuild permissions
                        PolicyStatement(
                            actions=[
                                "codebuild:BatchGetBuilds",
                                "codebuild:StartBuild"
                            ],
                            resources=["*"]
                        ),
                        # CodeConnections permissions
                        PolicyStatement(
                            actions=[
                                "codestar-connections:UseConnection"
                            ],
                            resources=["*"]
                        ),
                        # SNS permissions for manual approval notifications
                        PolicyStatement(
                            actions=[
                                "sns:Publish"
                            ],
                            resources=[
                                f"arn:aws:sns:{self.region}:{self.account}:"
                                f"{self.stack_name}-manual-approval"
                            ]
                        )
                    ]
                )
            }
        )

        # Add CDK Nag suppressions for CodePipeline role inline policy wildcard permissions
        NagSuppressions.add_resource_suppressions(
            self.codepipeline_role,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": ("CodePipeline requires wildcard permissions for S3 artifact "
                              "bucket objects as artifact names are dynamically generated "
                              "during pipeline execution"),
                    "appliesTo": [
                        "Resource::<ArtifactBucket7410C9EF.Arn>/*"
                    ]
                },
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": ("CodePipeline requires wildcard permissions for CodeBuild "
                              "projects and CodeConnections as resource names are dynamic"),
                    "appliesTo": [
                        "Resource::*"
                    ]
                }
            ]
        )

        # Create IAM service roles for CodeBuild
        self.codebuild_role = Role(
            self,
            "CodeBuildServiceRole",
            assumed_by=ServicePrincipal("codebuild.amazonaws.com"),
            description="Service role for CodeBuild projects to access AWS resources",
            inline_policies={
                "CodeBuildExecutionPolicy": PolicyDocument(
                    statements=[
                        # CloudWatch Logs permissions
                        PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=[
                                (f"arn:aws:logs:{self.region}:{self.account}:"
                                 "log-group:/aws/codebuild/*")
                            ]
                        ),
                        # S3 permissions for artifact bucket
                        PolicyStatement(
                            actions=[
                                "s3:GetBucketVersioning",
                                "s3:GetObject",
                                "s3:GetObjectVersion",
                                "s3:PutObject"
                            ],
                            resources=[
                                self.artifact_bucket.bucket_arn,
                                f"{self.artifact_bucket.bucket_arn}/*"
                            ]
                        ),
                        # CodeBuild Reports permissions
                        PolicyStatement(
                            actions=[
                                "codebuild:CreateReportGroup",
                                "codebuild:CreateReport",
                                "codebuild:UpdateReport",
                                "codebuild:BatchPutTestCases",
                                "codebuild:BatchPutCodeCoverages"
                            ],
                            resources=[
                                f"arn:aws:codebuild:{self.region}:{self.account}:report-group/*"
                            ]
                        ),
                        # CDK deployment permissions (for deploy stage)
                        PolicyStatement(
                            actions=[
                                "sts:AssumeRole",
                                "cloudformation:*",
                                "iam:PassRole",
                                "iam:GetRole",
                                "iam:CreateRole",
                                "iam:DeleteRole",
                                "iam:UpdateRole",
                                "iam:AttachRolePolicy",
                                "iam:DetachRolePolicy",
                                "iam:PutRolePolicy",
                                "iam:DeleteRolePolicy",
                                "iam:GetRolePolicy",
                                "iam:ListRolePolicies",
                                "iam:ListAttachedRolePolicies"
                            ],
                            resources=["*"]
                        ),
                        # CDK bootstrap and diff permissions
                        PolicyStatement(
                            actions=[
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                                "ssm:GetParametersByPath",
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                                "s3:ListBucket",
                                "s3:GetBucketLocation",
                                "s3:GetBucketVersioning",
                                "s3:CreateBucket",
                                "s3:PutBucketVersioning",
                                "s3:PutBucketPublicAccessBlock",
                                "s3:PutEncryptionConfiguration"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

    def create_pylint_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for PyLint code quality validation.

        Returns:
            codebuild.Project: The PyLint validation project
        """
        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION
                    },
                    "commands": [
                        "pip3 install -r requirements-dev.txt -r requirements.txt"
                    ]
                },
                "build": {
                    "commands": [
                        ("find . -name '*.py' ! -path './cdk.out/*' | "
                         "xargs pylint")
                    ]
                },
            }
        }

        return Project(
            self,
            "PyLintProject",
            project_name=project_name,
            description="PyLint code quality validation for the StackSets blog project",
            environment=self.build_environment,
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_pytest_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for PyTest unit tests and coverage validation.

        Returns:
            codebuild.Project: The PyTest validation project
        """
        reports_directory = "reports"
        unit_tests_file = "results.xml"
        coverage_file = "coverage.xml"

        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION
                    },
                    "commands": [
                        "pip3 install -r requirements.txt -r requirements-dev.txt"
                    ]
                },
                "build": {
                    "commands": [
                        ("coverage erase && python3 -m coverage run --branch -m pytest -v && "
                         "coverage report"),
                        f"python3 -m coverage xml -i -o {reports_directory}/{coverage_file}",
                        f"python3 -m pytest --junitxml={reports_directory}/{unit_tests_file}"
                    ]
                }
            },
            "reports": {
                "unit_tests_reports": {
                    "files": unit_tests_file,
                    "base-directory": reports_directory,
                    "file-format": "JUNITXML",
                },
                "coverage_reports": {
                    "files": coverage_file,
                    "base-directory": reports_directory,
                    "file-format": "COBERTURAXML",
                }
            }
        }

        return Project(
            self,
            "PyTestProject",
            project_name=project_name,
            description="PyTest unit tests and coverage validation for the StackSets blog project",
            environment=self.build_environment,
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_bandit_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for Bandit security scanning validation.

        Returns:
            codebuild.Project: The Bandit security scanning project
        """
        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION
                    },
                    "commands": [
                        "pip3 install -r requirements-dev.txt"
                    ]
                },
                "build": {
                    "commands": [
                        "bandit -r ."
                    ]
                }
            }
        }

        return Project(
            self,
            "BanditProject",
            project_name=project_name,
            description="Bandit security scanning validation for the StackSets blog project",
            environment=self.build_environment,
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_pip_audit_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for pip-audit dependency vulnerability scanning.

        Returns:
            codebuild.Project: The pip-audit vulnerability scanning project
        """
        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION
                    },
                    "commands": [
                        "pip3 install -r requirements-dev.txt"
                    ]
                },
                "build": {
                    "commands": [
                        "pip-audit -r requirements.txt",
                        "pip-audit -r requirements-dev.txt"
                    ]
                }
            }
        }

        return Project(
            self, "PipAuditProject",
            project_name=project_name,
            description=("pip-audit dependency vulnerability scanning for the "
                         "StackSets blog project"),
            environment=self.build_environment,
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_cdk_diff_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for CDK diff execution and output capture.

        Returns:
            codebuild.Project: The CDK diff project
        """
        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION,
                        "nodejs": self.NODEJS_VERSION
                    },
                    "commands": [
                        "npm install -g aws-cdk@latest",
                        "pip3 install -r requirements.txt",
                        "cdk --version"
                    ]
                },
                "build": {
                    "commands": [
                        "cdk diff -c deployment_type=app"
                    ]
                }
            }
        }

        return Project(
            self,
            "CDKDiffProject",
            project_name=project_name,
            description="CDK diff execution and output capture for manual approval review",
            environment=BuildEnvironment(
                build_image=self.build_environment.build_image,
                compute_type=self.build_environment.compute_type,
                environment_variables=self._get_common_environment_variables()
            ),
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_cdk_deploy_project(self, project_name:str) -> Project:
        """
        Create CodeBuild project for CDK deployment with appropriate compute size.

        Returns:
            codebuild.Project: The CDK deploy project
        """
        buildspec_definition = {
            "version": 0.2,
            "phases": {
                "install": {
                    "runtime-versions": {
                        "python": self.PYTHON_VERSION,
                        "nodejs": self.NODEJS_VERSION
                    },
                    "commands": [
                        "npm install -g aws-cdk@latest",
                        "pip3 install -r requirements.txt"
                    ]
                },
                "build": {
                    "commands": [
                        "cdk deploy -c deployment_type=app --require-approval never"
                    ]
                }
            }
        }

        return Project(
            self, "CDKDeployProject",
            project_name=project_name,
            description=("CDK deployment execution with proper error handling "
                         "and artifact generation"),
            environment=BuildEnvironment(
                build_image=self.build_environment.build_image,
                compute_type=self.build_environment.compute_type,
                environment_variables=self._get_common_environment_variables()
            ),
            build_spec=BuildSpec.from_object_to_yaml(buildspec_definition),
            role=self.codebuild_role,
            encryption_key=self.encryption_key
        )

    def create_pipeline(self) -> Pipeline:  # pylint: disable=too-many-locals
        """
        Create the CodePipeline with CodeConnections source stage.

        Returns:
            codepipeline.Pipeline: The created pipeline
        """
        # Create source artifact
        source_output = Artifact("SourceOutput")

        # Create CodeConnections source action
        self.source_action = CodeStarConnectionsSourceAction(
            action_name="Source",
            connection_arn=self.pipeline_config.connection_arn,
            output=source_output,
            owner=self.pipeline_config.get_repository_owner(),
            repo=self.pipeline_config.get_repository_name(),
            branch=self.pipeline_config.branch_name,
            trigger_on_push=True
        )

        # Create the pipeline with all stages
        return Pipeline(
            self,
            "Pipeline",
            pipeline_name=self.pipeline_config.get_pipeline_name(),
            artifact_bucket=self.artifact_bucket,
            role=self.codepipeline_role,
            stages=[
                StageProps(
                    stage_name="Source",
                    actions=[
                        self.source_action
                    ]
                ),
                StageProps(
                    stage_name="Validation",
                    actions=[
                        # Create Code Validaton Stage
                        CodeBuildAction(
                            action_name="PyLint",
                            project=self.pylint_project,
                            input=source_output
                        ),
                        CodeBuildAction(
                            action_name="PyTest",
                            project=self.pytest_project,
                            input=source_output
                        ),
                        CodeBuildAction(
                            action_name="Bandit",
                            project=self.bandit_project,
                            input=source_output
                        ),
                        CodeBuildAction(
                            action_name="PipAudit",
                            project=self.pip_audit_project,
                            input=source_output
                        )
                    ]
                ),
                StageProps(
                    stage_name="Deploy",
                    actions=[
                        CodeBuildAction(
                            action_name="CDKDiff",
                            project=self.cdk_diff_project,
                            input=source_output,
                            run_order=1
                        ),
                        ManualApprovalAction(
                            action_name="ManualApproval",
                            run_order=2
                        ),
                        CodeBuildAction(
                            action_name="CDKDeploy",
                            project=self.cdk_deploy_project,
                            input=source_output,
                            run_order=3
                        )
                    ]
                )
            ]
        )

    def add_cdk_nag_suppressions(self) -> None:
        """Add CDK Nag suppressions for remaining wildcard permissions."""
        # Add CDK Nag suppressions for the S3 bucket
        NagSuppressions.add_resource_suppressions(
            self.artifact_bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": ("Server access logs are not required for CI/CD artifact "
                              "bucket as it contains temporary build artifacts only")
                }
            ]
        )

        NagSuppressions.add_resource_suppressions(
            self.codepipeline_role,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Wildcard is needed so that the pipeline can work",
                    "applies_to": [
                        "Action::s3:*"
                    ]
                },
            ],
            True,
        )

        NagSuppressions.add_resource_suppressions(
            self.codebuild_role,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Wildcard is needed that the pipeline can work",
                    "applies_to": [
                        "Action::s3:*"
                    ],
                },
            ],
            True,
        )

        NagSuppressions.add_resource_suppressions_by_path(
            self,
            (f"/{self.stack_name}/Pipeline/Source/Source/"
             "CodePipelineActionRole/DefaultPolicy/Resource"),
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": ("CodePipeline Source Action Role is fully managed by "
                              "AWS CDK I cant control it"),
                }
            ]
        )
