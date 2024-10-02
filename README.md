# AWS CloudFormation Sample Templates

This repository contains sample CloudFormation templates that you can use
to help you get started on new infrastructure projects. Keep in mind that these 
templates are not meant to be production-ready "QuickStarts". You should 
take the time to learn how they work, adapt them to your needs, and make sure
that they meet your company's compliance standards.

Each template in this repository passes
[CloudFormation Linter](https://github.com/aws-cloudformation/cfn-lint)
(cfn-lint) checks, and also a basic set of
[CloudFormation Guard](https://github.com/aws-cloudformation/cloudformation-guard)
 rules based on the CIS Top 20, with exceptions for some rules where it
made sense to keep the sample focused on a single use case.

## Discord

Join us on Discord to discuss rain and all things CloudFormation! Connect and
interact with CloudFormation developers and experts, find channels to discuss
rain, the CloudFormation registry, StackSets, cfn-lint, Guard and more:

[![Join our Discord](https://discordapp.com/api/guilds/981586120448020580/widget.png?style=banner3)](https://discord.gg/9zpd7TTRwq)

## Submitting Templates

Before you submit a template, we suggest that you follow these guidelines:

- Fork the repository and create a fresh branch to work on your sample
  ```
  git remote add upstream git@github.com:aws-cloudformation/aws-cloudformation-templates.git
  git fetch upstream
  git checkout -b my-branch-name upstream/main
  git push -u origin
  ```
- Write the template in YAML, with a `.yaml` suffix (not `.yml` or
  `.template`). Our test scripts will auto-generate a JSON file based on the
  YAML. YAML is the source of truth for all templates in this repository.
- If your solution needs any other type of YAML file, like a K8s manifest 
  or a build spec, give it a `.yml` extension. This will cause it to be skipped
  by the test scripts.
- Test your template. Can you successfully create a stack with it?  When you
  delete a stack, is the stack (and all of its resources) successfully deleted?
  Make sure users aren't left with stray resources or stacks that have deletion
  errors.
- In the Description section, add a brief description of your template. The
  description should indicate what the template does and why it's useful. For
  example:
  ```
  Description: "Create a LAMP stack using a single EC2 instance and
  a local MySQL database for storage. This template demonstrates using the AWS
  CloudFormation bootstrap scripts to install the packages and files necessary
  to deploy the Apache web server, PHP, and MySQL when the instance is
  launched."
  ```
- Format your template to make it human readable:
  - Err on the side of human readability. If it makes your template easier to
    read, do it.
  - Use cfn-lint to lint your template and make sure it is valid.
  - Consider using two-space indents to reduce line wrapping.
- Review IAM resources. If you include IAM resources, follow the standard
  security advice of granting least privilege (granting only the permissions
  required to do a task).
- Remove secrets/credentials from your template. You might hardcode credentials
  or secrets in your template when you're testing. Don't forget to remove them
  before submitting your template. You can use this tool to help you scrub
  secrets:
  [https://github.com/awslabs/git-secrets](https://github.com/awslabs/git-secrets).
- Add your template to the correct folder so that others can discover it.
- Run the `scripts/test-all.sh` script in the directory where you're working to 
  make sure the template is valid.
- If you write any lambda function code, put it in a separate file and run
  `pylint` or `eslint` to make sure the code is valid.

When your template is ready, submit a pull request. A member of the AWS
organization will review your request and might suggest changes. 

## Additional Resources

### CloudFormation Linter (cfn-lint)

The [CloudFormation Linter](https://github.com/aws-cloudformation/cfn-lint) is
an indispensable tool for developing your templates. It should be a part of
every developer's workflow, and incorporated into your CI/CD pipelines.

Install cfn-lint with pip:

```sh
pip install cfn-lint
```

### CLoudFormation Rain

[Rain](https://github.com/aws-cloudformation/rain) is a command line interface
(CLI) for CloudFormation that greatly improves the experience for authoring and
deploying templates. It has many features, such as creating starter templates
for various use cases, interactive deployments, modules, and more.

Rain can be installed with Brew:

```sh
brew install rain
```

or if you are a Go user, you can install it like this:

```sh
go install github.com/aws-cloudformation/rain/cmd/rain@latest
```


In the *AWS CloudFormation User Guide*, you can view more information about the
following topics:

- Learn how to use templates to create AWS CloudFormation stacks using the
  [AWS Management Console](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-create-stack.html)
  or
  [AWS Command Line Interface (AWS CLI)](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html).
- To view all the supported AWS resources and their properties, see the
  [Template Reference](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html).
