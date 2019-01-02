#!/bin/bash

# Thx to @sengledo ;)

if [ -z "${ARTIFACT_BUCKET}" ]; then
    echo "This deployment script needs an S3 bucket to store CloudFormation artifacts."
    echo "You can also set this by doing: export ARTIFACT_BUCKET=my-bucket-name"
    echo
    read -p "S3 bucket to store artifacts: " ARTIFACT_BUCKET
fi

MACRO_NAME=$(basename $(pwd))

aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket ${ARTIFACT_BUCKET} \
    --output-template-file packaged.yaml

aws cloudformation deploy \
    --stack-name ${MACRO_NAME}-macro \
    --template-file packaged.yaml \
    --capabilities CAPABILITY_IAM

aws cloudformation deploy \
    --stack-name ${MACRO_NAME}-test \
    --template-file test.yaml \
    --capabilities CAPABILITY_IAM
