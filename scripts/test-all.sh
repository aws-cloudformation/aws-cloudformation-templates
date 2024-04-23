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

echo "Success"
