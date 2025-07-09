# Amazon Q Business Enterprise Template

This comprehensive CloudFormation template deploys a complete Amazon Q Business solution for enterprise use cases, including data sources, retrievers, web experience, monitoring, and alerting.

## 🏗️ Architecture Overview

The template creates a production-ready Q Business deployment with:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon Q Business Enterprise                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Application   │  │      Index      │  │    Retriever    │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  S3 Data Source │  │ Web Experience  │  │   Monitoring    │  │
│  │                 │  │                 │  │   & Alerting    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### Core Components
- **Q Business Application**: Main AI assistant application
- **Index**: Enterprise-grade document index with custom attributes
- **Retriever**: Native index retriever for document search
- **Web Experience**: User-friendly web interface
- **Data Sources**: S3 bucket integration with scheduled sync

### Security & Compliance
- **IAM Roles**: Least privilege access with proper trust policies
- **Encryption**: KMS encryption for data at rest and in transit
- **Identity Center**: Integration with AWS IAM Identity Center
- **CloudWatch Logs**: Centralized logging with retention policies

### Monitoring & Observability
- **CloudWatch Dashboard**: Real-time metrics and visualizations
- **Custom Metrics**: Lambda-based health monitoring
- **Alerting**: SNS notifications for failures and errors
- **Scheduled Monitoring**: EventBridge-triggered health checks

### Enterprise Features
- **Document Attributes**: Department, document type, confidentiality levels
- **Personalization**: Enabled for user-specific experiences
- **Q Apps**: Custom application development capabilities
- **Attachments**: File upload and processing support

## 📋 Prerequisites

### Required Resources
1. **AWS IAM Identity Center**: Must be enabled and configured
2. **S3 Bucket**: Existing bucket with documents to index
3. **Email Address**: For receiving alerts and notifications
4. **KMS Key**: For encryption (optional, uses AWS managed key by default)

### Required Permissions
The deploying user/role needs permissions for:
- IAM role creation and policy attachment
- Q Business resource management
- CloudWatch dashboard and alarm creation
- SNS topic and subscription management
- Lambda function deployment
- EventBridge rule creation

## 🛠️ Deployment

### Step 1: Prepare Prerequisites

1. **Enable Identity Center**:
   ```bash
   # Get your Identity Center instance ARN
   aws sso-admin list-instances
   ```

2. **Set Up S3 Bucket with Sample Data**:
   
   **Option A: Automated Setup (Recommended)**
   ```bash
   # Use the provided script to create bucket and upload sample data
   chmod +x setup-sample-data.sh
   ./setup-sample-data.sh my-company-qbusiness-docs us-east-1
   ```
   
   **Option B: Manual Setup**
   ```bash
   # Create bucket manually
   aws s3 mb s3://my-company-qbusiness-docs --region us-east-1
   
   # Upload your own documents
   aws s3 cp documents/ s3://my-company-qbusiness-docs/ --recursive
   ```

3. **Sample Data Included**:
   The setup script creates a complete set of sample company documents:
   - **HR Policies**: Employee handbook, expense policy
   - **IT Procedures**: Security procedures, access control
   - **Engineering Manuals**: Onboarding guide, development processes
   - **Support FAQs**: Customer support questions and answers
   
   Each document includes proper metadata for department, document type, and confidentiality level.

### Step 2: Deploy the Template

```bash
aws cloudformation create-stack \
  --stack-name enterprise-qbusiness \
  --template-body file://QBusinessEnterprise.yaml \
  --parameters \
    ParameterKey=ApplicationName,ParameterValue=MyEnterpriseQBusiness \
    ParameterKey=IdentityCenterInstanceArn,ParameterValue=arn:aws:sso:::instance/ssoins-xxxxxxxxxxxxxxxx \
    ParameterKey=S3BucketName,ParameterValue=your-company-documents \
    ParameterKey=NotificationEmail,ParameterValue=admin@yourcompany.com \
    ParameterKey=WebExperienceTitle,ParameterValue="Company Knowledge Assistant" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 3: Monitor Deployment

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name enterprise-qbusiness

# Watch events
aws cloudformation describe-stack-events --stack-name enterprise-qbusiness
```

## 📊 Post-Deployment Configuration

### 1**Check Application Status**:

   ```bash
   APPLICATION_ID=$(aws cloudformation describe-stacks \
     --stack-name enterprise-qbusiness \
     --query 'Stacks[0].Outputs[?OutputKey==`ApplicationId`].OutputValue' \
     --output text)
   
   aws qbusiness get-application --application-id $APPLICATION_ID
   ```

### 2. **Verify Web Experience Status**:
   ```bash
   aws qbusiness list-web-experiences --application-id $APPLICATION_ID
   ```

   **Expected Status**: `ACTIVE`


