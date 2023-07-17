**Overview**

These CloudFormation templates can automatically setup PrivateLink infrastructures securely connecting to SAP server.

**Pre-requisites**

- You already have a working SAP Gateway server that you can connect to

- You already have an AWS account with Admin permission

- You already setup a VPC (with private subnets within) in the AWS account and ensure
  - Either SAP server in EC2 of that VPC
  - Or SAP server can be reachable wihin that VPC (e.g. on-premise SAP connected through [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/SetUpVPNConnections.html))

- You already have a public resolvable DNS name that can be used to connect to their SAP server
  - Either DNS in Route53 of same account
  - Or DNS in Route53 of another account
  - Or DNS registered outside of AWS

**Use CloudFormation Templates**

1. Log into AWS account console with Admin permission

2. Check and choose the region of your SAP-reachable VPC
   - PrivateLink are regional service that clients can only call through PrivateLink in the same AWS region
   - If you want to setup PrivateLink in a different region, you need to first create a new VPC in the new region and setup [VPC Peering](https://docs.aws.amazon.com/vpc/latest/peering/working-with-vpc-peering.html) with SAP-reachable VPC (noted that the CIDR of new VPC must not overlap with current VPC's IP range)

3. Go to CloudFormation console and click `Create stack`

4. In the CreateStack console, tick `Template is ready` and `Upload a template file`

5. If the DNS in Route53 within same AWS account (full-automation)
   1. Upload `SapPrivateLink.yaml` and fill all the inputs
   2. Click Next all the way (accept all acknowledgements if asked) to create that stack
   3. Stack creating will take a while, monitor any updates shown in `Events` tab to know if and where got failures (Stack creation will auto-rollback if anything failure and will cleanup everything it created)
   4. After stack created, click `Outputs` tab, and click each of those to monitor and confirm below things:
      - Certificate's status shows `Issued`, this should always be issued otherwise Stack creation will be stuck there waiting
      - VPCEndpointService's DomainVerification shows `Verified` (it may take a few minutes, just keep refresh and monitoring)
      - TargetGroup's health check shows `Healthy` (it may take a few minutes, just keep refresh and monitoring), if not healthy need check if you give correct port or protocol to connect to your SAP or if the EC2 security group blocks the traffic
   5. If above checks all pass, the PrivateLink infrastructure created successfully, and can just use the VPCEndpointService's service name and DNS name to connect to SAP through PrivateLink
   6. If anything fails and want to retry, can just manually delete the stack to cleanup all created resources and start over

6. If the DNS outside of that AWS account (semi-automation with two manual domain verification steps)
   1. Upload `SapPrivateLinkNoHostedZone.yaml` and fill all the inputs
   2. Click Next all the way (accept all acknowledgements if asked) to create that stack
   3. Stack creating will take a while, monitor any updates shown in `Events` tab to know if and where got failures (Stack creation will auto-rollback if anything failure and will cleanup everything it created)
   4. Stack creating will stop at certificate creating step (noted that if you earlier verified the certificate with the same domain, it may auto-verify and automatically create certificate), go to that certificate in `Certificate Manager` console, in the `Domains` section take note of `CNAME name` and `CNAME value`
   5. Go to your DNS provider (in AWS it is Route53) trying to add a new record with below entries:
      - Type: `CNAME`
      - Record Name: the `CNAME name` of certificate (noted that CNAME should end with your domain name, if in Route53 the domain name suffix auto-populated, you just need to enter the first string segment before `.`)
      - Record Value: the `CNAME value` of certificate
   6. If above done correctly, the domain will get verified and certificate will show `Issued` (it can take a few minutes), and cloudformation creation will continue
   7. After stack created, click Outputs tab and click into the VPCEndpointService URL, and take note of `Domain verification name` and `Domain verification value`
   8. Go to your DNS provider (in AWS it is Route53) trying to add a new record with below entries:
      - Type: `TXT`
      - Record Name: the `Domain verification name` ending with `.<domain name>` (if in Route53 where domain name suffix auto-populated, just need to enter the `Domain verification name`)
      - Record Value: `Domain verification value` within double quotes (check your DNS provider if double quotes needed or not, like in Route53, double quotes not needed as will be auto-populated)
   9. If above done correctly, the domain will get verified shown in VPCEndpointService (it can take a few minutes)
   10. Then go back to stack Outputs tab and just check the TargetGroup's health check shows `Healthy` (it may take a few minutes, just keep refresh and monitoring), if not healthy need check if you give correct port or protocol to connect to your SAP or if the EC2 security group blocks the traffic
   11. If health check pass, the PrivateLink infrastructure created successfully, and can just use the VPCEndpointService's service name and DNS name to connect to SAP through PrivateLink
   12. If anything fails and want to retry, can just manually delete the stack to cleanup all created resources and start over

7. You can find all resources created in the CloudFormation stack's `Resources` tab (you can fine tune by directly editting resource, but it is not advised to delete those resources as they can make CloudFormation delete failing or stucking for quite long time, always delete CloudFormation stack to delete and cleanup resources)

8. If CloudFormation stuck in deleting, it is very possible there are existing connections to the created VPC Endpoint Service, need to manually reject those connections and CloudFormation's deletion will resume automatically
