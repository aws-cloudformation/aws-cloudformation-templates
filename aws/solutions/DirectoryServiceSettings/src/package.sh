#!/usr/bin/env bash
set -e

# Builds a lambda package from a single Python 3 module with pip dependencies.
# This is a modified version of the AWS packaging instructions:
# https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-dependencies

# Set name of python script, excluding .py extension
SCRIPT_NAME="directory_settings_custom_resource"
SCRIPT_DIRECTORY=$(pwd)

# Clean-Up
rm -rf .package .DS_Store "$SCRIPT_NAME".zip

create_package() {
    # Create .package directory
    mkdir -p .package
    # Add dependencies to .package, per the requirements.txt
    pip3 install --target .package --requirement requirements.txt
    # Add the python script to .package
    cp ./"${SCRIPT_NAME}".py .package
}

# Includes Python Script & Dependencies (if any)
make_zip() {
    cd .package
    zip -r ../"${SCRIPT_NAME}".zip ./*
    echo -e "\n### SCRIPT DIRECTORY:      ${SCRIPT_DIRECTORY}"
    echo -e "\n### LAMBDA ZIP FILE:       ${SCRIPT_NAME}.zip"
    cd ..
}

create_package
make_zip

echo -e "### LAMBDA PACKAGE SIZE:   $(du -sh .package)"
