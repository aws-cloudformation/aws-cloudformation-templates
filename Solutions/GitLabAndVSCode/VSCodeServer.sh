#!/bin/bash

set -eou pipefail

local_ip=$(ec2-metadata | grep "^local-ipv4: " | cut -d " " -f 2)

# Install the latest code-server from coder.com (not from yum)
export HOME=/root 
curl -fsSL https://code-server.dev/install.sh | bash

# Install cfn-signal
yum install -y aws-cfn-bootstrap

#Install argon2 for hashing the vscode server password
yum install -y argon2

# Configure the service
tee /etc/systemd/system/code-server.service <<EOF
[Unit]
Description=Start code server

[Service]
ExecStart=/usr/bin/code-server --port 8080 --host $local_ip
Restart=always
Type=simple
User=ec2-user

[Install]
WantedBy = multi-user.target
EOF

# Get the password from secrets manager
secret_string=$(aws secretsmanager get-secret-value --secret-id ${SecretName} | jq -r ".SecretString")

# Hash the password
hashed_password=$(echo -n $secret_string | argon2 saltiness -e)

# Install Node.js
sudo -u ec2-user -i <<EOF
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source .bashrc
nvm install 20.11.0
nvm use 20.11.0
EOF

# Save the config file
mkdir -p /home/ec2-user/.config/code-server
sudo tee /home/ec2-user/.config/code-server/config.yaml <<ENDCONFIG
cert: false
auth: password
hashed-password: "$hashed_password"
user-data-dir: /home/ec2-user
ENDCONFIG

chown -R ec2-user /home/ec2-user/.config

systemctl daemon-reload
systemctl enable --now code-server

# Tell CloudFormation we're ready to go
# This is a variable for the Sub intrisic function, not a bash variable
cfn-signal -s true --stack ${AWS::StackName} --resource Server --region ${AWS::Region}


