.SHELLFLAGS = -c -e

.PHONY: all
all: packaged.yaml
	aws cloudformation deploy \
	  --template-file packaged.yaml \
	  --stack-name Hup \
	  --capabilities CAPABILITY_IAM \
	  --no-fail-on-empty-changeset \

packaged.yaml: template.yaml macro.py custom_resource.py
	aws cloudformation package \
	  --template-file template.yaml \
	  --s3-bucket $$(aws \
	    --output text \
	    --query StackResourceDetail.PhysicalResourceId \
	    cloudformation describe-stack-resource \
	    --stack-name Hup \
	    --logical-resource-id Bucket \
	  ) \
	  --output-template-file $@ \

.PHONY: check
check:
	-prettier --check $$(git ls-files --cached --others --exclude-standard)
	-yapf3 --diff --recursive .
