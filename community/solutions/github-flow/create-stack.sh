STACK_NAME="${1}"
REPOSITORY_NAME="${2}"
S3_BUCKET="${3}"

aws cloudformation package \
  --template template.yml \
  --s3-bucket ${S3_BUCKET}  \
  --output-template-file packaged-template.yml

aws cloudformation deploy \
  --template-file packaged-template.yml \
  --stack-name "${STACK_NAME}" \
  --parameter-overrides "RepositoryName=${REPOSITORY_NAME}" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
