#!/usr/bin/env bash
set -eou pipefail

GUARD_RULES=../../scripts/rules.guard

echo "Packaging common resources..."
rain pkg -x common-resources.yaml > common-resources-pkg.yaml

echo "Linting common resources..."
cfn-lint common-resources-pkg.yaml

echo "Guarding common resources..."
cfn-guard validate -d common-resources-pkg.yaml -r $GUARD_RULES

echo "Packaging common resources stack set..."
rain pkg common-resources-stackset.yaml > common-resources-stackset-pkg.yaml

echo "Linting common resources stack set..."
cfn-lint common-resources-stackset-pkg.yaml

echo "Guarding common resources stack set..."
cfn-guard validate -d common-resources-stackset-pkg.yaml -r $GUARD_RULES

echo "Linting log setup for target accounts..."
cfn-lint log-setup-target-accounts.yaml

echo "Guarding log setup for target acounts..."
cfn-guard validate -d log-setup-target-accounts.yaml -r $GUARD_RULES

echo "Packaging log setup for the management account..."
rain pkg log-setup-management.yaml > log-setup-management-pkg.yaml

echo "Linting log setup for the management account..."
cfn-lint log-setup-management-pkg.yaml

echo "Guarding log setup for the management account..."
cfn-guard validate -d log-setup-management-pkg.yaml -r $GUARD_RULES




