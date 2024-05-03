#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Linting $1"

has_rain_directive=$(cat "${1}"| grep "\!Rain::")
if [ "$?" -eq 1 ]
then
    cfn-lint --config-file ${CONFIG_FILE} $1
else
    echo "$1 has a Rain directive, packaging first, which may break line numbers"
    rain pkg $1 | cfn-lint --config-file ${CONFIG_FILE}
fi