### 3. Configure Data Source Sync

The S3 data source is configured to sync daily at 2 AM. To trigger manual sync:

```bash
# Get data source ID
DATA_SOURCE_ID=$(aws cloudformation describe-stacks \
  --stack-name enterprise-qbusiness \
  --query 'Stacks[0].Outputs[?OutputKey==`S3DataSourceId`].OutputValue' \
  --output text)

APPLICATION_ID=$(aws cloudformation describe-stacks \
  --stack-name enterprise-qbusiness \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationId`].OutputValue' \
  --output text)

INDEX_ID=$(aws cloudformation describe-stacks \
  --stack-name enterprise-qbusiness \
  --query 'Stacks[0].Outputs[?OutputKey==`IndexId`].OutputValue' \
  --output text)

# Start sync job
aws qbusiness start-data-source-sync-job \
  --application-id $APPLICATION_ID \
  --index-id $INDEX_ID \
  --data-source-id $DATA_SOURCE_ID
```

### 4. Set Up User Access

Configure users in Identity Center to access the Q Business application:

1. Go to AWS IAM Identity Center console
2. Create users and Add users to appropriate groups

  **Optional: Commands to Create User in Identity Center**:
   ```bash
   # Get Identity Store ID
   IDENTITY_STORE_ID=$(aws sso-admin list-instances \
     --query 'Instances[0].IdentityStoreId' --output text)
   
   # Create user
   aws identitystore create-user \
     --identity-store-id $IDENTITY_STORE_ID \
     --user-name "qbusiness-admin" \
     --display-name "Q Business Admin" \
     --name Formatted="Q Business Admin",GivenName="QBusiness",FamilyName="Admin" \
     --emails Value="admin@company.com",Primary=true
   ```
   
3. Go to Q Business Console → Access Management
4. Add user with Admin/User permissions
5. Set password for the users in Identity Center
6. Configure attribute mappings if needed

### 5. Access web Experience URL

After deployment, get the web experience URL:

```bash
aws cloudformation describe-stacks \
  --stack-name enterprise-qbusiness \
  --query 'Stacks[0].Outputs[?OutputKey==`WebExperienceUrl`].OutputValue' \
  --output text
```

- Login with the user created in the above step.

### 6. Test with Sample Queries

Once your data source sync is complete, try these sample queries in the Q Business web experience:

**Policy Questions:**
- "What is our expense policy for meals?"
- "How much can I spend on hotel rooms when traveling?"
- "What benefits does the company offer?"
- "What is our code of conduct regarding professional behavior?"

**Security and IT Questions:**
- "How do I reset my password?"
- "What are the password requirements?"
- "How do we handle security incidents?"
- "What is our data classification policy?"

**Engineering and Process Questions:**
- "How do new engineers get onboarded?"
- "What development tools do we use?"
- "What is our Git workflow?"
- "How do we conduct code reviews?"

**Customer Support Questions:**
- "What are your business hours?"
- "How do I contact customer support?"
- "How do I export my data?"
- "What payment methods do you accept?"

These queries will help you verify that the document indexing and retrieval are working correctly.


### 7. Monitor Application Health

Access the CloudWatch dashboard:

```bash
# Get dashboard URL
aws cloudformation describe-stacks \
  --stack-name enterprise-qbusiness \
  --query 'Stacks[0].Outputs[?OutputKey==`DashboardUrl`].OutputValue' \
  --output text
```

## 🔧 Customization Options

### Document Attributes

The template includes predefined document attributes:
- `department`: STRING - Department owning the document
- `document_type`: STRING - Type of document (policy, procedure, etc.)
- `confidentiality`: STRING - Confidentiality level
- `last_modified`: DATE - Last modification date

To add custom attributes, modify the `DocumentAttributeConfigurations` section.

### Data Source Configuration

#### S3 Data Source Patterns
```yaml
inclusionPatterns:
  - '*.pdf'
  - '*.docx'
  - '*.txt'
  - '*.md'
exclusionPatterns:
  - 'temp/*'
  - '*/archive/*'
