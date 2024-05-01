#!/usr/bin/env bash

set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Linting with config file ${CONFIG_FILE}"
cfn-lint --config-file ${CONFIG_FILE} **/*.yaml

echo "Guard..."
cfn-guard validate --data . \
    --rules ${SCRIPT_DIR}/rules.guard \
    --show-summary fail

echo "Running pylint on Python lambda functions..."
pylint aws/services/CloudFormation/MacrosExamples/Boto3/lambda/*.py
pylint aws/services/CloudFormation/MacrosExamples/Count/src/*.py
pylint aws/services/CloudFormation/MacrosExamples/DateFunctions.*py
pylint aws/services/CloudFormation/MacrosExamples/ExecutionRoleBuilder/lambda/*.py
pylint aws/services/CloudFormation/MacrosExamples/Explode/lambda/*.py
pylint aws/services/CloudFormation/MacrosExamples/PyPlate/*.py
pylint aws/services/CloudFormation/MacrosExamples/S3Objects/lambda/*.py
pylint aws/services/CloudFormation/MacrosExamples/StackMetrics/lambda/*.py
pylint aws/services/CloudFormation/MacrosExamples/StringFunctions/*.py

echo "Success"
