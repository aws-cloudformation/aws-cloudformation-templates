#!/bin/bash
set -eou pipefail

APPNAME=cli-cfn-webapp
PROFILE=""
if [ "$#" -ne 1 ]; then
  echo "Using default profile"
else
  PROFILE="--profile $1"
fi

echo "Building API..."
./buildapi.sh

echo "Building Site..."
./buildsite.sh

echo "Packaging..."
aws cloudformation package $PROFILE \
    --s3-bucket ezbeard-rain-lambda \
    --template-file webapp.yaml --output-template-file webapp-pkg.yaml

echo "Linting..."
cfn-lint webapp-pkg.yaml

echo "Deploying..."
aws cloudformation deploy $PROFILE \
    --template-file webapp-pkg.yaml \
    --stack-name $APPNAME \
    --parameter-overrides AppName=$APPNAME \
    --capabilities CAPABILITY_IAM

echo "Rebuilding site with config..."
# Look up output values from the stack
outs=$(aws cloudformation describe-stacks $PROFILE --stack-name $APPNAME | jq -r ".Stacks[0].Outputs")
APIGW=$(echo $outs | jq -r '.[] | select(.OutputKey == "RestApiInvokeURL") | .OutputValue')
REDIRECT=$(echo $outs | jq -r '.[] | select(.OutputKey == "RedirectURI") | .OutputValue')
DOMAIN=$(echo $outs | jq -r '.[] | select(.OutputKey == "AppName") | .OutputValue')
APPCLIENT=$(echo $outs | jq -r '.[] | select(.OutputKey == "AppClientId") | .OutputValue')
CONTENTBUCKET=$(echo $outs | jq -r '.[] | select(.OutputKey == "ContentBucketName") | .OutputValue')
./buildsite.sh $APIGW $REDIRECT $DOMAIN $APPCLIENT

echo "Uploading site to s://$CONTENTBUCKET..."
aws s3 cp $PROFILE --recursive site/dist s3://$CONTENTBUCKET 

# TODO: Invalidate CloudFront distribution

echo "Success!"

