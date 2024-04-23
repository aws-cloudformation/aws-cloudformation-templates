#!/usr/bin/env bash

set -eou pipefail

echo "Linting..."
cfn-lint

echo "Guard..."
cfn-guard validate --data . \
    --rules scripts/rules.guard \
    --show-summary fail

echo "Success"
