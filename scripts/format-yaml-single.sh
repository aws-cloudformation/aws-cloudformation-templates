#!/usr/local/bin/bash
set -eou pipefail
echo $1
n=$(basename $1)
rain fmt $1 > /tmp/$n
mv /tmp/$n $1


