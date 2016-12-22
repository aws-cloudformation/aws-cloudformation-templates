# Creating and Managing a Read Only IAM User 

## Introduction

In many cases, an AWS Administrator needs to temporarily provide read-only credentials to an individual. This CloudFormation template gives one a mechanism to create, control, and securely distribute credentials for this read-only IAM user. The process follows best practice ["least privileged access"](http://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege), by creating an inline IAM policy that explicitly defines which _Action(s)_ a user can execute. To simply administration, it moves the management of Access Keys and MultiFactor Authentication to the user. This limits secret key distribution through unsecured channels, and allows the user to enable [multi factor authentication](https://aws.amazon.com/iam/details/mfa/) for Console Login. 


## Policy

This **example** provides READ-ONLY access to the following infrastructure and data services: EC2, CloudFormation, AutoScaling, and S3. The policy was derived from the AWS Managed Policy *ReadOnlyAccess*. 
  
	"ReadPolicy" : {
      "Type": "AWS::IAM::Policy",
      "Properties": {
        "PolicyName": "read_only_policy",
        "PolicyDocument": {
          "Version" : "2012-10-17",
          "Statement": [
            {
              "Effect" : "Allow",
              "Action":[
                "autoscaling:Describe*",
                "cloudformation:Describe*",
                "cloudformation:GetTemplate",
                "cloudformation:List*",
                "ec2:Describe*",
                "ec2:GetConsoleOutput",
                "s3:List*",
                "s3:GetBucketLocation",
                "s3:GetBucketPolicy",
                "s3:GetLifecycleConfiguration",
                "tag:Get*"
              ],
              "Resource": "*"
            }
          ]
        },
        "Users" : [
          { "Ref" : "User" }
        ]
      }
    }


## Create Stack (Admin)

The new user will be forced to update their password on first login. Even so, it's never a good idea to type a plain text password into the terminal. Fortunately, the AWS CLI allows one to use a *parameters file*. Using the format below, create a file that contains a password which follows the accounts [IAM password policy](http://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html). This example uses gpg for encryption. 

    ## Create parameters file 
    $ cat read_only.parameters.json 
    [
      {
        "ParameterValue" : "<password that follows account policy>",
        "ParameterKey": "Password"
      }
    ]
    
    ## Create Stack 
    $ aws cloudformation create-stack --stack-name aws-proserve --template-body file://read_only.json --parameters file://read_only.parameters.json --capabilities CAPABILITY_IAM


    ## ## Wait until stack is complete 
    $ aws cloudformation describe-stacks --stack-name aws-proserve --query Stacks[].StackStatus
    "CREATE_COMPLETE"
   
    ## Copy outputs and parameters file 
    $ aws cloudformation describe-stacks --stack-name aws-proserve --query Stacks[].Outputs | tee access_info.txt
    [
      [
        {
            "OutputKey": "User", 
            "OutputValue": "aws-proserve-User-17MHGUGWDIKNK"
        }, 
        {
            "OutputKey": "ConsoleAccess", 
            "OutputValue": "https://098287060599.signin.aws.amazon.com/console"
        }
      ]
    ]
    $ cat read_only.parameters.json >> access_info.txt

    ## If required, encrypt and send access_info file. Otherwise  
    ## send the plain text file and verify that user immediately logs in.   
    $ gpg -e -r bear@example.com access_info.txt


## Create Access Keys / Enable MFA (User)

Open access_info.txt, and use the *Console URL*, *username*, and *password*, to login. Select Services -> IAM, then click on Users. Enter the *username* in the Filter search field, and double click on the user. Goto the Security Credentials tab, then create access keys and enable MFA. 


## Update Stack (Admin)

To make changes to users policy, update the template and stack. 

    ## Update policy to allow only S3 access only

    "ReadPolicy" : {
      "Type": "AWS::IAM::Policy",
      "Properties": {
        "PolicyName": "read_only_policy",
        "PolicyDocument": {
          "Version" : "2012-10-17",
          "Statement": [
            {
              "Effect" : "Allow",
              "Action":[
                "s3:List*",
                "s3:GetBucketLocation",
                "s3:GetBucketPolicy",
                "s3:GetLifecycleConfiguration"
              ],
              "Resource": "*"
            }
          ]
        },
        "Users" : [
          { "Ref" : "User" }
        ]
      }
    }

    ## Update Stack 
    $ aws cloudformation update-stack --stack-name aws-proserve --template-body file://read_only.json --parameters file://read_only.parameters.json --capabilities CAPABILITY_IAM


# Appendix 

## AWS CLI

AWS CLI can be downloaded here [http://aws.amazon.com/cli](http://aws.amazon.com/cli), or use a python package manager. After the install, configure the cli using the command below. (**NOTE:** One must set default region, i.e. us-west-2)

    $ pip install awscli
    $ aws configure

