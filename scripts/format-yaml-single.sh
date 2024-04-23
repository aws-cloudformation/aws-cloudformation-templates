#!/usr/local/bin/bash
n=$(basename $1)
rain fmt $1 > /tmp/$n
mv /tmp/$n $1


