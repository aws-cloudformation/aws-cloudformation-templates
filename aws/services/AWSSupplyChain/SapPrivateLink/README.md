**Overview**

These cloud formation templates can be shared to customer to setup PrivateLink infrastructures to connect to customer's SAP server

**Pre-requisites**
- Customer already set up an AWS account with VPC (including various private subnets across AZs within) that can connect to their SAP serve
  - Either SAP server in EC2 of that VPC
  - Or SAP server can be reachable from that VPC
- Customer already got a public resolvable DNS name that can be used to connect to their SAP server
  - Either DNS in Route53 of same account
  - Or DNS in Route53 of another account
  - Or DNS registered outside of AWS

**Use CloudFormation Templates**

1. Customer log into their AWS account console with Admin role

2. Check and choose the region of the SAP-residing/connecting VPC
   - If you want to create a privateLink in a different region, you need to first create a new VPC (CIDR range must be outside of SAP-residing/connecting VPC's one) in the new region and setup VPC-peering with SAP-residing/connecting VPC, follow https://docs.aws.amazon.com/vpc/latest/peering/working-with-vpc-peering.html

3. Go to CloudFormation console and click `Create stack`

4. In the CreateStack console, tick `Template is ready` and `Upload a template file`

5. If the DNS in Route53 within same AWS account (full-automation)
   1. Upload `SapPrivateLink.yaml` and fill all the inputs
   2. Click Next all the way (accept all acknowledgements if asked) to create that stack
   3. Stack creating will take a while, monitor any updates shown in `Events` tab to know if and where got failures (Stack creation will auto-rollback if anything failure and will cleanup everything it created)
   4. After stack created, click `Outputs` tab, and click each of those to monitor and confirm below things:
      - Certificate's status shows `Issued`, this should always be issued otherwise Stack creation will be stuck there waiting
      - VPCEndpointService's DomainVerification shows `Verified` (iit may take a few minutes, just keep refresh and monitoring)
      - TargetGroup's health check shows `Healthy` (it may take a few minutes, just keep refresh and monitoring), if not healthy it means the given IP is not able to connecting to SAP, need check why
   5. If above checks all pass, the PrivateLink infrastructure created successfully, and can just use the VPCEndpointService's service name and DNS name to connect to SAP through PrivateLink
   6. If anything fails and want to retry, can just manually delete the stack to cleanup all created resources and start over

6. If the DNS outside of that AWS account (semi-automation with two manual domain verification steps)
   1. Upload `SapPrivateLinkNoHostedZone.yaml` and fill all the inputs
   2. Click Next all the way (accept all acknowledgements if asked) to create that stack
   3. Stack creating will take a while, monitor any updates shown in `Events` tab to know if and where got failures (Stack creation will auto-rollback if anything failure and will cleanup everything it created)
   4. Stack creating will stop at certificate creating step, go to that certificate in `Certificate Manager` console, in the `Domains` section take note of `CNAME name` and `CNAME value`
   5. Go to your DNS manager trying to add a new record with below entries:
      - Type: `CNAME`
      - Record Name: the `CNAME name` of certificate (noted that CNAME should end with your DNS name, in Route53 where DNS name suffix auto-populated, you just need to enter the first string segment before `.`)
      - Record Value: the `CNAME value` of certificate
   6. If above done correctly, the domain will get verified and certificate will show `Issued` (it can take up to a few minutes), and cloudformation creation will continue
   7. After stack created, click Outputs tab and click into the VPCEndpointService URL, and take note of `Domain verification name` and `Domain verification value`
   8. Go to your DNS manager trying to add a new record with below entries:
      - Type: `TXT`
      - Record Name: the `Domain verification name` ending with `.<DNS>` (in Route53 where DNS name suffix auto-populated, just need to enter the `Domain verification name`)
      - Record Value: `Domain verification value` within double quotes (in Route53, double quotes not needed)
   9. If above done correctly, the domain will get verified shown in VPCEndpointService (it can take up to a few minutes)
   10. Then go back to stack Outputs tab and just check the TargetGroup's health check shows `Healthy` (it may take a few minutes, just keep refresh and monitoring), if not healthy it means the given IP is not able to connecting to SAP, need check why
   11. If health check pass, the PrivateLink infrastructure created successfully, and can just use the VPCEndpointService's service name and DNS name to connect to SAP through PrivateLink
   12. If anything fails and want to retry, can just manually delete the stack to cleanup all created resources and start over
