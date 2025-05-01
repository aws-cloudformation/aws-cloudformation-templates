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

echo "Success!"

