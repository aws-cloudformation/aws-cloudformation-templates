#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  This file is licensed to you under the AWS Customer Agreement (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at http://aws.amazon.com/agreement/ .
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
#  See the License for the specific language governing permissions and limitations under the License.

import cfnresponse
import traceback
from os import chmod,mkdir
import sys
import boto3
from zipfile import ZipFile
from Crypto.PublicKey import RSA

def lambda_handler(event,context):
    try:
        if event['RequestType'] == 'Create':
            # Generate keys
            new_key = RSA.generate(2048)
            pub_key = new_key.publickey().exportKey(format='OpenSSH')
            priv_key = new_key.exportKey()
            # Encrypt private key
            kms = boto3.client('kms',region_name=event["ResourceProperties"]["Region"])
            enc_key = kms.encrypt(KeyId=event["ResourceProperties"]["KMSKey"],Plaintext=priv_key)['CiphertextBlob']
            f = open('/tmp/enc_key','wb')
            f.write(enc_key)
            f.close()
            # Upload priivate key to S3
            s3 = boto3.client('s3')
            s3.upload_file('/tmp/enc_key',event["ResourceProperties"]["KeyBucket"],'enc_key')
        else:
            pub_key = event['PhysicalResourceId']
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, pub_key)
    except:
        traceback.print_exc()
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')
