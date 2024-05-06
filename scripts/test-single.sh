#!/usr/bin/env bash

set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Formatting YAML file..."
${SCRIPT_DIR}/format-yaml-single.sh $1

echo "Generating JSON file based on YAML..."
${SCRIPT_DIR}/create-json-single.sh $1

echo "Linting..."
${SCRIPT_DIR}/lint-single.sh $1

echo "Guarding..."
cfn-guard validate --data $1 --rules ${SCRIPT_DIR}/rules.guard --show-summary fail

echo "Success"
