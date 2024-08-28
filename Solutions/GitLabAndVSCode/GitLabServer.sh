#!/bin/bash

set -eou pipefail

local_ip=$(ec2-metadata | grep "^local-ipv4: " | cut -d " " -f 2)

# Install cfn-signal
yum install -y aws-cfn-bootstrap

# Install postfix
yum install -y postfix
systemctl enable postfix
systemctl start postfix

# Get the yum repo
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.rpm.sh | sudo bash

# Install gitlab and run it on the local ip
export EXTERNAL_URL="http://$local_ip" 
yum install -y gitlab-ee

# Tell CloudFormation we're ready to go
# This is a variable for the Sub intrisic function, not a bash variable
cfn-signal -s true --stack ${AWS::StackName} --resource Server --region ${AWS::Region}


