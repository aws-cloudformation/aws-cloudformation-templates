# Create Cross Account VPC Peers using AWS Lambda and CloudFormation.

## Issue

Customer need to automate the process to create VPC Peers between VPCs owned by different accounts.

## Short Description
VPC Peering facilitates network traffic between VPCs. By default, CloudFormation does not support creating VPC peering connections between VPCs owned by different accounts.  

## Resolution
Using AWS Lambda and CloudFormation Custom Resources we can go around this limitation, allowing the creation of the VPC Peers from within a CloudFormation Stack.

