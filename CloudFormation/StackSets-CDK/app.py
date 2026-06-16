#!/usr/bin/env python3
"""
AWS CDK application for deploying StackSets infrastructure.

This module serves as the main entry point for deploying AWS CloudFormation
StackSets infrastructure across multiple AWS accounts and regions. It creates
the necessary CDK stacks for managing StackSets and monitoring infrastructure.

The application:
- Loads configuration from config.json and environment variables
- Creates StackSet management infrastructure
- Deploys monitoring resources across target accounts/regions
- Provides CI/CD pipeline capabilities (when implemented)

Usage:
    python3 app.py
    cdk deploy --all
"""

import sys
from aws_cdk import App, Environment, Aspects
from cdk_nag import AwsSolutionsChecks
from stacksets_blog import StackSetStack, PipelineStack
from stacksets_blog.utils import (
    get_stackset_config,
    get_monitoring_config,
    get_environment_config,
    get_pipelines_config
)

# Create AWS CDK app
app = App()

# Get environment configuration
env_config = get_environment_config()

# Set AWS CDK environment
env = Environment(
    account=env_config.account,
    region=env_config.region
)

# Get configurations from config file and environment
stackset_config = get_stackset_config("config.json", env_config)
monitoring_config = get_monitoring_config("config.json", env_config)

# Show all configuration
print("\nDeployment Configuration:\n")
print(f"  - Account: {env_config.account}")
print(f"  - Region: {env_config.region}")
print(f"  - Target regions: [{','.join(stackset_config.target_regions)}]")
print(f"  - Target accounts: [{','.join(stackset_config.target_accounts)}]")
print(f"  - Notification email: {monitoring_config.notification_email}")
print(f"  - Dashboard name: {monitoring_config.dashboard_name}")
print(f"  - Alarm prefix: {monitoring_config.alarm_prefix}")

# Deploy stacks
deployment_type = app.node.try_get_context("deployment_type")
if deployment_type is None:
    print("  - Deployment type: pipeline")
    pipelines_config = get_pipelines_config("config.json")
    print(f"  - Connection ARN: {pipelines_config[0].connection_arn}")
    print(f"  - Repository: {pipelines_config[0].repository_name}\n")
    for pipeline_config in pipelines_config:
        PipelineStack(
            app,
            f"PipelineStack{pipeline_config.environment.capitalize()}",
            description="CI/CD pipeline for automated StackSet updates",
            pipeline_config=pipeline_config,
            deployment_config=stackset_config
        )
elif deployment_type == "app":
    print("  - Deployment type: application\n")
    StackSetStack(
        app,
        "StackSetStack",
        config=stackset_config,
        monitoring_config=monitoring_config,
        description="StackSet management and multi-region deployment",
        env=env
    )
else:
    print("Error: unrecognized deployment_type. Valid types: None,app")
    sys.exit(1)

# Apply CDK Nag security checks
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))

app.synth()
