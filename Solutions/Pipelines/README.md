# CloudFormation CI/CD Pipelines

This project contains templates that can be used to create CI/CD pipelines.
The pipelines can be centrally managed and accessed by app teams via a web
application, or they can be owned and managed by autonomous teams. The
templates are composed of local modules, which can be used as building blocks
to create new types of pipelines.

In the centrally managed use case, templates are stored in an S3 bucket
controlled by the platform team. When an app team chooses a template to spin up
a pipeline, the pipeline is configured to self-mutate whenever there is a
change to the source in S3. Each pipeline has two sources, one for the pipeline
and one for the application itself. Application teams control the build
specification files for the CodeBuild jobs in pipeline actions.

The web application included in this project is a simple proof-of-concept that
could be used as a starting point for building a fully featured CI/CD portal.
Once a template is chosen from the administrative UI, access is granted to the
AWS console to view and interact with the stack and pipeline.

CloudFormation templates are divided up into two categories. Bootstrap
templates are used to install the correct roles into target deployment
accounts. Pipeline templates are used to create the pipelines in the central
account.

