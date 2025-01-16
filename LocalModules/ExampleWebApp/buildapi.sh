#!/usr/bin/env bash

set -eou pipefail

SCRIPT_DIR=$(dirname "$0")
echo "SCRIPT_DIR: ${SCRIPT_DIR}"
cd $SCRIPT_DIR

function build() {
    echo "Building $1..."
    cd ../$1
    staticcheck .
    go vet .
    GOOS=linux GOARCH=amd64 go build -o bootstrap main.go
    mkdir -p ../../dist/$1
    zip ../../dist/$1/lambda-handler.zip bootstrap
}

cd api/resources/test

build test
build jwt


