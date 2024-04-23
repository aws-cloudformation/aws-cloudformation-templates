#!/usr/local/bin/bash
#
SCRIPT_DIR=$(dirname "$0")
find . -name "*.yaml" | xargs -n1 "${SCRIPT_DIR}/create-json-single.sh"

