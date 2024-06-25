#!/usr/bin/env bash
set -eou pipefail

echo "Packaging common resources..."
rain pkg -x common-resources.yaml > common-resources-pkg.yaml

echo "Linting common resources..."
cfn-lint common-resources-pkg.yaml

echo "Packaging common resources stack set..."
rain pkg common-resources-stackset.yaml > common-resources-stackset-pkg.yaml

echo "Linting common resources stack set..."
cfn-lint common-resources-stackset-pkg.yaml



