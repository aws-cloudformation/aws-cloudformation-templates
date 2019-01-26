# Aurora serverless cluster

## Features
- Aurora MySQL compliant serverless cluster.
- Inside a VPC so not publicly accessible.
- Bastion host for accessing the database from outside the VPC.

## Before creating the stack
- Create EC2 key to use for accessing the bastion host.

## After creating the stack
- Add the database password to AWS Secret Manager so you will be able to retrieve it from your authorized applications. Secret Manager can also automatically rotate the password periodically.
- Update the bastion security group in EC2 adding to allow incoming connections from your work places.
