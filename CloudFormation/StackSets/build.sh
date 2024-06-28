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

echo "Linting log setup for target accounts..."
cfn-lint log-setup-target-accounts.yaml

echo "Packaging log setup for the management account..."
rain pkg log-setup-management.yaml > log-setup-management-pkg.yaml

echo "Linting log setup for the management account..."
cfn-lint log-setup-management-pkg.yaml





