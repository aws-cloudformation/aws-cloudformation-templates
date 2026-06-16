#!/bin/bash

# Deploy StackSet execution role in target account
# Usage: ./deploy-execution-role.sh --management-account-id <account-id> --region <region>

while [[ $# -gt 0 ]]; do
    case $1 in
        --management-account-id)
            MANAGEMENT_ACCOUNT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 --management-account-id <account-id> --region <region>"
            exit 1
            ;;
    esac
done

if [ -z "$MANAGEMENT_ACCOUNT_ID" ] || [ -z "$REGION" ]; then
    echo "Usage: $0 --management-account-id <account-id> --region <region>"
    echo "Example: $0 --management-account-id 284051759444 --region us-east-1"
    exit 1
fi

CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'Unable to determine')

echo "Deploying StackSet execution role..."
echo "Target Account: $CURRENT_ACCOUNT"
echo "Management Account: $MANAGEMENT_ACCOUNT_ID"
echo "Region: $REGION"
echo ""

aws cloudformation deploy \
    --template-file prerequisites/stackset-execution-role.yaml \
    --stack-name StackSetExecutionRole \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides AdministrationAccountId=$MANAGEMENT_ACCOUNT_ID \
    --region $REGION