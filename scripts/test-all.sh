#!/usr/bin/env bash
#
# This script runs all tests. 
#
# It formats YAML templates using rain, creates a JSON version, lints, 
# runs a basic set of Guard rules, and runs pylint on function code.

set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Formatting YAML files..."
${SCRIPT_DIR}/format-yaml-all.sh

echo "Generating JSON files based on YAML..."
${SCRIPT_DIR}/create-json-all.sh

echo "Linting with config file ${CONFIG_FILE}"
find . -name "*.yaml" | grep -v "\.env" | xargs -n 1 ${SCRIPT_DIR}/lint-single.sh

echo "Guarding..."
${SCRIPT_DIR}/guard-all.sh
#cfn-guard validate --data **/*.yaml \
#    --rules ${SCRIPT_DIR}/rules.guard \
#    --show-summary fail \
#    --type CFNTemplate

# Don't run this from sub directories
p=$(pwd)
b=$(basename $p)
if [ "$b" == "aws-cloudformation-templates" ]
then
    echo "Running pylint on Python lambda functions..."
    MACROS="${SCRIPT_DIR}/../CloudFormation/MacrosExamples"
    RCFILE="--rcfile ${SCRIPT_DIR}/../.pylintrc"
    pylint $RCFILE $MACROS/Boto3/lambda/*.py
    pylint $RCFILE $MACROS/Count/src/*.py
    pylint $RCFILE $MACROS/DateFunctions/*.py
    pylint $RCFILE $MACROS/ExecutionRoleBuilder/lambda/*.py
    pylint $RCFILE $MACROS/Explode/lambda/*.py
    pylint $RCFILE $MACROS/PyPlate/*.py
    pylint $RCFILE $MACROS/S3Objects/lambda/*.py
    pylint $RCFILE $MACROS/StackMetrics/lambda/*.py
    pylint $RCFILE $MACROS/StringFunctions/*.py

    pylint $RCFILE IoT/reset_function.py

    pylint $RCFILE Solutions/ADConnector/src/adconnector_custom_resource.py
    pylint $RCFILE Solutions/DirectoryServiceSettings/src/directory_settings_custom_resource.py
    pylint $RCFILE APIGateway/handler.py
fi
