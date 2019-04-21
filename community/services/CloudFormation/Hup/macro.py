import os

import jmespath

path = jmespath.compile('Metadata."AWS::CloudFormation::Init"')
max_batch_size = jmespath.compile(
    'UpdatePolicy.AutoScalingRollingUpdate.MaxBatchSize')
min_successful_instances_percent = jmespath.compile(
    'UpdatePolicy.AutoScalingRollingUpdate.MinSuccessfulInstancesPercent')


def lambda_handler(event, context):
  resources = event['fragment']['Resources']
  for logical_id, resource in resources.copy().items():
    data = path.search(resource)
    if data is not None:
      action = {
          'Fn::Sub':
              f'/opt/aws/bin/cfn-init --region ${{AWS::Region}} --stack ${{AWS::StackName}} --resource {logical_id}'
      }
      parameters = dict(
          DocumentName='AWS-RunShellScript',
          Parameters=dict(commands=[action]),
          Targets=[
              dict(
                  Key='tag:aws:cloudformation:stack-name',
                  Values=[dict(Ref='AWS::StackName')],
              ),
              dict(
                  Key='tag:aws:cloudformation:logical-id',
                  Values=[logical_id],
              ),
          ],
          CloudWatchOutputConfig=dict(CloudWatchOutputEnabled=True),
      )
      # UpdatePolicy MaxBatchSize -> SendCommand MaxConcurrency and
      # UpdatePolicy MinSuccessfulInstancesPercent -> SendCommand
      # MaxErrors
      value = max_batch_size.search(resource)
      if value is not None:
        parameters['MaxConcurrency'] = value
      value = min_successful_instances_percent.search(resource)
      if value is not None:
        parameters['MaxErrors'] = f'{100 - value}%'
      resources[f'{logical_id}Hup'] = dict(
          Type='AWS::CloudFormation::CustomResource',
          Properties=dict(
              Metadata=data,
              ServiceToken=os.environ['CustomResourceFunction'],
              Service='ssm',
              Action='send_command',
              Parameters=parameters,
              Role=os.environ['SendCommandRole'],
          ),
      )
  return dict(
      status='SUCCESS',
      fragment=event['fragment'],
      requestId=event['requestId'],
  )
