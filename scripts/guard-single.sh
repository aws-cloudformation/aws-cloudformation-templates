#!/usr/bin/env bash
#
# This script runs guard against $1
#
set -eou pipefail

SCRIPT_DIR=$(dirname "$0")

echo "Running cfn-guard on $1 using ${SCRIPT_DIR}/rules.guard"

cfn-guard validate --data $1 \
    --rules ${SCRIPT_DIR}/rules.guard \
    --show-summary fail \
    --type CFNTemplate

