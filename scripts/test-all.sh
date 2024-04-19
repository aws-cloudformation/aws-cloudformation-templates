#!/usr/local/bin/bash

set -eou pipefail

CFN_LINT_IGNORE="-i W3005"

echo "Linting..."
cfn-lint "${CFN_LINT_IGNORE}" **/*.yaml
cfn-lint "${CFN_LINT_IGNORE}" **/*.json

echo "Guard..."
cfn-guard validate --data . \
    --rules scripts/rules.guard \
    --show-summary fail

echo "Success"
