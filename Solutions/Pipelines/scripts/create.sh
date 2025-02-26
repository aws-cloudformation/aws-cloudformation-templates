#!/bin/bash

# Use this script to create the stack for the first time, 
# or to manually deploy changes to the stack without using
# the self-mutating pipeline.

set -eou pipefail

APP_NAME=$1
TEAM_NAME=$2
STAGE_NAMES=$3
ACCOUNTS=$4

SCRIPT_DIR=$(dirname "$0")
$SCRIPT_DIR/build.sh

echo "Deploying..."
aws cloudformation deploy \
    --stack-name $APP_NAME \
    --template-file dist/pipeline/multi-stage/template.yaml \
    --parameter-overrides \
        AppName=$APP_NAME \
        TeamName=$TEAM_NAME \
        StageNames=$STAGE_NAMES \
        Accounts=$ACCOUNTS \
    --capabilities CAPABILITY_IAM

echo "Done!"