```

#### Sync Schedule
Default: Daily at 2 AM UTC (`cron(0 2 * * ? *)`)

Common alternatives:
- Every 6 hours: `cron(0 */6 * * ? *)`
- Business hours only: `cron(0 9-17 ? * MON-FRI *)`
- Weekly: `cron(0 2 ? * SUN *)`

### Monitoring Configuration

#### Custom Metrics
The template includes a Lambda function that publishes custom metrics:
- Application health status
- Custom business metrics
- Integration status checks

#### Alert Thresholds
- Data source sync failures: 1 failure triggers alert
- High error rate: 10 errors in 10 minutes triggers alert

## 💰 Cost Optimization

### Pricing Components

1. **Q Business Application**: $20/user/month
2. **Index Capacity**: $0.25/unit/hour (starts with 1 unit)
3. **Data Source Sync**: Included in application pricing
4. **Storage**: $0.023/GB/month for indexed content
5. **Supporting Services**:
   - CloudWatch: ~$5-10/month for dashboards and alarms
   - Lambda: <$1/month for custom metrics
   - SNS: <$1/month for notifications

### Cost Optimization Tips

1. **Right-size Index Capacity**:
   ```bash
   # Monitor index utilization
   aws cloudwatch get-metric-statistics \
     --namespace AWS/QBusiness \
     --metric-name IndexUtilization \
     --start-time 2024-01-01T00:00:00Z \
     --end-time 2024-01-02T00:00:00Z \
     --period 3600 \
     --statistics Average
   ```

2. **Optimize Data Sources**:
   - Use inclusion/exclusion patterns to limit indexed content
   - Schedule syncs during off-peak hours
   - Remove duplicate or outdated documents

3. **Monitor User Adoption**:
   - Track active users to optimize licensing
   - Use CloudWatch metrics to identify usage patterns

## 🔒 Security Best Practices

### IAM Roles and Policies
- Service roles use least privilege principles
- Trust policies include source account and ARN conditions
- Data source roles are scoped to specific S3 buckets

### Encryption
- KMS encryption for all data at rest
- TLS encryption for data in transit
- CloudWatch logs encrypted with KMS

### Network Security
- Deploy in private subnets when possible
- Use VPC endpoints for AWS service communication
- Implement security groups for additional protection

### Access Control
- Identity Center integration for centralized user management
- Attribute-based access control (ABAC) support
- Regular access reviews and auditing

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. QBusinessRetriever Configuration Errors

**Error**: `Properties validation failed for resource QBusinessRetriever with message: #/Configuration: required key [NativeIndexConfiguration] not found`

**Solution**: The retriever configuration requires `NativeIndexConfiguration` and the IndexId attribute:
```yaml
QBusinessRetriever:
  Type: AWS::QBusiness::Retriever
  Properties:
    Type: 'NATIVE_INDEX'
    Configuration:
      NativeIndexConfiguration:
        IndexId: !GetAtt QBusinessIndex.IndexId  # Use GetAtt, not Ref
```

#### 2. IAM Role Trust Policy Issues

**Error**: `Please make sure your role exists, has qbusiness.amazonaws.com as trusted entity`

**Solution**: Ensure the data source role has proper trust policy with conditions:
```yaml
AssumeRolePolicyDocument:
  Statement:
    - Effect: Allow
      Principal:
        Service: qbusiness.amazonaws.com
      Action: sts:AssumeRole
      Condition:
        StringEquals:
          'aws:SourceAccount': !Ref 'AWS::AccountId'
        ArnLike:
          'aws:SourceArn': 
            - !Sub 'arn:aws:qbusiness:${AWS::Region}:${AWS::AccountId}:application/*/index/*/data-source/*'
            - !Sub 'arn:aws:qbusiness:${AWS::Region}:${AWS::AccountId}:application/*'
```

#### 3. S3 Data Source Configuration Schema Errors

**Error**: `Encountered 1 error(s) while processing the data source configuration input against the schema`

**Solution**: The S3 data source configuration must include required fields:
```yaml
Configuration:
  type: 'S3'                    # Required: Data source type
  syncMode: 'FULL_CRAWL'        # Required: Sync mode
  connectionConfiguration:       # Required: Connection details
    repositoryEndpointMetadata:
      BucketName: !Ref S3BucketName
  repositoryConfigurations:      # Required: Repository config
    document:
      fieldMappings: [...]
  version: '1.0.0'              # Recommended: Schema version
```

#### 4. Web Experience 404 Error (PENDING_AUTH_CONFIG)

**Error**: Web experience shows 404 or "Page not found"

**Root Cause**: Web experience stuck in `PENDING_AUTH_CONFIG` status

**Solution Steps**:

1. **Check Web Experience Status**:
   ```bash
   aws qbusiness get-web-experience \
     --application-id YOUR_APP_ID \
     --web-experience-id YOUR_WEB_EXP_ID
   ```

2. **If Status is PENDING_AUTH_CONFIG**:
   - **Option A**: Delete and recreate web experience with proper role ARN
   - **Option B**: Complete user assignment in Identity Center

3. **Create Users in Identity Center**:
   ```bash
   # Create user
   aws identitystore create-user \
     --identity-store-id YOUR_IDENTITY_STORE_ID \
     --user-name "qbusiness-admin" \
     --display-name "Q Business Admin" \
     --name Formatted="Q Business Admin",GivenName="QBusiness",FamilyName="Admin" \
     --emails Value="admin@example.com",Primary=true
   ```

