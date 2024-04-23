#!/usr/bin/env bash

set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Linting..."
cfn-lint --config-file ${CONFIG_FILE} -- $1

echo "Guarding..."
cfn-guard validate --data $1 --rules ${SCRIPT_DIR}/rules.guard --show-summary fail

echo "Success"
