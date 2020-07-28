# ElasticTranscoder

[CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) does not provide a way to create [ElasticTranscoder](https://docs.aws.amazon.com/elastictranscoder/latest/developerguide/introduction.html) Pipelines. This [Custom Resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) allows you to create such a Pipeline from within your Cloudformation template.

## Create the ElasticTranscoderPipeline Custom Resource

You first need to create the ElasticTranscoderPipeline Custom Resource by executing the stack:

```bash
sam build 
sam deploy --stack-name ElasticTranscoderPipeline
```

## Using the ElasticTranscoderPipeline

You can then reference the ElasticTranscoderPipeline in your CloudFormation template.

```bash
sam build --template-file template-example.yaml
sam deploy --stack-name ElasticTranscoder 
```

*BEWARE*: The example stack uses the [SamPolicyTemplateTranslator](https://github.com/awslabs/aws-cloudformation-templates) CloudFormation Macro.

## Cleaning up

```bash
aws cloudformation delete-stack --stack-name ElasticTranscoder
aws cloudformation delete-stack --stack-name ElasticTranscoderPipeline
```
