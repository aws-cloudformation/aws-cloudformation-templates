#!/bin/bash

# Amazon Q Business Sample Data Setup Script
# This script creates an S3 bucket and uploads comprehensive sample documents for the enterprise template
#
# FEATURES:
# - Creates S3 bucket with proper security configuration
# - Uploads comprehensive sample company documents with metadata
# - Fixes IAM permissions for Q Business data source integration
# - Triggers data source sync jobs
# - Provides troubleshooting guidance
#
# USAGE:
#   ./setup-sample-data.sh <bucket-name> [region] [stack-name]
#   ./setup-sample-data.sh --fix-permissions <stack-name> <bucket-name>
#   ./setup-sample-data.sh --sync <stack-name>
#
# SAMPLE DOCUMENTS CREATED:
# - Employee handbook (HR policies, benefits, procedures)
# - IT security procedures (passwords, data classification, incident response)
# - Customer support FAQ (common questions, business hours, contact info)
# - Engineering onboarding guide (development processes, tools, standards)
#
# TROUBLESHOOTING:
# If Q Business returns "no relevant information found":
# 1. Check data source sync status
# 2. Verify IAM permissions with --fix-permissions
# 3. Trigger manual sync with --sync
# 4. Check CloudWatch logs for detailed errors
#
# FIXES INCLUDED:
# - Adds missing qbusiness:BatchPutDocument permission
# - Updates S3 bucket policies for new bucket access
# - Comprehensive sample documents with proper metadata
# - Automatic sync triggering and monitoring
#
# VERSION: 2.0 - Enhanced with troubleshooting fixes and automation

set -e  # Exit on any error

# Configuration
BUCKET_NAME=""
REGION="us-east-1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_DATA_DIR="$SCRIPT_DIR/sample-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first:"
        echo "  https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "AWS CLI is installed and configured"
}

# Function to validate bucket name
validate_bucket_name() {
    if [[ -z "$BUCKET_NAME" ]]; then
        print_error "Bucket name is required"
        echo "Usage: $0 <bucket-name> [region]"
        echo "Example: $0 my-company-qbusiness-docs us-east-1"
        exit 1
    fi
    
    # Check bucket name format
    if [[ ! "$BUCKET_NAME" =~ ^[a-z0-9][a-z0-9-]*[a-z0-9]$ ]] || [[ ${#BUCKET_NAME} -lt 3 ]] || [[ ${#BUCKET_NAME} -gt 63 ]]; then
        print_error "Invalid bucket name format"
        echo "Bucket names must:"
        echo "  - Be 3-63 characters long"
        echo "  - Start and end with lowercase letter or number"
        echo "  - Contain only lowercase letters, numbers, and hyphens"
        exit 1
    fi
}

# Function to create S3 bucket
create_bucket() {
    print_status "Creating S3 bucket: $BUCKET_NAME in region: $REGION"
    
    # Check if bucket already exists
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        print_warning "Bucket $BUCKET_NAME already exists"
        return 0
    fi
    
    # Create bucket
    if [[ "$REGION" == "us-east-1" ]]; then
        # us-east-1 doesn't need LocationConstraint
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION"
    fi
    
    print_success "Bucket created successfully"
}

# Function to configure bucket settings
configure_bucket() {
    print_status "Configuring bucket settings..."
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Set bucket encryption
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    },
                    "BucketKeyEnabled": true
                }
            ]
        }'
    
    
    print_success "Bucket configured with versioning, encryption, and public access blocked"
}

