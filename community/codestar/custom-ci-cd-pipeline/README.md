# custom-ci-cd-pipeline

This template creates a custom CodePipeline pipeline for continuous integration and continuous delivery, for *two environments* named `staging` and `production`.

## Steps
1. Source: fetches the a user-defined branch from a CodeCommit repository.
2. Build staging: builds the project using CodeBuild by executing the `buildspec.yml` file.
3. Staging deployment: deploys the output of step 2 using CodeBuild by executing the `deployspec.yml` file.
4. Manual approval.
5. Build production: builds the project using CodeBuild by executing the `buildspec.yml` file.
6. Staging deployment: deploys the output of step 5 using CodeBuild by executing the `deployspec.yml` file.

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

*Important note:* in steps 2 and 5 you need to add `deployspec.yml` in `artifacts.files` section, among other output files.

```
artifacts:
  files:
    - ....
    - deployspec.yml
```
