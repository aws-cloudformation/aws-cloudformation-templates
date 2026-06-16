# Gitea Server

Create an EC2 instance with Gitea installed, and a CloudFront distribution for
encrypted access to the web ui from the browser. The output from the template
provides the CloudFront URL.

As a prerequisite, you need to create a plaintext secret in Secrets Manager to
store your password for a Gitea user called 'admin1' that will be created by the
user data script. The default name for the secret is 'gitea-password'. Do not create 
a "Key/value" secret, choose "Plaintext".

## Files

### `Gitea.yaml`

This is the raw template, which includes [Rain](https://github.com/aws-cloudformation/rain) 
directives to import a VPC module and embed the user data script.

### `Gitea-pkg.yaml`

The is the rendered template that you can deploy with `aws cloudformation
deploy` or `rain deploy`. To regenerate this template if you make any changes
to `Gitea.yaml`, run `rain pkg -x Gitea.yaml > Gitea-pkg.yaml`.

### `Gitea.sh`

This is the user data script that is embedded in the packaged template. It is
meant to be used with Amazon Linux instances.



