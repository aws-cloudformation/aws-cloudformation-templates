#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  This file is licensed to you under the AWS Customer Agreement (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at http://aws.amazon.com/agreement/ .
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
#  See the License for the specific language governing permissions and limitations under the License.

import boto3
from botocore.vendored import requests
import json
import logging

#Set to False to allow self-signed/invalid ssl certificates
verify=False

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

s3_client = boto3.client('s3')
def lambda_handler(event, context):
    OAUTH_token=event['context']['git-token']
    OutputBucket=event['context']['output-bucket']
    temp_archive = '/tmp/archive.zip'
    # Identify git host flavour
    hostflavour='generic'
    if 'X-Hub-Signature' in event['params']['header'].keys():
        hostflavour='githubent'
    elif 'X-Gitlab-Event' in event['params']['header'].keys():
        hostflavour='gitlab'
    elif 'User-Agent' in event['params']['header'].keys():
        if event['params']['header']['User-Agent'].startswith('Bitbucket-Webhooks'):
            hostflavour='bitbucket'
    headers={}
    if hostflavour == 'githubent':
        archive_url = event['body-json']['repository']['archive_url']
        owner = event['body-json']['repository']['owner']['name']
        name = event['body-json']['repository']['name']
        # replace the code archive download and branch reference placeholders
        archive_url= archive_url.replace('{archive_format}','zipball').replace('{/ref}','/master')
        # add access token information to archive url
        archive_url= archive_url+'?access_token='+OAUTH_token
    elif hostflavour == 'gitlab':
        # https://gitlab.com/jaymcconnell/gitlab-test-30/repository/archive.zip?ref=master
        archive_url = event['body-json']['project']['http_url'].replace('.git','/repository/archive.zip?ref=master')+'&private_token='+OAUTH_token
        owner = event['body-json']['project']['namespace']
        name = event['body-json']['project']['name']
    elif hostflavour == 'bitbucket':
        archive_url = event['body-json']['repository']['links']['html']['href']+'/get/master.zip'
        owner = event['body-json']['repository']['owner']['username']
        name = event['body-json']['repository']['name']
        r = requests.post('https://bitbucket.org/site/oauth2/access_token',data = {'grant_type':'client_credentials'},auth=(event['context']['oauth-key'], event['context']['oauth-secret']))
        if 'error' in r.json().keys():
            logger.error('Could not get OAuth token. %s: %s' % (r.json()['error'],r.json()['error_description']))
            raise Exception('Failed to get OAuth token')
        headers['Authorization'] = 'Bearer ' + r.json()['access_token']
    s3_archive_file = "%s/%s/%s_%s.zip" % (owner,name,owner,name)
    # download the code archive via archive url
    logger.info('Downloading archive from %s' % archive_url)
    r = requests.get(archive_url,verify=verify,headers=headers)
    with open(temp_archive, "wb") as codearchive:
        codearchive.write(r.content)
    # upload the archive to s3 bucket
    logger.info("Uploading zip to S3://%s/%s" % (OutputBucket,s3_archive_file))
    s3_client.upload_file(temp_archive,OutputBucket, s3_archive_file)
    logger.info('Upload Complete')
