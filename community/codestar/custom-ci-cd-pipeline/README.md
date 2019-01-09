# A CodeBuild and CodePipeline template for Containerized Application

This template creates a custom CodePipeline pipeline for continuous integration and continuous delivery, for *two environments* named `staging` and `production`.

## Steps

1. Retrieve source: fetches the latest version of a branch from a CodeCommit repository.
2. Build staging: builds the project using CodeBuild by executing the `buildspec.yml` file.
3. Deploy staging: deploys the output of step 2 using CodeBuild by executing the `deployspec.yml` file.
4. Manual approval.
5. Build production: builds the project using CodeBuild by executing the `buildspec.yml` file.
6. Deploy production: deploys the output of step 5 using CodeBuild by executing the `deployspec.yml` file.

## CodeCommit repository
You need to create the CodeCommit repository before creating the stack, in the same AWS region as where you are creating the pipeline. The repository name is given as a parameter to the stack.

## Environment variable

In steps 2 and 3 an `ENVIRONMENT=staging` variable will be set, while for steps 5 and 6 that will be `ENVIRONMENT=production`. This means that you can customize `buildspec.yml` and `deployspec.yml` files to behave differently between environments.

```
if [ "${ENVIRONMENT}" = "production" ]; then
  # Build/deploy for production
else
  # Build/deploy for staging
fi
```

Both `buildspec.yml` and `deployspec.yml` files are run in CodeBuild projects. Read [this page](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html) for more information about the syntax to use.

*Important note:* in steps 2 and 5 you need to add `deployspec.yml` in `artifacts.files` section of the `buildspec.yml` among other output files in order for deployments to function.

```
artifacts:
  files:
    - ....
    - deployspec.yml
```

## CodeBuild role

If you need to perofm an action in your build or deployment phase which requires particular permissions you can add a [policy](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-policy.html) to the IAM role used by the CodeBuild projects. The role ARN is exported with this name: `${AWS::StackName}CodeBuildRoleArn`.

## Author
Egidio Caprino
egidio.caprino@gmail.com
[@EgidioCaprino](https://twitter.com/EgidioCaprino)
[LinkedIn](https://www.linkedin.com/in/egidio-caprino-3042b476/)
