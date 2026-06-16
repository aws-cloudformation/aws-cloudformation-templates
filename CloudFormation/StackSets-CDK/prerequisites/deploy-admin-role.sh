#!/bin/bash

# Deploy StackSet administration role in management account
# Usage: ./deploy-admin-role.sh --region <region>

while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            REGION="$2"
            shift 2
            ;;
        *)
            echo "Unknown option $1"
            echo "Usage: $0 --region <region>"
            exit 1
            ;;
    esac
done

if [ -z "$REGION" ]; then
    echo "Usage: $0 --region <region>"
    echo "Example: $0 --region us-east-1"
    exit 1
fi

CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'Unable to determine')

echo "Deploying StackSet administration role..."
echo "Management Account: $CURRENT_ACCOUNT"
echo "Region: $REGION"
echo ""

aws cloudformation deploy \
    --template-file prerequisites/stackset-administration-role.yaml \
    --stack-name StackSetAdministrationRole \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION