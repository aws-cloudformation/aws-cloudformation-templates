#!/bin/bash
set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
echo "SCRIPT_DIR: ${SCRIPT_DIR}"

cd ${SCRIPT_DIR}/site

if [ "$#" -eq 4 ]
then
  echo "Editing config file..."

  APIGW=$1
  REDIRECT=$2
  DOMAIN=$3
  APPCLIENT=$4

  ESCAPED_APIGW=$(printf '%s\n' "${APIGW}" | sed -e 's/[\/&]/\\&/g')
  ESCAPED_REDIRECT=$(printf '%s\n' "${REDIRECT}" | sed -e 's/[\/&]/\\&/g')

  cat js/config-template.js | sed s/__APIGW__/"${ESCAPED_APIGW}"/ | sed s/__REDIRECT__/"${ESCAPED_REDIRECT}"/ | sed s/__DOMAIN__/"${DOMAIN}"/ | sed s/__APPCLIENT__/"$APPCLIENT"/ > js/config.js

  echo "Config file:"
  cat js/config.js
else
    echo "Number of args was $#"
fi

echo "Linting..."
npm run lint

echo "Building site..."
npm run build

