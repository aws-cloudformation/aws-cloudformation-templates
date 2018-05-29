# How to launch

```
S3_BUCKET=my-aws-codestar
REGION=us-west-2
aws s3 cp ./template.json s3://$(S3_BUCKET)/template.json
aws cloudformation create-stack \
  --stack-name awscodestar-strate \
  --template-url https://s3-$(REGION).amazonaws.com/$(S3_BUCKET)/template.json \
  --parameters \
    ParameterKey=ProjectId,ParameterValue=strate \
    ParameterKey=RepositoryName,ParameterValue=strate \
    ParameterKey=AppName,ParameterValue=strate \
  --capabilities CAPABILITY_NAMED_IAM
```