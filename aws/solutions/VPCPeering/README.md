# Create Cross Account VPC Peers using AWS Lambda and CloudFormation.

## Issue
VPC peering facilitates network traffic between VPCs. By default, CloudFormation does not support creating VPC peering connections between VPCs in different AWS accounts. How do I work around this limitation? 

## Short Description
When you request a VPC peering connection from one AWS account (referred to here as the requester_account) to a VPC in another AWS account (a peer_account), the VPC peering connection request must first be approved and accepted by the peer_account to be activated. By default, the requester_account cannot both request and also approve VPC peering connection requests made to a different AWS peer_account. 

## Resolution
Using AWS Lambda and CloudFormation Custom Resources we can go around this limitation, allowing the creation of the VPC Peers from within a CloudFormation Stack.

## Instructions

The following steps provide a brief overview of this process:
 * Create a Cross Account Role on the peer account, using the template CrossAccountRoleTemplate.json, in this stack you need to specify the account id that will be requesting the VPC Peer connection
 * Create a Lambda backed custom resource on the account requesting the VPC peer, using the template VPCPeer.json, in this stack you need to specify your local VPC id, the remote VPC id, the account ID that owns the remote VPC and the Role Name created in the previous step

