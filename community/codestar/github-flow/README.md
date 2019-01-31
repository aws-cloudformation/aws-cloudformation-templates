# GitHub flow in AWS CodeStar

Features:
- Checks PRs as soons as they are created in CodeCommit
- Checks a PR every time it is updated
- Only checks PRs that can be merged

## Steps
1. Create the repository in CodeCommit (or use an existing one in next steps)
2. Run `create-stack stackName repoName s3Bucket` where
  - `stackName` is the name you want to give to the stack in CloudFormation
  - `repoName` is the name of the repository you created in CodeCommit
  - `s3Bucket` is an S3 bucket where Lambda code will be uploaded before being deployed
3. Edit the just created stack in CloudFormation by changing the `CodeBuildImage` parameter if needed
4. Add `buildspec.yml` to your project. Check out [this page](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html) if you don't know how to fill this file. In the `post_build` you can have check wheter the validation failed or not and act accordingly. For instance, you might want to post a message on Slack:
``` bash
post_build:
  commands:
    - |
      if [ $CODEBUILD_BUILD_SUCCEEDING -ne 1 ]; then
        prUrl="https://${AWS_REGION}.console.aws.amazon.com/codesuite/codecommit/repositories/${REPOSITORY_NAME}/pull-requests/${PULL_REQUEST_ID}/details?region=${AWS_REGION}"
        buildUrl="https://${AWS_REGION}.console.aws.amazon.com/codesuite/codebuild/projects/${CODE_BUILD_PROJECT_NAME}/build/${CODEBUILD_BUILD_ID}/log?region=${AWS_REGION}"
        message="🚨 This PR is broken 👇\n${prUrl} 🚨\nLogs are here 👇\n${buildUrl}"
        curl \
          -X POST \
          -H 'Content-type: application/json' \
          --data "{\"text\": \"${message}\"}" \
          "${SLACK_WEB_HOOK}"
      fi
```
## Environment variables passed to the CodeBuild project

There are many default environment variables you can access within a build run. You can find them listed in [this page](https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html). In addition to those, the Lambda function will pass:

- `REPOSITORY_NAME`: name of the `CodeCommit` repository
- `PULL_REQUEST_ID`: ID of the pull request
- `CODE_BUILD_PROJECT_NAME`: name of the CodeBuild project
