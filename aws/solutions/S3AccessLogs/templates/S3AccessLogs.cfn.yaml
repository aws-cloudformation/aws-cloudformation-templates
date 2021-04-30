AWSTemplateFormatVersion: 2010-09-09
Description: >-
  This template creates an Amazon S3 bucket that will be used for storing S3 server access logs.
Metadata:
  AWS::CloudFormation::Interface:
    ParameterGroups:
      - Label:
          default: S3 Server Access Logs Configuration
        Parameters:
          - S3AccessLogsBucketName
    ParameterLabels:
      S3AccessLogsBucketName:
        default: S3 Server Access Logs Bucket Name
Parameters:
  S3AccessLogsBucketName:
    AllowedPattern: '^$|^(?=^.{3,63}$)(?!.*[.-]{2})(?!.*[--]{2})(?!^(?:(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(?!$)|$)){4}$)(^(([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$)'
    ConstraintDescription:
      S3 bucket name can include numbers, lowercase letters, uppercase letters, and hyphens (-). It cannot start or end with a hyphen (-).
    Default: ''
    Description:
      (Optional) S3 Server Access Logs bucket name for where Amazon S3 should store server access log files. S3 bucket name can include numbers,
      lowercase letters, uppercase letters, and hyphens (-). It cannot start or end with a hyphen (-). If empty, a new S3 bucket will be created as a
      destination for S3 server access logs, it will follow the format, aws-s3-access-logs-<account>-<region>
    Type: String
Conditions:
  S3AccessLogsBucketNameCondition: !Not [!Equals [!Ref S3AccessLogsBucketName, '']]
Resources:
  S3AccessLogsBucket:
    Metadata:
      cfn_nag:
        rules_to_suppress:
          - id: W35
            reason:
              Amazon S3 server access logs not enabled on this bucket, as this bucket is the target for storing all Amazon S3 server access logs.
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !If
        - S3AccessLogsBucketNameCondition
        - !Ref S3AccessLogsBucketName
        - !Sub aws-s3-access-logs-${AWS::AccountId}-${AWS::Region}
      AccessControl: LogDeliveryWrite
      PublicAccessBlockConfiguration:
        BlockPublicAcls: True
        BlockPublicPolicy: True
        IgnorePublicAcls: True
        RestrictPublicBuckets: True
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      VersioningConfiguration:
        Status: Enabled
  S3AccessLogsBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref S3AccessLogsBucket
      PolicyDocument:
        Statement:
          - Sid: DenyNonSSLRequests
            Effect: Deny
            Action: s3:*
            Resource:
              - !Sub arn:${AWS::Partition}:s3:::${S3AccessLogsBucket}
              - !Sub arn:${AWS::Partition}:s3:::${S3AccessLogsBucket}/*
            Principal: '*'
            Condition:
              Bool:
                aws:SecureTransport: false
Outputs:
  S3AccessLogsBucketName:
    Description: S3 Server Access Logs Bucket Name
    Value: !Ref S3AccessLogsBucket
    Export:
      Name: !Sub '${AWS::StackName}-S3AccessLogsBucketName'
