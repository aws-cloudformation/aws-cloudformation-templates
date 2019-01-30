'use strict';
const { CodeCommit, CodeBuild } = require('aws-sdk');

const { AWS_REGION, CODEBUILD_PROJECT_NAME } = process.env;

const pullRequestIdRegExp = /pull-request\/([0-9]+)/;
const codeCommit = new CodeCommit({ apiVersion: '2015-04-13', region: AWS_REGION });
const codeBuild = new CodeBuild({ apiVersion: '2016-10-06', region: AWS_REGION });

const getPullRequestId = ({ Sns }) => {
  const [, pullRequestId] = pullRequestIdRegExp.exec(Sns.Message);
  return pullRequestId;
};

const startBuild = async (commitId, repositoryName, pullRequestId) => (
  await codeBuild.startBuild({
    projectName: CODEBUILD_PROJECT_NAME,
    sourceVersion: commitId,
    environmentVariablesOverride: [
      {
        name: 'REPOSITORY_NAME',
        value: repositoryName,
        type: 'PLAINTEXT',
      },
      {
        name: 'PULL_REQUEST_ID',
        value: pullRequestId,
        type: 'PLAINTEXT',
      },
      {
        name: 'CODEBUILD_PROJECT_NAME',
        value: CODEBUILD_PROJECT_NAME,
        type: 'PLAINTEXT',
      },
    ],
  }).promise()
);

const isMergeable = async (pullRequest) => {
  const { pullRequestTargets: [{ repositoryName, sourceCommit, destinationCommit }] } = pullRequest;

  const { mergeable } = await codeCommit.getMergeConflicts({
    repositoryName,
    sourceCommitSpecifier: sourceCommit,
    destinationCommitSpecifier: destinationCommit,
    mergeOption: 'FAST_FORWARD_MERGE',
  }).promise();

  if (!mergeable) {
    console.log('Pull Request is not mergeable', JSON.stringify(pullRequest));
  }

  return mergeable;
};

exports.handler = async (event, context) => {
  console.log('event', JSON.stringify(event));
  console.log('context', JSON.stringify(context));

  const pullRequests = await Promise.all(
    event.Records
    .map(getPullRequestId)
    .map(pullRequestId => codeCommit.getPullRequest({ pullRequestId }).promise())
  );

  console.log('Pull Requests', JSON.stringify(pullRequests));
  
  const buildRuns = await Promise.all(
    pullRequests
      .map(({ pullRequest }) => pullRequest)
      .filter(({ pullRequestStatus }) => pullRequestStatus === 'OPEN')
      .map(async (pullRequest) => {
        if (!await isMergeable(pullRequest)) {
          return false;
        }
        const {
          pullRequestId,
          pullRequestTargets: [{ repositoryName, sourceCommit }],
        } = pullRequest;
        return startBuild(sourceCommit, repositoryName, pullRequestId);
      })
  );

  console.log('Build Runs', JSON.stringify(buildRuns.filter(Boolean)));
};
