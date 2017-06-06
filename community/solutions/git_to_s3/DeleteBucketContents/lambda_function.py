#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  This file is licensed to you under the AWS Customer Agreement (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at http://aws.amazon.com/agreement/ .
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
#  See the License for the specific language governing permissions and limitations under the License.

import cfnresponse
import traceback
import boto3

def lambda_handler(event,context):
    try:
        if event['RequestType'] == 'Delete':
            s3 = boto3.client('s3')
            # Delete KeyBucket contents
            print 'Getting KeyBucket objects...'
            s3objects = s3.list_objects_v2(Bucket=event["ResourceProperties"]["KeyBucket"])
            if 'Contents' in s3objects.keys():
                print 'Deleting KeyBucket objects %s...' % str([{'Key':key['Key']} for key in s3objects['Contents']])
                s3.delete_objects(Bucket=event["ResourceProperties"]["KeyBucket"],Delete={'Objects':[{'Key':key['Key']} for key in s3objects['Contents']]})
            # Delete Output bucket contents and versions
            print 'Getting OutputBucket objects...'
            objects=[]
            versions=s3.list_object_versions(Bucket=event["ResourceProperties"]["OutputBucket"])
            while versions:
                if 'Versions' in versions.keys():
                    for v in versions['Versions']:
                        objects.append({'Key':v['Key'],'VersionId': v['VersionId']})
                if 'DeleteMarkers'in versions.keys():
                    for v in versions['DeleteMarkers']:
                        objects.append({'Key':v['Key'],'VersionId': v['VersionId']})
                if versions['IsTruncated']:
                    versions=s3.list_object_versions(Bucket=event["ResourceProperties"]["OutputBucket"],VersionIdMarker=versions['NextVersionIdMarker'])
                else:
                    versions=False
            if objects != []:
                s3.delete_objects(Bucket=event["ResourceProperties"]["OutputBucket"],Delete={'Objects':objects})
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, '')
    except:
        print traceback.print_exc()
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')
