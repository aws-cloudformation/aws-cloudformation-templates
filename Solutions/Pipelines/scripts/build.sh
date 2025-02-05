#!/bin/bash

set -eou pipefail

mkdir -p dist/pipeline/multi-stage

function build {

    echo "Packaging $1"
    aws cloudformation package \
        --template-file templates/$1/template.yaml \
        --output-template-file dist/$1/template.yaml

    echo "Linting $1"
    cfn-lint dist/$1/template.yaml

}

build pipeline/multi-stage



