#!/bin/bash

set -eoux pipefail

local_ip=$(ec2-metadata | grep "^local-ipv4: " | cut -d " " -f 2)
echo "local_ip:$local_ip"

# Install the latest code-server from coder.com (not from yum)
export HOME=/root 
curl -fsSL https://code-server.dev/install.sh | bash

yum install -y argon2
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
echo "secret_string: $secret_string"

# Hash the password
hashed_password=$(echo -n $secret_string | argon2 saltiness -e)
echo "hashed_password: $hashed_password"

#TODO: Stop echoing the password

# Install Node.js and save the code-server config file
sudo -u ec2-user -i <<EOF
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source .bashrc
nvm install 20.11.0
nvm use 20.11.0
mkdir -p /home/ec2-user/.config/code-server
sudo tee /home/ec2-user/.config/code-server/config.yaml <<ENDCONFIG
cert: false
auth: password
hashed-password: ${hashed_password}
user-data-dir: /home/ec2-user
ENDCONFIG
EOF

systemctl daemon-reload
systemctl enable --now code-server


