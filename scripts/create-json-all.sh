#!/usr/bin/env bash
#
SCRIPT_DIR=$(dirname "$0")
find . -name "*.yaml" | grep -v "\.env" | xargs -n1 "${SCRIPT_DIR}/create-json-single.sh"

