#!/usr/bin/env bash
#
# This script runs guard against all templates under the current directory.
#
set -eou pipefail

SCRIPT_DIR=$(dirname "$0")

cfn-guard validate --data . \
    --rules ${SCRIPT_DIR}/rules.guard \
    --show-summary fail \
    --type CFNTemplate

echo "Success"
