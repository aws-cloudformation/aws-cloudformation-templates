# Create Cross Account VPC Peers using AWS Lambda and CloudFormation.

## Issue

Customer need to automate the process to create VPC Peers between VPCs owned by different accounts.

## Short Description
VPC Peering facilitates network traffic between VPCs. By default, CloudFormation does not support creating VPC peering connections between VPCs owned by different accounts.  

## Resolution
Using AWS Lambda and CloudFormation Custom Resources we can go around this limitation, allowing the creation of the VPC Peers from within a CloudFormation Stack.

# Instrucctions

The following steps provide a brief overview of this process:
 * Create a Cross Account Role on the peer account , using the template CrossAccountRoleTemplate.json, in this stack you need to specify the account id that will be requesting the VPC Peer connection
 * Create a Lambda backed custom resource on the account requesting the VPC peer, using the template VPCPeer.json, in this stack you need to specify your local VPC id, the remote VPC id, the account ID that owns the remote VPC and the Role Name created in the previous step


