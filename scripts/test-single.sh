#!/usr/bin/env bash

set -eou pipefail

echo "Linting..."
cfn-lint -- $1

echo "Guarding..."
cfn-guard validate --data $1 --rules scripts/rules.guard --show-summary fail

echo "Success"
