#!/bin/bash

set -eou pipefail

local_ip=$(ec2-metadata | grep "^local-ipv4: " | cut -d " " -f 2)

# Get the password from secrets manager
secret_string=$(aws secretsmanager get-secret-value --secret-id ${SecretName} | jq -r ".SecretString")

# Install cfn-signal
yum install -y aws-cfn-bootstrap

# Install go
yum install -y go

# Install nodejs
yum install -y nodejs

# Clone the repo and build Gitea
sudo -u ec2-user -i <<EOF
cd /home/ec2-user
mkdir /home/ec2-user/lib
touch /home/ec2-user/gitea.ini

git clone https://github.com/go-gitea/gitea
cd gitea
git checkout v1.22.1
TAGS="bindata sqlite sqlite_unlock_notify" make build
EOF


# Install was failing because of this for some reason
# This is the default and I think there is code that doesn't check to 
# see that we changed it.
mkdir /home/git
chown ec2-user /home/git

# Configure systemd
tee /etc/systemd/system/gitea.service <<EOF
[Unit]
Description=Gitea (Git with a cup of tea)
After=network.target
[Service]
RestartSec=2s
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/lib
ExecStart=/home/ec2-user/gitea/gitea web --port 8080 --config /home/ec2-user/gitea.ini
Restart=always
Environment=USER=ec2-user HOME=/home/git GITEA_WORK_DIR=/home/ec2-user/lib
[Install]
WantedBy=multi-user.target
EOF

# Configure gitea for headless install using the private IP
tee /home/ec2-user/gitea.ini << EOF
[database]
DB_TYPE = sqlite3

[security] 
INSTALL_LOCK = true

[server]
HTTP_ADDR = $local_ip

[service]
DISABLE_REGISTRATION = true

[service.explore]
REQUIRE_SIGNIN_VIEW = true
DISABLE_USERS_PAGE = true

[other]
ENABLE_SITEMAP = false
ENABLE_FEED = false
EOF

chown ec2-user /home/ec2-user/gitea.ini

systemctl daemon-reload
systemctl enable --now gitea

# Wait for the server to start up
sleep 30

# Create the admin user
cd /home/ec2-user/gitea
sudo -u ec2-user ./gitea --config /home/ec2-user/gitea.ini admin user create --username admin1 --password $secret_string --email ezbeard@amazon.com --admin --must-change-password=false

# Tell CloudFormation we're ready to go
# This is a variable for the Sub intrisic function, not a bash variable
cfn-signal -s true --stack ${AWS::StackName} --resource Server --region ${AWS::Region}

