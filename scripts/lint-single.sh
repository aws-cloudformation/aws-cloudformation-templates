#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$0")
CONFIG_FILE="${SCRIPT_DIR}/../.cfnlintrc"

echo "Linting $1"

is_macro=$(echo $1 | grep MacrosExamples)
if [ "$?" -eq 0 ]
then
    echo "$1 is a macro example, skipping it"
    exit 0
fi

has_rain_directive=$(cat "${1}"| grep "\!Rain::")
if [ "$?" -eq 1 ]
then
    cfn-lint --config-file ${CONFIG_FILE} $1
else
    echo "$1 has a Rain directive, packaging first, which may break line numbers"
    rain pkg -x $1 | cfn-lint --config-file ${CONFIG_FILE}
fi

