## Summary

This is a Cloudformation Macro used to dynamically add a public and private subnet per Availability Zone when launching a template.  When the CreateStack template is launched and a change set is created, the Macro (named 'CreateSubnetsPerAZ') will dynamically add resources to the template for a public and private subnet per available AZ

## How to Use 

- Create a stack using the `CreateMacro` template, which will create the Lambda function and register it as a CFN Macro (with the name: 'CreateSubnetsPerAZ')
- Now the Macro is registered in your AWS account, and you can reference this macro in any CFN template using a top-level resource, similar to the following:

```yaml
Transform:
  - CreateSubnetsPerAZ
```

- Create a stack using the `CreateStack` template.  The template contains a VPC with a public and private subnet.  When this template is launched and the change set is created, the macro will add a private and public subnet to every AZ available in that region.  If this template is launched in us-west-2, there will be 2 public and 2 private subnets.  If launched in us-east-1, there will be 6 public and 6 private subnets

## References 

See the recently announced CloudFormation Macros feature: [CloudFormation Macros](https://aws.amazon.com/blogs/aws/cloudformation-macros)

## /HT 

[@mike-mosher](https://github.com/mike-mosher)


