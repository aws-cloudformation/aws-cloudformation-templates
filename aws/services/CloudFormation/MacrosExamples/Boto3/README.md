# How to install and use the Boto3 macro in your AWS account

The `Boto3` macro adds the ability to create CloudFormation resources that represent operations performed by [boto3](http://boto3.readthedocs.io/). Each `Boto3` resource represents one function call.

A typical use case for this macro might be, for example, to provide some basic configuration of resources.

## Deploying

1. You will need an S3 bucket to store the CloudFormation artifacts:
    * If you don't have one already, create one with `aws s3 mb s3://<bucket name>`

2. Package the CloudFormation template. The provided template uses [the AWS Serverless Application Model](https://aws.amazon.com/about-aws/whats-new/2016/11/introducing-the-aws-serverless-application-model/) so must be transformed before you can deploy it.

    ```shell
    aws cloudformation package \
        --template-file macro.template \
        --s3-bucket <your bucket name here> \
        --output-template-file packaged.template
    ```

3. Deploy the packaged CloudFormation template to a CloudFormation stack:

    ```shell
    aws cloudformation deploy \
        --stack-name boto3-macro \
        --template-file packaged.template \
        --capabilities CAPABILITY_IAM
    ```

4. To test out the macro's capabilities, try launching the provided example template:

    ```shell
    aws cloudformation deploy \
        --stack-name boto3-macro-example \
        --template-file example.template
    ```

## Usage

To make use of the macro, add `Transform: Boto3` to the top level of your CloudFormation template.

Here is a trivial example template that adds a readme file to a new CodeCommit repository:

```yaml
Transform: Boto3
Resources:
  Repo:
    Type: AWS::CodeCommit::Repository
    Properties:
      RepositoryName: my-repo

  AddReadme:
    Type: Boto3::CodeCommit.put_file
    Mode: Create
    Properties:
      repositoryName: !GetAtt Repo.Name
      branchName: master
      fileContent: "Hello, world!"
      filePath: README.md
      commitMessage: Add a readme file
      name: CloudFormation
```

## Features

### Resource type

The resource `Type` is used to identify a [boto3 client](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/clients.html) and the method of that client to execute.

The `Type` must start with `Boto3::` and be followed by the name of a client, a `.` and finally the name of a method.

The client name will be converted to lower case so that you can use resource names that look similar to other CloudFormation resource types.

Examples:
* `Boto3::CodeCommit.put_file`
* `Boto3::IAM.put_user_permissions_boundary`
* `Boto3::EC2.create_snapshot`

### Resource mode

The resource may contain a `Mode` property which specifies whether the boto3 call should be made on `Create`, `Update`, `Delete` or any combination of those.

The `Mode` may either be a string or a list of strings. For example:

* `Mode: Create`
* `Mode: Delete`
* `Mode: [Create, Update]`

### Resource properties

The `Properties` of the resource will be passed to the specified boto3 method as arguments. The name of each property needs to match those defined in the `Boto3` library, they are therefore case sensitive.

#### Special properties

There are some properties that enable special functionality when used. They have been designed to enhance the capabilties of the Macro to mimic standard CloudFormation resources. The use of these enables resources to the be created by CloudFormation that are not yet supported within CloudFormation itself but are supprted in `Boto3`

* _CustomName (optional)

  This property is used to mimic the automatic naming capability of supported CloudFormation resources. The value supplied is the name of the `Boto3` property that you wish to be populated with a unique randomly generated name. If the corresponding property is not supplied or suppiled as an empty string the name generated will be of the form:

  `<StackName>-<LogicalResourceId>-<A random 12 alphumermic string>`

  If the corresponding property is suplpied in addition to the `_CustomName` property then the name generated will use this property in place of the `LogicalResourceid`

  Finally if the `_CustomName` property is not supplied at all no name will be generated and instead the values supplied in the `Boto3` function will be used.

* _Ref (optional)

  This property is used to set the value of the `PhysicalResourceId` of the created resource. It therefore allows the `Ref` function be used on the resource to retrieve it.

  This property takes a [jmespath](https://jmespath.org/) string expression which is applied to the response of the `Boto3` function to extract the required value.

* _GetAtt (optional)

  This property is used in a similar way to the `_Ref` property but intead of populating the value of the `Ref` CloudFormation function call it allows the setting of the values returned by the `Fn::GetAtt` function.

  This property takes a dict of string and [jmespath](https://jmespath.org/) string expression key pairs, which are applied to the response of the `Boto3` function to extract the required value.

There are examples in the section below of how each of these special properties can be used.

### Controlling the order of execution

You can use the standard CloudFormation property `DependsOn` when you need to ensure that your `Boto3` resources are executed in the correct order.

## Examples


The following resource:

```yaml
ChangeBinaryTypes:
  Type: Boto3::CloudFormation.execute_change_set
  Mode: [Create, Update]
  Properties:
    ChangeSetName: !Ref ChangeSet
    StackName: !Ref Stack
```

will result in running the equivalent of the following:

```python
boto3.client("cloudformation").execute_change_set(ChangeSetName=<value of ChangeSet>, StackName=<value of StackName>)
```

when the stack is created or updated.


The following resource:

***Stack Name: SampleStack***
```yaml
  Repo:
    Type: Boto3::CodeCommit.create_repository
    Mode: Create
    Properties:
      _CustomName: repositoryName
      _Ref: repositoryMetadata.repositoryId
      _GetAtt:
        Arn: repositoryMetadata.Arn
        CloneUrlHttp: repositoryMetadata.cloneUrlHttp
        CloneUrlSsh: repositoryMetadata.cloneUrlSsh
        Name: repositoryMetadata.repositoryName
      repositoryDescription: my-repo
```

will create a CodeCommit Repository with the following capabilties:

* `!Ref Repo` will return the repositoryName that was generated automatically (`SampleStack-`<u>Repo</u>`-A1B2C3D4E5F6`).
* `!GetAtt Repo.Arn` will return the repositoryMetadata.Arn value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.CloneUrlHttp` will return the repositoryMetadata.cloneUrlHttp value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.CloneUrlSsh` will return the repositoryMetadata.cloneUrlSsh value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.Name` will return the repositoryMetadata.repositoryName value from the `boto3.client('codedeploy').create_repository(...)` function call.


A slightly modified version (by adding the `_CustomName` defined property `repositoryName` value) of the same resource:

***Stack Name: SampleStack***
```yaml
  Repo:
    Type: Boto3::CodeCommit.create_repository
    Mode: Create
    Properties:
      _CustomName: repositoryName
      _Ref: repositoryMetadata.repositoryId
      _GetAtt:
        Arn: repositoryMetadata.Arn
        CloneUrlHttp: repositoryMetadata.cloneUrlHttp
        CloneUrlSsh: repositoryMetadata.cloneUrlSsh
        Name: repositoryMetadata.repositoryName
      repositoryName: MyRepo
      repositoryDescription: my-repo
```

will create a CodeCommit Repository with the following capabilties:

* `!Ref Repo` will return the repositoryName that was generated automatically (`SampleStack-`<u>MyRepo</u>`-A1B2C3D4E5F6`).
* `!GetAtt Repo.Arn` will return the repositoryMetadata.Arn value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.CloneUrlHttp` will return the repositoryMetadata.cloneUrlHttp value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.CloneUrlSsh` will return the repositoryMetadata.cloneUrlSsh value from the `boto3.client('codedeploy').create_repository(...)` function call.
* `!GetAtt Repo.Name` will return the repositoryMetadata.repositoryName value from the `boto3.client('codedeploy').create_repository(...)` function call.

## Author

[Steve Engledow](https://linkedin.com/in/stilvoid)  
Senior Solutions Builder  
Amazon Web Services