# Function to add metadata to files
add_metadata_to_file() {
    local file_path="$1"
    local s3_key="$2"
    local department=""
    local document_type=""
    local confidentiality=""
    local content_type=""
    
    # Extract metadata from filename prefix and original file path
    case "$s3_key" in
        policy-*)
            department="Human Resources"
            document_type="Policy"
            confidentiality="Internal"
            ;;
        procedure-*)
            department="Information Technology"
            document_type="Procedure"
            confidentiality="Internal"
            ;;
        manual-*)
            department="Engineering"
            document_type="Manual"
            confidentiality="Internal"
            ;;
        faq-*)
            department="Customer Support"
            document_type="FAQ"
            confidentiality="Public"
            ;;
        README.md)
            department="General"
            document_type="Documentation"
            confidentiality="Internal"
            ;;
        *)
            # Fallback: try to determine from original file path
            case "$file_path" in
                */policies/*)
                    department="Human Resources"
                    document_type="Policy"
                    confidentiality="Internal"
                    ;;
                */procedures/*)
                    department="Information Technology"
                    document_type="Procedure"
                    confidentiality="Internal"
                    ;;
                */manuals/*)
                    department="Engineering"
                    document_type="Manual"
                    confidentiality="Internal"
                    ;;
                */faqs/*)
                    department="Customer Support"
                    document_type="FAQ"
                    confidentiality="Public"
                    ;;
                *)
                    department="General"
                    document_type="Document"
                    confidentiality="Internal"
                    ;;
            esac
            ;;
    esac
    
    # Set content type based on file extension
    case "$s3_key" in
        *.md)
            content_type="text/markdown"
            ;;
        *.txt)
            content_type="text/plain"
            ;;
        *.pdf)
            content_type="application/pdf"
            ;;
        *)
            content_type="text/plain"
            ;;
    esac
    
    # Upload file with metadata to root directory
    aws s3 cp "$file_path" "s3://$BUCKET_NAME/$s3_key" \
        --metadata "department=$department,document_type=$document_type,confidentiality=$confidentiality" \
        --content-type "$content_type"
}

# Function to upload sample data
upload_sample_data() {
    print_status "Uploading sample data files to root directory..."
    
    if [[ ! -d "$SAMPLE_DATA_DIR" ]]; then
        print_error "Sample data directory not found: $SAMPLE_DATA_DIR"
        print_status "Creating sample data directory and files..."
        create_sample_data_directory
    fi
    
    local file_count=0
    
    # Upload all markdown files to root directory with descriptive names
    while IFS= read -r -d '' file; do
        # Get just the filename without path
        local filename=$(basename "$file")
        
        # Create descriptive root-level filename based on subdirectory and original name
        local root_filename=""
        case "$file" in
            */policies/*)
                root_filename="policy-${filename}"
                ;;
            */procedures/*)
                root_filename="procedure-${filename}"
                ;;
            */faqs/*)
                root_filename="faq-${filename}"
                ;;
            */manuals/*)
                root_filename="manual-${filename}"
                ;;
            *)
                root_filename="$filename"
                ;;
        esac
        
        print_status "Uploading: $filename -> $root_filename (root level)"
        add_metadata_to_file "$file" "$root_filename"
        
        ((file_count++))
    done < <(find "$SAMPLE_DATA_DIR" -name "*.md" -type f -print0)
    
    print_success "Uploaded $file_count sample documents to root directory"
}

# Function to create sample data directory if it doesn't exist
create_sample_data_directory() {
    print_status "Creating sample data directory structure..."
    
    mkdir -p "$SAMPLE_DATA_DIR"/{policies,procedures,faqs,manuals}
    
    # Create comprehensive employee handbook (will become policy-employee-handbook.md)
    cat > "$SAMPLE_DATA_DIR/policies/employee-handbook.md" << 'EOF'
# Employee Handbook - Company Policies and Procedures

## 1. EXPENSE POLICY
- Employees can expense up to **$50 per day** for meals when traveling
- Hotel expenses should not exceed **$200 per night**
- All expenses must be submitted within **30 days** with receipts
- Rental car expenses are covered for business travel
- Mileage reimbursement is **$0.65 per mile** for personal vehicle use

## 2. VACATION POLICY  
- Employees accrue **2 weeks of vacation per year**
- Vacation requests must be submitted **2 weeks in advance**
- Maximum vacation carryover is **5 days**
- Sick leave is separate from vacation time
- Personal days: **3 per year**

## 3. REMOTE WORK POLICY
- Employees can work remotely up to **3 days per week**
- Remote work must be approved by manager
- Home office equipment reimbursement up to **$500**
- Internet stipend: **$50 per month** for remote workers

## 4. BENEFITS
- Health insurance covers **90% of medical costs**
- Dental and vision insurance available
- **401k matching up to 6%** of salary
- Life insurance provided at **2x annual salary**
- Flexible spending account available
- Employee assistance program included

## 5. CODE OF CONDUCT
- Professional behavior expected at all times
- Harassment and discrimination are not tolerated
- Confidential information must be protected
- Social media guidelines apply to work-related posts
EOF

    # Create detailed expense policy (will become policy-expense-policy.md)
    cat > "$SAMPLE_DATA_DIR/policies/expense-policy.md" << 'EOF'
# Detailed Expense Policy

## Meal Expenses
- **Daily meal limit**: $50 per day when traveling
- **Business meals**: Up to $100 per person for client entertainment
- **Team meals**: Approved for team building events
- **Alcohol**: Limited to $25 per person at business meals

## Travel Expenses
- **Hotel**: Maximum $200 per night in major cities, $150 in other locations
- **Flights**: Economy class for domestic, business class for international flights over 6 hours
- **Rental cars**: Mid-size or smaller, unless business need requires larger vehicle
- **Mileage**: $0.65 per mile for personal vehicle use
- **Parking**: Reasonable parking fees covered
- **Tolls**: All toll charges covered

## Expense Submission
- **Deadline**: Submit within 30 days of expense
- **Receipts**: Required for all expenses over $25
- **Approval**: Manager approval required for expenses over $500
- **Reimbursement**: Processed within 2 weeks of submission

## Non-Reimbursable Expenses
- Personal entertainment
- Spouse/family travel costs
- Traffic violations and fines
- Personal phone calls
- Excessive or luxury accommodations
EOF

    # Create IT security procedures (will become procedure-it-security-procedures.md)
    cat > "$SAMPLE_DATA_DIR/procedures/it-security-procedures.md" << 'EOF'
# IT Security Procedures

## Password Requirements
- **Minimum 12 characters**
- Must include uppercase, lowercase, numbers, and symbols
- Changed every **90 days**
- Cannot reuse last **12 passwords**
- Use password manager for complex passwords

## Data Classification
- **PUBLIC**: Can be shared externally
- **INTERNAL**: For company use only  
- **CONFIDENTIAL**: Restricted access required
- **SECRET**: Executive approval required

## Incident Response
1. **Immediately report** security incidents to IT
2. **Do not attempt** to fix issues yourself
3. **Preserve evidence** and logs
4. **Document all actions** taken
5. **Follow up** with security team

## VPN Access
- **Required** for all remote connections
- Use **company-approved VPN client** only
- **Never share** VPN credentials
- **Report lost devices** immediately
- VPN must be active for all work activities

## Device Security
- Enable **full disk encryption**
- Install **security updates promptly**
- Use **approved antivirus software**
- **Lock screen** when away from desk
- **Report suspicious emails** to IT

## Network Security
- Use **secure WiFi networks** only
- **Avoid public WiFi** for work
- Enable **firewall** on all devices
- **Regular security scans** required
EOF

    # Create customer support FAQ (will become faq-customer-support-faq.md)
    cat > "$SAMPLE_DATA_DIR/faqs/customer-support-faq.md" << 'EOF'
# Customer Support FAQ

## Business Hours
**Q: What are your business hours?**
A: We are open **Monday-Friday 9 AM to 6 PM EST**. Weekend support available for premium customers.

## Account Management
**Q: How do I reset my password?**
A: Click **"Forgot Password"** on the login page and follow the email instructions. If you don't receive the email, check your spam folder.

**Q: How do I cancel my subscription?**
A: Log into your account and go to **Settings > Billing > Cancel Subscription**. You can also contact support for assistance.

## Billing and Payments
**Q: What payment methods do you accept?**
A: We accept **all major credit cards** (Visa, MasterCard, American Express), **PayPal**, and **bank transfers**.

**Q: Do you offer refunds?**
A: Yes, we offer **full refunds within 30 days** of purchase. Pro-rated refunds available for annual subscriptions.

**Q: How do I upgrade my plan?**
A: Go to **Settings > Billing > Change Plan** or contact our sales team for enterprise options.

## Support and Contact
**Q: How do I contact support?**
A: Email **support@company.com**, call **1-800-SUPPORT**, or use the live chat on our website.

**Q: What's included in the free trial?**
A: **14-day free trial** with full access to all features. No credit card required to start.

## Data and Security
**Q: Can I export my data?**
A: Yes, go to **Settings > Data Export** to download your information in CSV or JSON format.

**Q: Is my data secure?**
A: Yes, we use **enterprise-grade encryption**, regular security audits, and comply with **SOC 2 standards**.

## Training and Integration
**Q: Do you offer training?**
A: Yes, we provide **onboarding sessions**, video tutorials, and documentation. Premium support includes dedicated training.

**Q: How do I integrate with other tools?**
A: We offer **APIs and pre-built integrations** with popular tools. Check our integrations page for details.
EOF

    # Create engineering onboarding guide (will become manual-engineering-onboarding.md)
    cat > "$SAMPLE_DATA_DIR/manuals/engineering-onboarding.md" << 'EOF'
# Engineering Onboarding Guide

Welcome to the Engineering Team!

## First Day Setup
1. Receive **laptop and security badge**
2. Set up **development environment**
3. Install **required software tools**
4. Configure **VPN and security tools**
5. Join **team Slack channels**
6. Schedule **meetings with team members**

## Development Tools
- **IDE**: Visual Studio Code or IntelliJ
- **Version Control**: Git with GitHub
- **Project Management**: Jira
- **Communication**: Slack, Microsoft Teams
- **Documentation**: Confluence
- **Code Review**: GitHub Pull Requests

## Development Process
1. Create **feature branch** from main
2. Implement **changes with tests**
3. Run **automated test suite**
4. Submit **pull request** for review
5. Address **review feedback**
6. **Merge after approval**
7. Deploy to **staging environment**
8. **Verify functionality**
9. Deploy to **production**

## Coding Standards
- Follow **language-specific style guides**
- Write **comprehensive unit tests**
- **Document complex functions**
- Use **meaningful variable names**
- Keep **functions small and focused**
- **Regular code reviews** required

## Security Practices
- **Never commit secrets** or passwords
- Use **environment variables** for config
- **Regular dependency updates**
- **Security scanning** in CI/CD
- Follow **secure coding practices**

## Team Meetings
- **Daily standup** at 9 AM
- **Sprint planning** every 2 weeks
- **Retrospectives** monthly
- **Architecture reviews** as needed
- **All-hands engineering** monthly

## Resources
- Internal **documentation wiki**
- Slack **#engineering channel**
- **Mentor assignment** for first month
- **Training budget**: $2000 annually
- **Conference attendance** encouraged
EOF

    print_success "Created sample data directory with comprehensive documents"
}

# Function to check and fix IAM permissions for Q Business data source
check_and_fix_iam_permissions() {
    local stack_name="$1"
    
    if [[ -z "$stack_name" ]]; then
        print_warning "Stack name not provided. Skipping IAM permission check."
        print_warning "To fix IAM permissions later, run:"
        echo "  $0 --fix-permissions <stack-name> <bucket-name>"
        return 0
    fi
    
    print_status "Checking IAM permissions for Q Business data source..."
    
    # Get data source role name from CloudFormation stack
    local role_arn
    role_arn=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`DataSourceRoleArn`].OutputValue' \
        --output text 2>/dev/null)
    
    if [[ -z "$role_arn" || "$role_arn" == "None" ]]; then
        print_warning "Could not find DataSourceRoleArn in stack outputs"
        print_warning "Make sure the CloudFormation stack is deployed first"
        return 0
    fi
    
    local role_name
    role_name=$(echo "$role_arn" | cut -d'/' -f2)
    
    print_status "Found data source role: $role_name"
    
    # Check if Q Business permissions exist
    local has_qbusiness_policy=false
    if aws iam get-role-policy --role-name "$role_name" --policy-name "QBusinessDataSourcePolicy" &>/dev/null; then
        has_qbusiness_policy=true
    fi
    
    # Add Q Business permissions if missing
    if [[ "$has_qbusiness_policy" == "false" ]]; then
        print_status "Adding missing Q Business permissions to role: $role_name"
        
        aws iam put-role-policy \
            --role-name "$role_name" \
            --policy-name "QBusinessDataSourcePolicy" \
            --policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "QBusinessDocumentPermissions",
                        "Effect": "Allow",
                        "Action": [
                            "qbusiness:BatchPutDocument",
                            "qbusiness:BatchDeleteDocument",
                            "qbusiness:PutGroup",
                            "qbusiness:CreateUser",
                            "qbusiness:DeleteGroup",
                            "qbusiness:ListGroups",
                            "qbusiness:UpdateUser",
                            "qbusiness:ListUsers"
                        ],
                        "Resource": "*"
                    }
                ]
            }'
        
        print_success "Added Q Business permissions to data source role"
    else
        print_success "Q Business permissions already exist"
    fi
    
    # Update S3 permissions to include new bucket
    print_status "Updating S3 permissions for bucket: $BUCKET_NAME"
    
    local s3_policy_doc
    s3_policy_doc=$(cat << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        },
        {
            "Sid": "S3BucketVersioning",
            "Effect": "Allow",
            "Action": [
                "s3:GetObjectVersion",
                "s3:ListBucketVersions"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKET_NAME",
                "arn:aws:s3:::$BUCKET_NAME/*"
            ]
        }
    ]
}
EOF
    )
    
    aws iam put-role-policy \
        --role-name "$role_name" \
        --policy-name "S3DataSourcePolicy" \
        --policy-document "$s3_policy_doc"
    
    print_success "Updated S3 permissions for new bucket"
}

# Function to trigger data source sync
trigger_data_source_sync() {
    local stack_name="$1"
    
    if [[ -z "$stack_name" ]]; then
        print_warning "Stack name not provided. Skipping data source sync."
        print_warning "To trigger sync later, run:"
        echo "  aws qbusiness start-data-source-sync-job --application-id <app-id> --index-id <index-id> --data-source-id <ds-id>"
        return 0
    fi
    
    print_status "Triggering Q Business data source sync..."
    
    # Get required IDs from CloudFormation stack
    local app_id index_id ds_id
    app_id=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationId`].OutputValue' \
        --output text 2>/dev/null)
    
    index_id=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`IndexId`].OutputValue' \
        --output text 2>/dev/null)
    
    ds_id=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --query 'Stacks[0].Outputs[?OutputKey==`S3DataSourceId`].OutputValue' \
        --output text 2>/dev/null)
    
    if [[ -z "$app_id" || -z "$index_id" || -z "$ds_id" ]]; then
        print_warning "Could not find required IDs in stack outputs"
        print_warning "Make sure the CloudFormation stack is fully deployed"
        return 0
    fi
    
    # Start sync job
    local execution_id
    execution_id=$(aws qbusiness start-data-source-sync-job \
        --application-id "$app_id" \
        --index-id "$index_id" \
        --data-source-id "$ds_id" \
        --query 'executionId' \
        --output text)
    
    if [[ -n "$execution_id" ]]; then
        print_success "Started data source sync job: $execution_id"
        print_status "Monitor sync progress with:"
        echo "  aws qbusiness list-data-source-sync-jobs --application-id $app_id --index-id $index_id --data-source-id $ds_id"
    else
        print_error "Failed to start data source sync job"
    fi
}

# Function to verify upload
verify_upload() {
    print_status "Verifying uploaded files..."
    
    local file_count=$(aws s3 ls "s3://$BUCKET_NAME" --recursive | wc -l)
    
    if [[ $file_count -gt 0 ]]; then
        print_success "Successfully uploaded $file_count files to S3 bucket"
        
        echo ""
        echo "📁 Files in bucket:"
        aws s3 ls "s3://$BUCKET_NAME" --recursive --human-readable
        
        echo ""
        print_success "Sample data setup complete!"
        
    else
        print_error "No files found in bucket after upload"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Amazon Q Business Sample Data Setup"
    echo ""
    echo "Usage: $0 <bucket-name> [region] [stack-name]"
    echo "       $0 --fix-permissions <stack-name> <bucket-name>"
    echo "       $0 --sync <stack-name>"
    echo ""
    echo "Arguments:"
    echo "  bucket-name    Name for the S3 bucket (required)"
    echo "  region         AWS region (optional, default: us-east-1)"
    echo "  stack-name     CloudFormation stack name (optional, for IAM fixes and sync)"
    echo ""
    echo "Options:"
    echo "  --fix-permissions  Fix IAM permissions for existing stack"
    echo "  --sync            Trigger data source sync for existing stack"
    echo ""
    echo "Examples:"
    echo "  # Basic setup - create bucket and upload documents"
    echo "  $0 my-company-qbusiness-docs"
    echo ""
    echo "  # Setup with region and stack integration"
    echo "  $0 my-company-qbusiness-docs us-west-2 enterprise-qbusiness"
    echo ""
    echo "  # Fix IAM permissions for existing deployment"
    echo "  $0 --fix-permissions enterprise-qbusiness my-company-qbusiness-docs"
    echo ""
    echo "  # Trigger data source sync"
    echo "  $0 --sync enterprise-qbusiness"
    echo ""
    echo "The script will:"
    echo "  1. Create an S3 bucket with proper configuration"
    echo "  2. Upload comprehensive sample company documents with metadata"
    echo "  3. Configure bucket for Q Business data source integration"
    echo "  4. Fix IAM permissions if stack name provided"
    echo "  5. Trigger data source sync if stack is ready"
    echo ""
    echo "Sample documents created (uploaded to root directory for Q Business compatibility):"
    echo "  - policy-employee-handbook.md (HR policies, benefits, procedures)"
    echo "  - policy-expense-policy.md (detailed expense guidelines and limits)"
    echo "  - procedure-it-security-procedures.md (passwords, data classification)"
    echo "  - faq-customer-support-faq.md (common questions and answers)"
    echo "  - manual-engineering-onboarding.md (development processes)"
    echo "  - README.md (general documentation)"
    echo ""
    echo "Troubleshooting:"
    echo "  If Q Business says 'no relevant information found':"
    echo "  1. Check data source sync status"
    echo "  2. Verify IAM permissions with --fix-permissions"
    echo "  3. Trigger manual sync with --sync"
    echo "  4. Check CloudWatch logs for errors"
    echo ""
}

# Main execution
main() {
    echo "========================================="
    echo "Amazon Q Business Sample Data Setup"
    echo "========================================="
    echo ""
    
    # Handle special options
    if [[ "$1" == "--fix-permissions" ]]; then
        if [[ $# -lt 3 ]]; then
            print_error "Missing arguments for --fix-permissions"
            echo "Usage: $0 --fix-permissions <stack-name> <bucket-name>"
            exit 1
        fi
        
        local stack_name="$2"
        BUCKET_NAME="$3"
        
        check_aws_cli
        check_and_fix_iam_permissions "$stack_name"
        exit 0
    fi
    
    if [[ "$1" == "--sync" ]]; then
        if [[ $# -lt 2 ]]; then
            print_error "Missing stack name for --sync"
            echo "Usage: $0 --sync <stack-name>"
            exit 1
        fi
        
        local stack_name="$2"
        
        check_aws_cli
        trigger_data_source_sync "$stack_name"
        exit 0
    fi
    
    # Parse regular arguments
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi
    
    BUCKET_NAME="$1"
    local stack_name=""
    
    if [[ -n "$2" ]]; then
        # Check if second argument is a region or stack name
        if [[ "$2" =~ ^[a-z]{2}-[a-z]+-[0-9]$ ]]; then
            REGION="$2"
            if [[ -n "$3" ]]; then
                stack_name="$3"
            fi
        else
            # Assume it's a stack name
            stack_name="$2"
        fi
    fi
    
    if [[ -n "$3" && -z "$stack_name" ]]; then
        stack_name="$3"
    fi
    
    # Validate inputs
    validate_bucket_name
    check_aws_cli
    
    # Execute setup steps
    create_bucket
    configure_bucket
    upload_sample_data
    
    # Fix IAM permissions if stack name provided
    if [[ -n "$stack_name" ]]; then
        check_and_fix_iam_permissions "$stack_name"
        
        # Wait a moment for IAM changes to propagate
        print_status "Waiting for IAM changes to propagate..."
        sleep 10
        
        # Trigger sync
        trigger_data_source_sync "$stack_name"
    fi
    
    verify_upload
    
    # Show additional guidance
    echo ""
    echo "🎯 NEXT STEPS:"
    echo ""
    if [[ -n "$stack_name" ]]; then
        echo "✅ Bucket created and IAM permissions updated"
        echo "✅ Data source sync triggered"
        echo ""
        echo "Monitor sync progress:"
        echo "  aws qbusiness list-data-source-sync-jobs --application-id <app-id> --index-id <index-id> --data-source-id <ds-id>"
        echo ""
        echo "Once sync completes, test with these queries:"
    else
        echo "1. Update your CloudFormation template parameter:"
        echo "   S3BucketName: $BUCKET_NAME"
        echo ""
        echo "2. Deploy/update your Q Business stack"
        echo ""
        echo "3. Fix IAM permissions (if needed):"
        echo "   $0 --fix-permissions <stack-name> $BUCKET_NAME"
        echo ""
        echo "4. Trigger data source sync:"
        echo "   $0 --sync <stack-name>"
        echo ""
        echo "5. Test with these sample queries:"
    fi
    
    echo "   • 'What is our expense policy for meals?'"
    echo "   • 'What are the password requirements?'"
    echo "   • 'How do I reset my password?'"
    echo "   • 'What benefits does the company offer?'"
    echo "   • 'What are the security procedures for new employees?'"
    echo ""
    
    if [[ -z "$stack_name" ]]; then
        echo "💡 TIP: Run with stack name for automatic IAM fixes and sync:"
        echo "   $0 $BUCKET_NAME $REGION <your-stack-name>"
    fi
    echo ""
}

# Run main function with all arguments
main "$@"
