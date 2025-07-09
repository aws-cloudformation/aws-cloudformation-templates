# Amazon Q Business Templates

This directory contains CloudFormation templates for Amazon Q Business, including both basic and comprehensive enterprise deployments.

## Amazon Q Business Overview

Amazon Q Business is the most capable generative AI-powered assistant for finding information, gaining insight, and taking action at work. It makes generative AI securely accessible to everyone in your organization, and helps your employees get work done faster. Anyone in the organization can use natural language to request information or assistance to generate content or create lightweight apps that automate workflows.

**Resources:**
- [More Info](https://aws.amazon.com/q/business/)
- [Pricing](https://aws.amazon.com/q/business/pricing/)
- [Features](https://aws.amazon.com/q/business/features/)

## Templates

### 1. QBusinessApplication.yaml (Basic Template)
Creates a basic Q Business application with:
- Service role with proper permissions
- Identity Center integration
- Attachments and Q Apps enabled
- Development environment tags

**Use Case**: Quick setup for testing and development

### 2. QBusinessEnterprise.yaml (Enterprise Template)
Creates a comprehensive enterprise Q Business deployment with:
- Complete application stack (Application, Index, Retriever, Web Experience)
- S3 data source with scheduled sync
- Advanced monitoring and alerting
- Custom metrics and health checks
- Production-ready security configuration
- Cost optimization features

**Use Case**: Production enterprise deployments with full monitoring and data integration

## Prerequisites

### Basic Template
- AWS IAM Identity Center must be enabled in your account
- Obtain the Identity Center instance ARN from the console

### Enterprise Template
- AWS IAM Identity Center enabled and configured
- Existing S3 bucket with documents to index
- Email address for receiving alerts
- KMS key for encryption (optional)

## Quick Start

### Basic Deployment
```bash
aws cloudformation create-stack \
  --stack-name my-qbusiness-app \
  --template-body file://QBusinessApplication.yaml \
  --parameters ParameterKey=IdentityCenterInstanceArn,ParameterValue=arn:aws:sso:::instance/ssoins-xxxxxxxxxxxxxxxx \
  --capabilities CAPABILITY_IAM
```

### Enterprise Deployment
```bash
aws cloudformation create-stack \
  --stack-name enterprise-qbusiness \
  --template-body file://QBusinessEnterprise.yaml \
  --parameters \
    ParameterKey=ApplicationName,ParameterValue=CompanyKnowledgeBase \
    ParameterKey=IdentityCenterInstanceArn,ParameterValue=arn:aws:sso:::instance/ssoins-xxxxxxxxxxxxxxxx \
    ParameterKey=S3BucketName,ParameterValue=company-documents \
    ParameterKey=NotificationEmail,ParameterValue=admin@company.com \
  --capabilities CAPABILITY_NAMED_IAM
```

## Cost Optimization

- Q Business pricing is $20 per user per month
- Index capacity starts at $0.25/unit/hour
- Start with a small pilot group
- Monitor usage through CloudWatch metrics
- Consider data source costs separately

## Security Best Practices

- Uses least privilege IAM roles with proper trust policies
- Integrates with Identity Center for centralized authentication
- Enables KMS encryption for data at rest and in transit
- Implements proper resource tagging for governance
- Includes comprehensive logging and monitoring

## Enterprise Template Guide

For detailed information about the enterprise template, including:
- Complete architecture overview
- Advanced configuration options
- Sample data setup
- Monitoring and troubleshooting
- Cost optimization strategies
- Security best practices

**See: [README-Enterprise.md](README-Enterprise.md)**

