# VSCode Server

Create an EC2 instance with the code server from Coder.com and a CloudFront
distribution for encrypted access to the web ui from the browser. The output
from the template provides the CloudFront URL. There is no need to configure SSH
for this solution, it is purely browser based.

As a prerequisite, you need to create a plaintext secret in Secrets Manager to
store your password for the web site. This will be stored as a hash in the
configuration file for code server on the instance.

## Files

### `VSCodeServer.yaml`

This is the raw template, which includes [Rain](https://github.com/aws-cloudformation/rain) 
directives to import a VPC module and embed the user data script.

### `VSCodeServer-pkg.yaml`

The is the rendered template that you can deploy with `aws cloudformation
deploy` or `rain deploy`. To regenerate this template if you make any changes
to `VSCodeServer.yaml`, run `rain pkg -x VSCodeServer.yaml >
VSCodeServer-pkg.yaml`.

### `VSCodeServer.sh`

This is the user data script that is embedded in the packaged template. It is
meant to be used with Amazon Linux instances.



