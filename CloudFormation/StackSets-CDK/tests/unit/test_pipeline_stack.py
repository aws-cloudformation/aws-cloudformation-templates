"""
Unit tests for PipelineStack.

This module contains unit tests for the PipelineStack class.
Note: PipelineStack is currently a placeholder with TODO implementation,
so tests are minimal and focus on basic stack creation.
"""

import os
import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from stacksets_blog.pipeline_stack import PipelineStack
from stacksets_blog.config import PipelineConfig, StackSetConfig


class TestPipelineStack:  # pylint: disable=too-many-public-methods
    """Test suite for PipelineStack class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.app = App()  # pylint: disable=attribute-defined-outside-init

        # Set up required environment variables for pipeline tests
        self.original_env = {}  # pylint: disable=attribute-defined-outside-init
        self.test_env_vars = {  # pylint: disable=attribute-defined-outside-init
            "CODECONNECTIONS_ARN": (
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            "REPOSITORY_NAME": "test-owner/test-repo",
            "BRANCH_NAME": "main",
            "NOTIFICATION_EMAIL": "test@example.com",
            "ENVIRONMENT": "test"
        }

        # Store original values and set test values
        for key, value in self.test_env_vars.items():
            self.original_env[key] = os.environ.get(key)
            os.environ[key] = value

        # Create test configuration objects
        self.pipeline_config = PipelineConfig(  # pylint: disable=attribute-defined-outside-init
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name="main",
            environment="test"
        )

        self.deployment_config = StackSetConfig(  # pylint: disable=attribute-defined-outside-init
            stack_set_name="TestStackSet",
            target_regions=["us-east-1", "us-west-2"],
            parameters={
                "NotificationEmail": "test@example.com",
                "DashboardName": "TestDashboard",
                "AlarmPrefix": "TestAlarms"
            },
            instance_stack_name="TestStack",
            target_accounts=["123456789012", "123456789013"]
        )

    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_pipeline_stack_creation(self):
        """Test PipelineStack creation."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check stack is created successfully
        assert stack.stack_name == "TestPipelineStack"
        # Verify template can be generated (even if empty for placeholder stack)
        assert template is not None

    def test_pipeline_stack_with_description(self):
        """Test PipelineStack creation with description."""
        # Arrange
        description = "Test CI/CD pipeline stack"

        # Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config,
            description=description
        )

        # Assert
        assert stack.stack_name == "TestPipelineStack"

    def test_pipeline_stack_foundation_resources(self):
        """Test that PipelineStack creates foundation infrastructure resources."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that foundation resources are created
        # S3 artifact bucket
        template.has_resource_properties("AWS::S3::Bucket", {
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [
                    {
                        "ServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            },
            "VersioningConfiguration": {
                "Status": "Enabled"
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True
            }
        })

        # CodePipeline service role
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "codepipeline.amazonaws.com"
                        }
                    }
                ]
            }
        })

        # CodeBuild service role
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "codebuild.amazonaws.com"
                        }
                    }
                ]
            }
        })

    def test_pipeline_stack_inheritance(self):
        """Test that PipelineStack properly inherits from Stack."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert
        assert isinstance(stack, Stack)

    def test_pipeline_stack_with_custom_kwargs(self):
        """Test PipelineStack creation with custom kwargs."""
        # Arrange
        custom_kwargs = {
            "description": "Custom pipeline description",
            "env": {"region": "us-east-1"}
        }

        # Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config,
            **custom_kwargs
        )

        # Assert
        assert stack.stack_name == "TestPipelineStack"

    def test_s3_artifact_bucket_lifecycle_policy(self):
        """Test that S3 artifact bucket has proper lifecycle policies."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check lifecycle configuration
        template.has_resource_properties("AWS::S3::Bucket", {
            "LifecycleConfiguration": {
                "Rules": [
                    {
                        "Id": "DeleteOldArtifacts",
                        "Status": "Enabled",
                        "ExpirationInDays": 30,
                        "NoncurrentVersionExpiration": {
                            "NoncurrentDays": 7
                        }
                    }
                ]
            }
        })

    # TODO: Add more comprehensive tests when additional pipeline components are implemented  # pylint: disable=fixme
    # Future tests should include:
    # - test_codebuild_project_creation()
    # - test_codepipeline_creation()
    # - test_pipeline_stages_configuration()
    # - test_build_environment_configuration()
    # - test_source_configuration()
    # - test_deploy_configuration()

    def test_pipeline_stack_attributes(self):
        """Test that PipelineStack exposes necessary attributes."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert - Check that stack exposes the foundation resources
        assert hasattr(stack, 'artifact_bucket')
        assert hasattr(stack, 'codepipeline_role')
        assert hasattr(stack, 'codebuild_role')

        # Verify the attributes are not None
        assert stack.artifact_bucket is not None
        assert stack.codepipeline_role is not None
        assert stack.codebuild_role is not None

        # Check that validation projects are created
        assert hasattr(stack, 'pylint_project')
        assert hasattr(stack, 'pytest_project')
        assert hasattr(stack, 'bandit_project')
        assert hasattr(stack, 'pip_audit_project')

        # Verify validation projects are not None
        assert stack.pylint_project is not None
        assert stack.pytest_project is not None
        assert stack.bandit_project is not None
        assert stack.pip_audit_project is not None

        # Check that pipeline is available
        assert hasattr(stack, 'pipeline')

        # Verify pipeline is not None
        assert stack.pipeline is not None

    def test_pipeline_validation_stage_configuration(self):
        """Test that the pipeline has a properly configured validation stage.
        
        Tests parallel actions in the validation stage.
        """
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that CodePipeline is created with all stages
        template.has_resource_properties("AWS::CodePipeline::Pipeline", {
            "Stages": [
                {
                    "Name": "Source",
                    "Actions": [
                        {
                            "Name": "Source",
                            "ActionTypeId": {
                                "Category": "Source",
                                "Owner": "AWS",
                                "Provider": "CodeStarSourceConnection"
                            }
                        }
                    ]
                },
                {
                    "Name": "Validation",
                    "Actions": [
                        {
                            "Name": "PyLint",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 1
                        },
                        {
                            "Name": "PyTest",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 1
                        },
                        {
                            "Name": "Bandit",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 1
                        },
                        {
                            "Name": "PipAudit",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 1
                        }
                    ]
                },
                {
                    "Name": "Deploy",
                    "Actions": [
                        {
                            "Name": "CDKDiff",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 1
                        },
                        {
                            "Name": "ManualApproval",
                            "ActionTypeId": {
                                "Category": "Approval",
                                "Owner": "AWS",
                                "Provider": "Manual"
                            },
                            "RunOrder": 2
                        },
                        {
                            "Name": "CDKDeploy",
                            "ActionTypeId": {
                                "Category": "Build",
                                "Owner": "AWS",
                                "Provider": "CodeBuild"
                            },
                            "RunOrder": 3
                        }
                    ]
                }
            ]
        })

        # Verify that all CodeBuild projects are created (4 validation + 1 CDK diff + 1 CDK deploy)
        template.resource_count_is("AWS::CodeBuild::Project", 6)

    def test_cdk_diff_project_configuration(self):
        """Test that the CDK diff CodeBuild project is properly configured."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that CDK diff CodeBuild project exists with proper configuration
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-diff",
            "Description": "CDK diff execution and output capture for manual approval review",
            "Environment": {
                "Type": "LINUX_CONTAINER",
                "Image": "aws/codebuild/standard:7.0",
                "ComputeType": "BUILD_GENERAL1_SMALL"
            }
        })

        # Verify that the CDK diff project has key environment variables
        # Check for CDK_DEFAULT_ACCOUNT
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-diff",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    Match.object_like({
                        "Name": "CDK_DEFAULT_ACCOUNT",
                        "Type": "PLAINTEXT"
                    })
                ])
            }
        })

        # Check for NOTIFICATION_EMAIL variable from configuration
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-diff",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    Match.object_like({
                        "Name": "NOTIFICATION_EMAIL",
                        "Type": "PLAINTEXT",
                        "Value": "test@example.com"
                    })
                ])
            }
        })

    def test_cdk_deploy_project_configuration(self):
        """Test that the CDK deploy CodeBuild project is properly configured."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that CDK deploy CodeBuild project exists with proper configuration
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-deploy",
            "Description": (
                "CDK deployment execution with proper error handling and artifact generation"
            ),
            "Environment": {
                "Type": "LINUX_CONTAINER",
                "Image": "aws/codebuild/standard:7.0",
                "ComputeType": "BUILD_GENERAL1_SMALL"
            }
        })

        # Verify that the CDK deploy project has key environment variables
        # Check for CDK_DEFAULT_ACCOUNT
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-deploy",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    Match.object_like({
                        "Name": "CDK_DEFAULT_ACCOUNT",
                        "Type": "PLAINTEXT"
                    })
                ])
            }
        })

        # Check for NOTIFICATION_EMAIL variable from configuration
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-deploy",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    Match.object_like({
                        "Name": "NOTIFICATION_EMAIL",
                        "Type": "PLAINTEXT",
                        "Value": "test@example.com"
                    })
                ])
            }
        })

        # Verify that the stack has the CDK deploy project attribute
        assert hasattr(stack, 'cdk_deploy_project')
        assert stack.cdk_deploy_project is not None

    def test_validation_outputs_structure(self):
        """Test that validation outputs are properly structured for downstream stages."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert - Check validation projects are properly structured
        validation_projects = {
            'pylint': stack.pylint_project,
            'pytest': stack.pytest_project,
            'bandit': stack.bandit_project,
            'pip_audit': stack.pip_audit_project
        }

        # Verify all validation projects exist and are not None
        for project_name, project in validation_projects.items():
            assert project is not None, f"Validation project '{project_name}' should not be None"
            assert hasattr(project, 'project_name'), (
                f"Project '{project_name}' should have a project_name attribute"
            )

    def test_manual_approval_configuration(self):
        """Test that manual approval action is properly configured with SNS notification."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that the pipeline has the Deploy stage with manual approval
        template.has_resource_properties("AWS::CodePipeline::Pipeline", {
            "Stages": Match.array_with([
                Match.object_like({
                    "Name": "Deploy",
                    "Actions": Match.array_with([
                        Match.object_like({
                            "Name": "ManualApproval",
                            "ActionTypeId": {
                                "Category": "Approval",
                                "Owner": "AWS",
                                "Provider": "Manual"
                            },
                            "RunOrder": 2
                        })
                    ])
                })
            ])
        })



    def test_pipeline_configuration_from_environment(self):
        """Test that PipelineStack properly uses configuration from environment variables."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert - Check that pipeline configuration is properly initialized
        assert hasattr(stack, 'pipeline_config')
        assert stack.pipeline_config is not None

        # Verify configuration values from environment
        assert stack.pipeline_config.connection_arn == self.test_env_vars["CODECONNECTIONS_ARN"]
        assert stack.pipeline_config.repository_name == self.test_env_vars["REPOSITORY_NAME"]
        assert stack.pipeline_config.branch_name == self.test_env_vars["BRANCH_NAME"]
        assert stack.pipeline_config.environment == self.test_env_vars["ENVIRONMENT"]

        # Verify deployment configuration
        assert hasattr(stack, 'deployment_config')
        assert stack.deployment_config is not None
        assert (
            stack.deployment_config.parameters["NotificationEmail"] ==
            self.test_env_vars["NOTIFICATION_EMAIL"]
        )

    def test_pipeline_configuration_helper_methods(self):
        """Test that PipelineStack configuration helper methods work correctly."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert - Test deployment configuration access
        assert stack.deployment_config is not None
        assert stack.deployment_config.parameters["NotificationEmail"] == 'test@example.com'
        assert stack.deployment_config.parameters["DashboardName"] == 'TestDashboard'
        assert stack.deployment_config.parameters["AlarmPrefix"] == 'TestAlarms'

        # Assert - Test pipeline configuration helper methods
        assert stack.pipeline_config.get_repository_name() == 'test-repo'
        assert stack.pipeline_config.get_repository_owner() == 'test-owner'
        assert (
            stack.pipeline_config.get_pipeline_name() == 'test-repo-test-pipeline'
        )

        # Assert - Test configuration values
        assert stack.pipeline_config.environment == 'test'
        assert stack.pipeline_config.repository_name == 'test-owner/test-repo'
        assert stack.pipeline_config.branch_name == 'main'

    def test_pipeline_configuration_validation(self):  # pylint: disable=duplicate-code
        """Test that pipeline configuration validation works correctly."""
        # Arrange - Create production pipeline config
        production_pipeline_config = PipelineConfig(
            connection_arn=(
                "arn:aws:codeconnections:us-east-1:123456789012:connection/test-connection-id"
            ),
            repository_name="test-owner/test-repo",
            branch_name="main",
            environment="production"
        )

        # Act & Assert - Should create successfully with valid configuration
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=production_pipeline_config,
            deployment_config=self.deployment_config
        )
        assert stack.pipeline_config.environment == 'production'

    def test_codebuild_environment_variables_integration(self):
        """Test that CodeBuild projects receive proper environment variables from configuration."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that CDK projects have configuration environment variables
        # Check CDK diff project has environment variables
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-diff",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    {
                        "Name": "NOTIFICATION_EMAIL",
                        "Type": "PLAINTEXT",
                        "Value": "test@example.com"
                    }
                ])
            }
        })

        # Check CDK deploy project has environment variables
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-deploy",
            "Environment": {
                "EnvironmentVariables": Match.array_with([
                    {
                        "Name": "NOTIFICATION_EMAIL",
                        "Type": "PLAINTEXT",
                        "Value": "test@example.com"
                    }
                ])
            }
        })

    def test_iam_role_permissions_validation(self):
        """Test that IAM roles have proper permissions for pipeline operations."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check CodePipeline service role permissions
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "codepipeline.amazonaws.com"
                        }
                    }
                ]
            },
            "Policies": [
                {
                    "PolicyName": "PipelineExecutionPolicy",
                    "PolicyDocument": {
                        "Statement": Match.array_with([
                            # S3 permissions for artifact bucket
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": Match.array_with([
                                    "s3:GetBucketVersioning",
                                    "s3:GetObject",
                                    "s3:GetObjectVersion",
                                    "s3:PutObject",
                                    "s3:PutObjectAcl"
                                ])
                            }),
                            # CodeBuild permissions
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": Match.array_with([
                                    "codebuild:BatchGetBuilds",
                                    "codebuild:StartBuild"
                                ])
                            }),
                            # CodeConnections permissions
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": "codestar-connections:UseConnection"
                            })
                        ])
                    }
                }
            ]
        })

        # Assert - Check CodeBuild service role permissions
        template.has_resource_properties("AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "codebuild.amazonaws.com"
                        }
                    }
                ]
            },
            "Policies": [
                {
                    "PolicyName": "CodeBuildExecutionPolicy",
                    "PolicyDocument": {
                        "Statement": Match.array_with([
                            # CloudWatch Logs permissions
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": Match.array_with([
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents"
                                ])
                            }),
                            # S3 permissions for artifact bucket
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": Match.array_with([
                                    "s3:GetBucketVersioning",
                                    "s3:GetObject",
                                    "s3:GetObjectVersion",
                                    "s3:PutObject"
                                ])
                            }),
                            # CDK deployment permissions
                            Match.object_like({
                                "Effect": "Allow",
                                "Action": Match.array_with([
                                    "sts:AssumeRole",
                                    "cloudformation:*",
                                    "iam:PassRole"
                                ])
                            })
                        ])
                    }
                }
            ]
        })

    def test_buildspec_validation_for_codebuild_projects(self):
        """Test that CodeBuild projects have valid buildspec configurations."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check PyLint project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-pylint",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

        # Assert - Check PyTest project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-pytest",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

        # Assert - Check Bandit project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-bandit",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

        # Assert - Check pip-audit project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-pip-audit",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

        # Assert - Check CDK diff project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-diff",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

        # Assert - Check CDK deploy project buildspec structure
        template.has_resource_properties("AWS::CodeBuild::Project", {
            "Name": "test-repo-test-pipeline-deploy",
            "Source": {
                "Type": "NO_SOURCE",
                "BuildSpec": Match.string_like_regexp(r'.*version:\s*0\.2.*')
            }
        })

    def test_artifact_flow_between_stages(self):
        """Test that artifacts flow properly between pipeline stages."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )

        # Assert - Check that pipeline exists and has the expected structure
        assert stack.pipeline is not None
        template = Template.from_stack(stack)

        # Verify that the pipeline has the expected stages
        template.has_resource_properties(
            "AWS::CodePipeline::Pipeline", {
                "Stages": Match.array_with([
                Match.object_like({"Name": "Source"}),
                Match.object_like({"Name": "Validation"}),
                Match.object_like({"Name": "Deploy"})
            ])
        })

        # Verify that validation projects exist (these handle the artifact flow)
        validation_projects = [
            stack.pylint_project, stack.pytest_project,
            stack.bandit_project, stack.pip_audit_project
        ]
        for project in validation_projects:
            assert project is not None

    def test_pipeline_stage_ordering(self):
        """Test that pipeline stages are in the correct order with proper dependencies."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check that pipeline has stages in correct order
        template.has_resource_properties("AWS::CodePipeline::Pipeline", {
            "Stages": [
                # Stage 1: Source
                {
                    "Name": "Source",
                    "Actions": [
                        {
                            "Name": "Source",
                            "ActionTypeId": {
                                "Category": "Source",
                                "Owner": "AWS",
                                "Provider": "CodeStarSourceConnection"
                            }
                        }
                    ]
                },
                # Stage 2: Validation (parallel actions)
                {
                    "Name": "Validation",
                    "Actions": Match.array_with([
                        Match.object_like({
                            "Name": "PyLint",
                            "RunOrder": 1
                        }),
                        Match.object_like({
                            "Name": "PyTest",
                            "RunOrder": 1
                        }),
                        Match.object_like({
                            "Name": "Bandit",
                            "RunOrder": 1
                        }),
                        Match.object_like({
                            "Name": "PipAudit",
                            "RunOrder": 1
                        })
                    ])
                },
                # Stage 3: Deploy (sequential actions)
                {
                    "Name": "Deploy",
                    "Actions": Match.array_with([
                        Match.object_like({
                            "Name": "CDKDiff",
                            "RunOrder": 1
                        }),
                        Match.object_like({
                            "Name": "ManualApproval",
                            "RunOrder": 2
                        }),
                        Match.object_like({
                            "Name": "CDKDeploy",
                            "RunOrder": 3
                        })
                    ])
                }
            ]
        })

    def test_resource_tagging_and_naming_conventions(self):
        """Test that resources follow proper naming conventions and tagging."""
        # Arrange & Act
        stack = PipelineStack(
            self.app,
            "TestPipelineStack",
            pipeline_config=self.pipeline_config,
            deployment_config=self.deployment_config
        )
        template = Template.from_stack(stack)

        # Assert - Check S3 bucket naming (bucket name is generated using CDK tokens)
        template.has_resource_properties("AWS::S3::Bucket", {
            "BucketName": Match.any_value()  # CDK generates bucket name with tokens
        })

        # Assert - Check CodeBuild project naming conventions
        expected_projects = [
            "test-repo-test-pipeline-pylint",
            "test-repo-test-pipeline-pytest",
            "test-repo-test-pipeline-bandit",
            "test-repo-test-pipeline-pip-audit",
            "test-repo-test-pipeline-diff",
            "test-repo-test-pipeline-deploy"
        ]

        for project_name in expected_projects:
            template.has_resource_properties("AWS::CodeBuild::Project", {
                "Name": project_name
            })

        # Assert - Check pipeline naming (includes environment)
        template.has_resource_properties("AWS::CodePipeline::Pipeline", {
            "Name": "test-repo-test-pipeline"
        })

    def test_error_handling_in_configuration(self):
        """Test that configuration errors are properly handled."""
        # Arrange - Remove required environment variable
        del os.environ['CODECONNECTIONS_ARN']

        # Act & Assert - Should raise ValueError for missing configuration
        with pytest.raises(ValueError, match="CodeConnections ARN is required"):
            PipelineConfig(
                connection_arn="",
                repository_name="test-owner/test-repo",
                branch_name="main",
                environment="production"
            )

        # Restore environment variable for cleanup
        os.environ['CODECONNECTIONS_ARN'] = self.test_env_vars['CODECONNECTIONS_ARN']
