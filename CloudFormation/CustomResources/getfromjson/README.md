# getfromjson


## Overview

`getfromjson` is a module for Python that is meant to run in an [AWS
Lambda](https://aws.amazon.com/lambda/) function that, in turn, backs
one (or more) [AWS
CloudFormation](https://aws.amazon.com/cloudformation/) [custom
resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html)
that you declare and use to get a given value out of an input JSON
data structure and an input search argument you both provide.

For more information on Lambda-backed custom resources, see
[Lambda-backed custom
resources](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html).

There are two parts you'll need to set up. First, you set up the
infrastructure needed to support `getfromjson`: you do this with the
`src/getfromjson.yml` CloudFormation template, that describes the
following resources:

- the Lambda function and the `getfromjson.py` module for Python, that
  will back custom resource consumers; this function will be
  responsible for returning values from an input JSON data structure
  and search argument, that you both provide;

- the [AWS Identity and Access Management
  (IAM)](https://aws.amazon.com/iam/) [execution
  role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)
  for the Lambda function;

- the [Amazon CloudWatch
  Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
  log group for the Lambda function.

The _Setup_ section, further down in this document, shows you how to
create resources above, in a given AWS account and AWS region, by
using the template mentioned earlier to create a CloudFormation stack.

Next, you consume the Lambda function, that you previously created in
a given AWS account and AWS region, with custom resources that you
declare in other CloudFormation templates (that you'll use to create
new stacks) where you'll pass in both JSON data and a search argument
for the data. The `example-templates/` directory contains samples that
illustrate how to consume `getfromjson` with Lambda-backed custom
resources; the following snippet shows you an overview on how to
consume, in another template, the Lambda function (the example below
consumes custom resources' values in the `Outputs` section of the
template, but you can consume such values also from properties of
other resources you describe in the `Resources` section of the
template):

```
Resources:
  GetFromJsonCustomResourceSampleGetFromList:
    Type: Custom::GetFromJson
    Properties:
      ServiceTimeout: 1
      ServiceToken: !ImportValue Custom-GetFromJson
      json_data: '["test0", "test1", "test2"]'
      search: '[2]'

  GetFromJsonCustomResourceSampleGetFromMap:
    Type: Custom::GetFromJson
    Properties:
      ServiceTimeout: 1
      ServiceToken: !ImportValue Custom-GetFromJson
      json_data: '{"test": {"test1": ["x", "y"]}}'
      search: '["test"]["test1"][1]'

Outputs:
  GetFromJsonCustomResourceSampleGetFromListValue:
    Value: !GetAtt GetFromJsonCustomResourceSampleGetFromList.Data

  GetFromJsonCustomResourceSampleGetFromMapValue:
    Value: !GetAtt GetFromJsonCustomResourceSampleGetFromMap.Data
```

whereas the `GetFromJsonCustomResourceSampleGetFromListValue` and
`GetFromJsonCustomResourceSampleGetFromMapValue` outputs, once you'll
create the stack, will show `test2` and `y` respectively as the
returned values.

Note also the `ServiceToken: !ImportValue Custom-GetFromJson` line,
that the example above uses to tell the custom resource what is the
[Amazon Resource Name
(ARN)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns.html)
of the Lambda function that backs the custom resource itself. The
Lambda function's ARN is
[exported](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-exports.html)
in the `getfromjson` template with the `Custom-GetFromJson` export
name: in the example above, you use the `Fn::ImportValue` [intrinsic
function](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html)
to reference the ARN from the export.

For more information on CloudFormation custom resources in a
CloudFormation template, see the `AWS::CloudFormation::CustomResource`
[reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-customresource.html).


## Input and output: values and limits

The following are supported input and output values:

- input:

  - `json_data`:

    - `json_data` maximum length: 4,096 bytes;

    - map keys can contain alphanumeric characters, dashes, and
      underscore characters;

    - map values can contain Unicode characters;

  - `search`:

    - `search` maximum length: 256 bytes;

    - map keys can contain alphanumeric characters, dashes, and
      underscore characters;

    - list indexes must be integers (such as, `[0]` instead of
      `["0"]`);

- output:

    - custom resource response: 4,096 bytes maximum; this is a
      CloudFormation quota - for more information, see _Custom
      resource response_ in [Understand CloudFormation
      quotas](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html);

    - returned value can contain Unicode characters;

    - returned value type is represented as a Unicode string.


## Setup

Install [rain](https://github.com/aws-cloudformation/rain), that
you'll use to create CloudFormation stacks to manage resources. When
ready, create the Lambda function, its execution role and log group,
in a given AWS account and AWS region (the example below uses
`us-east-1` as the AWS region; change this value as needed); such
resources will be backing the custom resource consumer:

```
rain deploy src/getfromjson.yml getfromjson \
    --region us-east-1
```

Note that the `TagName` parameter for the `getfromjson.yml` template
is optional, and you can omit it if needed: its value defaults to
`GetFromJson`. `TagName` is used to add a tag called `Name`, with the
value for the `TagName` parameter, to resources that the template
describes (the Lambda function that backs relevant custom resources,
the function's execution role, and the function's log group).


## Usage

Please make sure to follow the _Setup_ section above before
continuing. When ready, create a CloudFormation stack that uses an
example template showing you how to invoke the Lambda function (that
you created earlier) that backs up the custom resources you'll use to
extract values from example JSON input (extracted values will be
available in the `Outputs` section for the example stack you'll
create; note that you can also choose to consume such values from
properties of other resources you describe in the `Resources` section
of the template):

```
rain deploy example-templates/getfromjson-consumer.yml getfromjson-consumer \
    --region us-east-1
```


## Development

Install the [AWS Serverless Application Model Command Line Interface
(AWS SAM CLI)
](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli.html)
in your workstation. When done, refer to the documentation on
[Installing Docker to use with the AWS SAM
CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-docker.html).

Install [rain](https://github.com/aws-cloudformation/rain), that
you'll use to create CloudFormation stacks to manage, on your behalf,
the resources you'll need.

Next, create and activate a [virtual
environment](https://docs.python.org/3/library/venv.html) for Python
using the following commands:

```
python -m venv venv
source venv/bin/activate
```

Next, install the following Python module(s) in your activated
environment:

```
python -m pip install --upgrade -r requirements-dev.txt
```

To run unit tests for `getfromjson` on your machine, use the following
command:

```
pytest --cov
```

To speed up the development lifecycle, you can locally invoke the
Lambda function code, and pass input events for your test use cases
(the unit tests for `getfromjson` do something similar as well, and by
invoking the Lambda function locally you add an integration testing
flavor to your development lifecycle). To do so, run the following
command from the root level of the project:

```
./run-local-invoke
```

The script above uses the SAM CLI to invoke the Lambda function code
locally on your machine; you'll need to have Docker installed and
running. The SAM CLI uses the content of the `template.yml` file in
the `src` directory to determine which settings to use for aspects
that include which `Runtime` to use, and the `MemorySize`: if you'll
need to adjust some of these values, make sure you reflect your
changes also in relevant parts of the `src/getfromjson.yml`
CloudFormation template; note that the value for `Handler` though
needs to have a different prefix depending on the file you use (it
should be `Handler: getfromjson.lambda_handler` in the SAM template,
and `Handler: index.lambda_handler` in the CloudFormation template).

Note: the code for `getfromjson`, by default, uses the `INFO` logging
level - you'll need to update the following line and use a different
logging level (such as, `logging.DEBUG`) when developing and
troubleshooting the code):

```
LOGGER.setLevel(logging.INFO)
```

When ready to create the infrastructure for `getfromjson`, use the
following commands to do so (the example below uses `us-east-1` as the
AWS region; change this value as needed):

```
pylint src/ \
    && mypy \
    && pytest --cov \
    && bandit -c bandit.yaml -r src/ \
    && rain deploy src/getfromjson.yml getfromjson \
        --region us-east-1
```

To create a stack with example custom resource consumers, run the
following command:

```
rain deploy example-templates/getfromjson-consumer.yml getfromjson-consumer \
    --region us-east-1
```
