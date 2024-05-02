#!/usr/bin/env bash
#
SCRIPT_DIR=$(dirname "$0")
find aws/services -name "*.yaml" | xargs -n1 "${SCRIPT_DIR}/create-json-single.sh"
# TODO aws/solutions, community

