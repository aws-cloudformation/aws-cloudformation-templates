#!/usr/local/bin/bash
name=$(echo $1 | sed s/\.yaml/\.json/g)
echo Creating $name based on $1
rain fmt -j $1 > ${name}
