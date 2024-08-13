#!/bin/bash

set -eoux pipefail

rpm --import https://packages.microsoft.com/keys/microsoft.asc
sh -c 'echo -e "[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'

# https://github.com/amazonlinux/amazon-linux-2023/issues/397
sleep 10

local_ip=$(ec2-metadata | grep local-ipv4 | cut -d " " -f 2)
yum install -y code git
tee /etc/systemd/system/code-server.service <<EOF
[Unit]
Description=Start code server

[Service]
ExecStart=/usr/bin/code serve-web --port 8080 --host $local_ip --without-connection-token --accept-server-license-terms 
Restart=always
Type=simple
User=ec2-user

[Install]
WantedBy = multi-user.target
EOF

sudo tee /home/ec2-user/.config/code-server/config.yaml <<EOF
cert: false
auth: password
hashed_password: '$(echo "${Password}" | sudo npx argon2-cli -e)'
EOF

systemctl daemon-reload
systemctl enable --now code-server

# Install Node.js
sudo -u ec2-user -i <<EOF
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source .bashrc
nvm install 20.11.0
nvm use 20.11.0
EOF

