# VPCPeering

- [VPCPeering](#vpcpeering)
  - [Description](#description)
  - [Resources](#resources)
  - [Solution Highlights](#solution-highlights)
  - [Instructions (Individual Templates)](#instructions-individual-templates)
  - [Instructions (Nested Stacks)](#instructions-nested-stacks)
  - [Creating more VPC peering connections from different AWS accounts with same accepter account](#creating-more-vpc-peering-connections-from-different-aws-accounts-with-same-accepter-account)

## Description

This solution lets you peer with another VPC in the same or different AWS account. After creating VPC peering connection, additional templates can be
deployed to:

- Apply a `Name` tag for the VPC peering connection in the accepter account using a python CloudFormation custom resource.
- Update specified Route Tables & Security Groups
  - **Note:** The Security Group updates are configured to allow all inbound traffic from the VPC Peer CIDR provided as an **EXAMPLE**, however, this
    can be locked down based on the requirements.
  - **Note:** The Route Table updates are configured to route the whole VPC CIDR as an **EXAMPLE**, however, this can be locked down based on the
    requirements.

This solution can be implemented as individual templates accordingly, or leveraging the nested stacks `main` templates.

## Resources

- [What is VPC Peering?](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html)
- [VPC Peering Basics](https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html)
- [Walkthrough: Peer with an Amazon VPC in another AWS account](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/peer-with-vpc-in-another-account.html)

## Solution Highlights

This solution can be used for creating VPC peering connections as designed, but can also be used as a reference in creating other CloudFormation
templates.

- Supports a comma-delimited list of AWS accounts authorized for VPC peering connections, with validation.
- Supports creating VPC peering connection with same or different AWS account (with CloudFormation assertions)
- Applies a Name tag to the VPC peering connection in the accepter account using a python CloudFormation custom resource.
- Supports a comma-delimited list of route tables, and a list of security groups (with validation), to be updated to allow communications via VPC
  peering connection.

## Instructions (Individual Templates)

1. Deploy [VPCPeering-Accepter-Role.cfn.yaml](templates/VPCPeering-Accepter-Role.cfn.yaml) template to create the assumable role in the accepter
   account that will be used by the requester account. **Note:** If VPC peering connection being done between 2 VPCs in the same AWS account, then
   this step can be skipped.
2. Deploy [VPCPeering-Requester-Setup.cfn.yaml](templates/VPCPeering-Requester-Setup.cfn.yaml) template to create the VPC peering connection in the
   requester account.
3. Deploy [VPCPeering-Accepter-Tag.cfn.yaml](templates/VPCPeering-Accepter-Tag.cfn.yaml) template to apply a name tag on the VPC peering connection in
   the accepter account.
4. Deploy [VPCPeering-Updates.cfn.yaml](templates/VPCPeering-Updates.cfn.yaml) template to update the specified route tables & security groups for
   communications with the VPC peering connection in the requester account.
5. Deploy [VPCPeering-Updates.cfn.yaml](templates/VPCPeering-Updates.cfn.yaml) template to update the specified route tables & security groups for
   communications with the VPC peering connection in the accepter account.

## Instructions (Nested Stacks)

1. Deploy [VPCPeering-Accepter-Role.cfn.yaml](templates/VPCPeering-Accepter-Role.cfn.yaml) template to create the assumable role in the accepter
   account. **Note:** If VPC peering connection being done between 2 VPCs in the same AWS account, then this step can be skipped.
2. Deploy [VPCPeering-Requester.main.cfn.yaml](templates/VPCPeering-Requester.main.cfn.yaml) template to the requester account.
3. Deploy [VPCPeering-Accepter.main.cfn.yaml](templates/VPCPeering-Accepter.main.cfn.yaml) template to the accepter account.

## Creating more VPC peering connections from different AWS accounts with same accepter account

1. Update existing stack for [VPCPeering-Accepter-Role.cfn.yaml](templates/VPCPeering-Accepter-Role.cfn.yaml) with the AWS account of the additional
   requester accounts you will be creating VPC peering connections with.
2. Continue with Step 2 from the [individual templates](#instructions-individual-templates) or [nested stacks](#instructions-nested-stacks)
   instructions.
