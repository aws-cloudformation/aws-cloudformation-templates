'use strict';
const { CodeCommit, CodeBuild } = require('aws-sdk');

const { AWS_REGION, CODE_BUILD_PROJECT_NAME } = process.env;

const pullRequestIdRegExp = /pull-request\/([0-9]+)/;
const codeCommit = new CodeCommit({ apiVersion: '2015-04-13', region: AWS_REGION });
const codeBuild = new CodeBuild({ apiVersion: '2016-10-06', region: AWS_REGION });

const getPullRequestId = ({ Sns }) => {
  const [, pullRequestId] = pullRequestIdRegExp.exec(Sns.Message);
  return pullRequestId;
};

const startBuild = async (commitId) => {
  await codeBuild.startBuild({
    projectName: CODE_BUILD_PROJECT_NAME,
    sourceVersion: commitId,
  }).promise();
};

const isMergeable = ({ pullRequestTargets: [{ destinationCommit, mergeBase }] }) => (
  destinationCommit === mergeBase
);

exports.handler = async (event, context) => {
  console.log('event', JSON.stringify(event));
  console.log('context', JSON.stringify(context));

  const pullRequests = await Promise.all(
    event.Records
    .map(getPullRequestId)
    .map(pullRequestId => codeCommit.getPullRequest({ pullRequestId }).promise())
  );
  
  await Promise.all(
    pullRequests
      .map(({ pullRequest }) => pullRequest)
      .filter(({ pullRequestStatus }) => pullRequestStatus === 'OPEN')
      .filter(isMergeable)
      .map(({ pullRequestTargets }) => pullRequestTargets[0].sourceCommit)
      .map(startBuild)
  );
};
