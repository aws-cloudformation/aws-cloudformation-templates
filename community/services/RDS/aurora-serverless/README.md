# Aurora serverless cluster

## Features
- Aurora MySQL compliant serverless cluster
- Not publicly accessible but inside a VPC
- Bastion host for accessing the database from outside the VPC

## Before creating the stack

### Password
Create a parameter in *System Manager* > *Parameter Store* and use the parameter name as value for the `MasterUserPassword`.

### EC2 key
Create EC2 key to use for accessing the bastion host.
