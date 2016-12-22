#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  This file is licensed to you under the AWS Customer Agreement (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at http://aws.amazon.com/agreement/ .
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
#  See the License for the specific language governing permissions and limitations under the License.

from pygit2 import Keypair,credentials,discover_repository,Repository,clone_repository,RemoteCallbacks
from boto3 import client
import os,stat
import shutil
from zipfile import ZipFile
from ipaddress import ip_network, ip_address
import json
import logging
import hmac
import hashlib

### If true the function will not include .git folder in the zip
exclude_git=True

### If true the function will delete all files at the end of each invocation, useful if you run into storage space constraints, but will slow down invocations as each invoke will need to checkout the entire repo
cleanup=False

key='enc_key'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

s3 = client('s3')
kms = client('kms')

def write_key(filename,contents):
    logger.info('Writing keys to /tmp/...')
    mode = stat.S_IRUSR | stat.S_IWUSR
    umask_original = os.umask(0)
    try:
        handle = os.fdopen(os.open(filename, os.O_WRONLY | os.O_CREAT, mode), 'w')
    finally:
        os.umask(umask_original)
    handle.write(contents+'\n')
    handle.close()

def get_keys(keybucket,pubkey,update=False):
    if not os.path.isfile('/tmp/id_rsa') or not os.path.isfile('/tmp/id_rsa.pub') or update:
        logger.info('Keys not found on Lambda container, fetching from S3...')
        enckey = s3.get_object(Bucket=keybucket,Key=key)['Body'].read()
        privkey = kms.decrypt(CiphertextBlob=enckey)['Plaintext']
        write_key('/tmp/id_rsa',privkey)
        write_key('/tmp/id_rsa.pub',pubkey)
    return Keypair('git','/tmp/id_rsa.pub','/tmp/id_rsa','')

def init_remote(repo, name, url):
    remote = repo.remotes.create(name, url, '+refs/*:refs/*')
    return remote

def create_repo(repo_path, remote_url, creds):
    if os.path.exists(repo_path):
            logger.info('Cleaning up repo path...')
            shutil.rmtree(repo_path)
    repo = clone_repository(remote_url, repo_path, callbacks=creds )

    return repo

def pull_repo(repo, remote_url, creds):
    remote_exists = False
    for r in repo.remotes:
        if r.url == remote_url:
            remote_exists = True
            remote = r
    if not remote_exists:
        remote = repo.create_remote('origin',remote_url)
    logger.info('Fetching and merging changes...')
    remote.fetch(callbacks=creds)
    remote_master_id = repo.lookup_reference('refs/remotes/origin/master').target
    repo.checkout_tree(repo.get(remote_master_id))
    master_ref = repo.lookup_reference('refs/heads/master')
    master_ref.set_target(remote_master_id)
    repo.head.set_target(remote_master_id)
    return repo

def zip_repo(repo_path,repo_name):
    logger.info('Creating zipfile...')
    zf = ZipFile('/tmp/'+repo_name.replace('/','_')+'.zip','w')
    for dirname, subdirs, files in os.walk(repo_path):
        if exclude_git:
            try:
                subdirs.remove('.git')
            except ValueError:
                pass
        zdirname = dirname[len(repo_path)+1:]
        zf.write(dirname,zdirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename),os.path.join(zdirname, filename))
    zf.close()
    return '/tmp/'+repo_name.replace('/','_')+'.zip'

def push_s3(filename,repo_name,outputbucket):
    s3key='%s/%s' % (repo_name,filename.replace('/tmp/',''))
    logger.info('pushing zip to s3://%s/%s' % (outputbucket,s3key))
    data=open(filename,'rb')
    s3.put_object(Bucket=outputbucket,Body=data,Key=s3key)
    logger.info('Completed S3 upload...')

def lambda_handler(event,context):
    keybucket=event['context']['key-bucket']
    outputbucket=event['context']['output-bucket']
    pubkey=event['context']['public-key']
    ### Source IP ranges to allow requests from, if the IP is in one of these the request will not be chacked for an api key
    ipranges=[]
    for i in event['context']['allowed-ips'].split(','):
        ipranges.append(ip_network(u'%s' % i))
    ### APIKeys, it is recommended to use a different API key for each repo that uses this function
    apikeys=event['context']['api-secrets'].split(',')
    ip = ip_address(event['context']['source-ip'])
    secure=False
    for net in ipranges:
        if ip in net:
            secure=True
    if 'X-Gitlab-Token' in event['params']['header'].keys():
        if event['params']['header']['X-Gitlab-Token'] in apikeys:
            secure=True
    if 'X-Git-Token' in event['params']['header'].keys():
        if event['params']['header']['X-Git-Token'] in apikeys:
            secure=True
    if 'X-Gitlab-Token' in event['params']['header'].keys():
        if event['params']['header']['X-Gitlab-Token'] in apikeys:
            secure=True
    if 'X-Hub-Signature' in event['params']['header'].keys():
        for k in apikeys:
            if hmac.new(str(k),str(event['context']['raw-body']),hashlib.sha1).hexdigest() == str(event['params']['header']['X-Hub-Signature'].replace('sha1=','')):
                secure=True
    if not secure:
        logger.error('Source IP %s is not allowed' % event['context']['source-ip'])
        raise Exception('Source IP %s is not allowed' % event['context']['source-ip'])
    try:
        repo_name = event['body-json']['project']['path_with_namespace']
    except:
        repo_name = event['body-json']['repository']['full_name']
    try:
        remote_url = event['body-json']['project']['git_ssh_url']
    except:
        try:
            remote_url = 'git@'+event['body-json']['repository']['links']['html']['href'].replace('https://','').replace('/',':',1)+'.git'
        except:
            remote_url = event['body-json']['repository']['ssh_url']
    repo_path = '/tmp/%s' % repo_name
    creds = RemoteCallbacks( credentials=get_keys(keybucket,pubkey), )
    try:
        repository_path = discover_repository(repo_path)
        repo = Repository(repository_path)
        logger.info('found existing repo, using that...')
    except:
        logger.info('creating new repo for %s in %s' % (remote_url, repo_path))
        repo = create_repo(repo_path, remote_url, creds)
    pull_repo(repo,remote_url,creds)
    zipfile = zip_repo(repo_path, repo_name)
    push_s3(zipfile,repo_name,outputbucket)
    if cleanup:
        logger.info('Cleanup Lambda container...')
        shutil.rmtree(repo_path)
        shutil.rm(zipfile)
        shutil.rm('/tmp/id_rsa')
        shutil.rm('/tmp/id_rsa.pub')
    return 'Successfully updated %s' % repo_name
