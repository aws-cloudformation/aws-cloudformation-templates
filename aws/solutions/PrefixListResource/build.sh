#! /bin/sh

# Figure out AWS profile to use
[[ -z "${AWS_PROFILE}" ]] && profile='default' || profile="${AWS_PROFILE}"
[[ -z "${2}" ]] && profile=$profile || profile="${2}"

# Figure out install region
[[ -z "${AWS_DEFAULT_REGION}" ]] && region='us-east-1' || region="${AWS_DEFAULT_REGION}"
[[ -z "${1}" ]] && region=$region || region="${1}"
account=`aws sts get-caller-identity --output text --query Account --profile ${profile}`
bucket_name="getpl-resource-${account}-${region}"
bucket_prefix='artifacts'

echo "Creating/validating bucket ${bucket_name}"
aws s3 mb s3://${bucket_name} \
  --region ${region} \
  --profile ${profile}

echo "Deploying function code to S3 location: ${bucket_name}/${bucket_prefix}"
aws cloudformation package \
  --template-file Templates/function-template.yaml \
  --s3-bucket ${bucket_name} \
  --s3-prefix 'artifacts' \
  --output-template-file Templates/packaged-function-template.yaml \
  --force-upload \
  --region ${region} \
  --profile ${profile}

echo "Deploying packaged template to stack in $region"
aws cloudformation deploy \
  --template-file Templates/packaged-function-template.yaml \
  --stack-name PrefixListCustomResource \
  --capabilities CAPABILITY_IAM \
  --region ${region} \
  --profile ${profile}

echo "Done"