4. **Assign User to Q Business Application**:
   - Go to AWS IAM Identity Center Console
   - Navigate to Applications → Find Q Business app
   - Assign users and set permissions
   - Set user passwords in Identity Center

5. **If Web Experience Still Stuck, Recreate It**:
   ```bash
   # Delete problematic web experience
   aws qbusiness delete-web-experience \
     --application-id YOUR_APP_ID \
     --web-experience-id YOUR_WEB_EXP_ID
   
   # Create new one with role ARN
   aws qbusiness create-web-experience \
     --application-id YOUR_APP_ID \
     --title "Enterprise Knowledge Assistant" \
     --subtitle "Ask questions about company documents" \
     --role-arn "arn:aws:iam::ACCOUNT:role/QBusinessRole" \
     --sample-prompts-control-mode ENABLED
   ```

#### 5. Data Source Sync Failures
```bash
# Check sync job status
aws qbusiness list-data-source-sync-jobs \
  --application-id $APPLICATION_ID \
  --index-id $INDEX_ID \
  --data-source-id $DATA_SOURCE_ID

# Check CloudWatch logs
aws logs filter-log-events \
  --log-group-name /aws/qbusiness/MyEnterpriseQBusiness \
  --start-time $(date -d '1 hour ago' +%s)000
```

#### 6. KMS Key Issues

**Error**: KMS key access denied

**Solution**: Ensure KMS key policy includes Q Business service permissions:
```yaml
- Sid: Allow Q Business Service
  Effect: Allow
  Principal:
    Service: qbusiness.amazonaws.com
  Action:
    - 'kms:Decrypt'
    - 'kms:GenerateDataKey'
    - 'kms:CreateGrant'
  Resource: '*'
  Condition:
    StringEquals:
      'aws:SourceAccount': !Ref 'AWS::AccountId'
```

### Deployment Validation Checklist

Before deploying, ensure:

- [ ] Identity Center is enabled and configured
- [ ] S3 bucket exists and contains documents
- [ ] IAM permissions are sufficient for deployment
- [ ] Email address is valid for notifications
- [ ] Region supports Q Business service

After deployment, verify:

- [ ] Application status is ACTIVE
- [ ] Index is created successfully  
- [ ] Data source sync completes without errors
- [ ] Web experience status is ACTIVE (not PENDING_AUTH_CONFIG)
- [ ] Users can access web experience URL
- [ ] CloudWatch dashboard shows metrics

### Emergency Recovery

If deployment fails completely:

1. **Check CloudFormation Events**:
   ```bash
   aws cloudformation describe-stack-events --stack-name enterprise-qbusiness
   ```

2. **Delete and Redeploy**:
   ```bash
   aws cloudformation delete-stack --stack-name enterprise-qbusiness
   # Wait for deletion to complete, then redeploy
   ```

3. **Partial Recovery** (if only web experience fails):
   - Delete web experience manually
   - Update stack to recreate it

### Monitoring Commands

```bash
# Application health
aws qbusiness get-application --application-id $APPLICATION_ID

# Index statistics
aws qbusiness describe-index \
  --application-id $APPLICATION_ID \
  --index-id $INDEX_ID

# Recent conversations
aws qbusiness list-conversations \
  --application-id $APPLICATION_ID \
  --user-id $USER_ID
```

## 🔄 Maintenance

### Regular Tasks

1. **Weekly**:
   - Review CloudWatch dashboard
   - Check alert notifications
   - Monitor data source sync status

2. **Monthly**:
   - Review cost and usage reports
   - Update document attributes if needed
   - Audit user access and permissions

3. **Quarterly**:
   - Review and update inclusion/exclusion patterns
   - Optimize index capacity based on usage
   - Update security configurations

### Backup and Recovery

The template includes:
- CloudWatch log retention (90 days)
- SNS topic for critical alerts
- Custom metrics for health monitoring

For disaster recovery:
- Document all configuration parameters
- Maintain backup of custom document attributes
- Keep record of user access configurations

## 📚 Additional Resources

- [Amazon Q Business User Guide](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/)
- [Q Business API Reference](https://docs.aws.amazon.com/amazonq/latest/api-reference/)
- [Identity Center Integration](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/identity-center.html)
- [Data Source Connectors](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/connectors.html)
- [Cost Optimization Guide](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/cost-optimization.html)

## 🤝 Support

For issues with this template:
1. Check the troubleshooting section above
2. Review CloudWatch logs and metrics
3. Consult AWS Q Business documentation
4. Contact AWS Support for service-specific issues
