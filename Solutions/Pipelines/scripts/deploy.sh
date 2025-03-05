#!/bin/bash

# Use this script to deploy changes to the application, 
# including changes to the CloudFormation stack.
# The pipeline is self-mutating, so it will restart 
# when it detects a change.

set -eou pipefail

APP_NAME=$1
TEAM_NAME=$2
STAGE_NAMES=$3
ACCOUNTS=$4

SCRIPT_DIR=$(dirname "$0")
$SCRIPT_DIR/build.sh

echo "Packaging and deploying to S3..."

mkdir -p dist/app
mkdir -p dist/web
mkdir -p dist/pipeline/multi-stage

cp templates/pipeline/multi-stage/buildspec.yml dist/pipeline/multi-stage/
cp app/buildspec.yml dist/app/

PIPELINE_ZIP=dist/pipeline-source.zip
rm -f $PIPELINE_ZIP
cd dist/pipeline/multi-stage
zip -r ../../../$PIPELINE_ZIP *
cd ../../..

function get_bucket {
    aws cloudformation describe-stacks \
        --stack-name $APP_NAME \
        --query "Stacks[].Outputs[*].[OutputKey,OutputValue]" \
        --output text | grep $1 | sed "s/$1\t//g"
}

PIPELINE_BUCKET=$(get_bucket PipelineSourceBucket)

echo "About to upload to pipeline bucket $PIPELINE_BUCKET"

aws s3 cp $PIPELINE_ZIP s3://$PIPELINE_BUCKET/

APP_ZIP=dist/app-source.zip
rm -f $APP_ZIP
cd dist/app
zip -r ../../$APP_ZIP *
cd ../..

APP_BUCKET=$(get_bucket AppSourceBucket)

echo "About to upload to app bucket $APP_BUCKET"

aws s3 cp $APP_ZIP s3://$APP_BUCKET/

echo "Done!"

