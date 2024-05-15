#!/usr/bin/env bash
set -eou pipefail
echo $1
n=$(basename $1)
rain fmt -u $1 > /tmp/$n
mv /tmp/$n $1
