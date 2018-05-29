
STACK_NAME=demo
TEMPLATE_FILE=./template.yml
PIPELINE_NAME=pipeline-pipeline

login:
	aws configure < keys

validate: login
	aws cloudformation validate-template --template-body file://template.yml

get-pipeline-state: login
	aws codepipeline get-pipeline-state --name $(PIPELINE_NAME)

MONITOR_CMD="import sys,json; j=json.loads(sys.stdin.read());print('\n'.join(jj['stageName']+' '+jj['latestExecution']['status'] for jj in j['stageStates']))"
monitor-pipeline-state: login
	while true; do \
	date; aws codepipeline get-pipeline-state --name $(PIPELINE_NAME) | python -c $(MONITOR_CMD) ; echo; \
	sleep 2s ;\
	done

create-stack: login
	aws cloudformation deploy --template-file $(TEMPLATE_FILE) --stack-name $(STACK_NAME) --capabilities CAPABILITY_IAM --parameter-overrides ProjectId=$(STACK_NAME)

describe-stack: login
	aws cloudformation describe-stacks --stack-name $(STACK_NAME)
	aws cloudformation describe-stack-events --stack-name $(STACK_NAME) | less -S

clean: login
	aws configure < keys
	aws cloudformation delete-stack --stack-name $(STACK_NAME)
