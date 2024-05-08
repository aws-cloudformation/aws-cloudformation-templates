# Deploying CodeBuild and CodePipeline with CloudFormation

Managing the AWS developer tools with cloud formation helps speed up initial
environment and deployment setup processes. This example deploys a CodeCommit
Repository, two CodeBuild jobs, and then creates a CodePipeline which uses
continuous integration to run any time changes are pushed to the code commit
repository. The templates provided can be expanded to create multiple CodeBuild
jobs or add additional environments to the CodePipeline stages. Using these
CloudFormation templates will be considerably faster than working through the
required menus to deploy the jobs and pipelines through the AWS console.

## Cloud Formation Templates

This example contains two CloudFormation templates.

### codebuild-template.yml

This template must be deployed first as the cloudformation-codepipeline-template
has dependencies on the output of this template. This template deploys the
following resources

- An S3 storage account for holding build artifacts
- App-build CodeBuild project for running scripts and commands to build the
  application
- App-deploy CodeBuild Project for running scripts and commands to deploy the
  application
- Required IAM roles for the codebuild to create logs in cloudwatch and s3,
  create objects in s3, and create reports

## fullcd-codepipeline-template.yml

This template deploys the pipeline which is triggered on a commit to main. It
has 3 stages

1. app-build stage - executes the app-build CodeBuild job
2. Manual approval stage - requires manual approval
3. app-deploy stage - executes the app-deploy CodeBuild job

## Deploying and Testing

The following steps will use the
[AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
to deploy the cloud formation templates. If you are unfamiliar with using the
AWS CLI, you can execute the steps using the AWS console CloudFormation
deployment.

1. Set required variables

```
codebuild_stackname="cf-sample-codebuild"
codepipeline_stackName="cf-sample-codepipeline"
codebuild_template="cloudformation-codebuild-template.yml"
codepipeline_template="cloudformation-codepipeline-template.yml"
```

2. Deploy the CodeBuild cloud formation template
   `aws cloudformation create-stack --stack-name $codebuild_stackname --template-body file://$codebuild_template --capabilities CAPABILITY_NAMED_IAM`
    1. Clone the newly created code commit repository to a local folder. Replace
       repositoryCloneUrl with the HTTPs URL provided through CodeCommit
       `git clone <repositoryCloneUrl>`
    2. Add these files from this sample to the new repository (Copy and paste into
       the clone repository directory). This is required because CodeBuild needs to
       have a path to the CodeBuild spec files before it can run them
    3. Deploy the codepipeline
       `aws cloudformation create-stack --stack-name $codepipeline_stackName --template-body file://$codepipeline_template --parameters ParameterKey=CodeBuildStack,ParameterValue=$codebuild_stackname --capabilities CAPABILITY_NAMED_IAM`
    4. Update the readme or add a new file and push the changes to the main branch
       to trigger a pipeline execution

The cloud formation templates can also be deployed using the AWS console.

## Cleanup

Execute the following cloud formation commands to remove the created resources.
These resoources can also be removed through the AWS console

1. Empty the created S3 bucket
   `aws s3 rm s3://${codebuild_stackname}-bucket --recursive`
2. Execute the following AWS CLI commands to remove the created resources

```
aws cloudformation delete-stack --stack-name $codepipeline_stackName
aws cloudformation delete-stack --stack-name $codebuild_stackname
```

## Usage

- Leverage these templates as a starting point for creating CodePipelines with
  CodeBuild stages
- Create additional CodeBuild jobs for new environments in your application
- Use the sample reporting to see how test metrics are reported in CodeBuild
  jobs

## Authors

[Austin Mleziva](https://github.com/mleziva) - AWS Professional Services Cloud
Application Architect

## Appendix

### Command Reference

#### Setting Names

```
codebuild_stackname="cf-sample-codebuild"
codepipeline_stackName="cf-sample-codepipeline"
codebuild_template="cloudformation-codebuild-template.yml"
codepipeline_template="cloudformation-codepipeline-template.yml"
```

#### Creating Deployment Resources

```
aws cloudformation create-stack --stack-name $codebuild_stackname --template-body file://$codebuild_template --capabilities CAPABILITY_NAMED_IAM
aws cloudformation create-stack --stack-name $codepipeline_stackName --template-body file://$codepipeline_template --parameters ParameterKey=CodeBuildStack,ParameterValue=$codebuild_stackname --capabilities CAPABILITY_NAMED_IAM
```

#### Updating Deployment Resources

```
aws cloudformation update-stack --stack-name $codebuild_stackname --template-body file://$codebuild_template --capabilities CAPABILITY_NAMED_IAM
aws cloudformation update-stack --stack-name $codepipeline_stackName --template-body file://$codepipeline_template --parameters ParameterKey=CodeBuildStack,ParameterValue=$codebuild_stackname --capabilities CAPABILITY_NAMED_IAM
```

#### Deleting Deployment Resources

```
aws cloudformation delete-stack --stack-name $codepipeline_stackName
aws cloudformation delete-stack --stack-name $codebuild_stackname
```
