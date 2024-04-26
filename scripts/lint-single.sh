#!/usr/bin/env bash

set -eou pipefail

echo "Linting $1"
cfn-lint $1

echo "Success"
