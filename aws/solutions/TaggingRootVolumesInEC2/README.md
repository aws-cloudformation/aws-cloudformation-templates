# Tag the EBS Root Volume through a CloudFormation Template. For Both Windows and Linux Systems

CloudFormation template that will create a Linux and Windows Instance which will then tag the root volume of these instances.

Template will invoke the following:
  - Create a Windows and Linux EC2 Instance.
  - The Template will use the UserData property of the EC2 Instance resource to tag the root volume.
  - This is done through the AWS CLI commands which at base will tag the root volume with "--tags Key=MyRootTag,Value=MyRootVolumesValue" for the Windows and Linux AMIs.
  - If the Windows AMI you are trying to utilize does not have the AWS CLI installed you can still utilize the base Windows commands within the template (This is the uncommented section of the Windows Instance).
  - Create an IAM role to attach to the Instances which will give them permissions to tag the root volumes created.

To Create the instances you can either utilize the AWS CLI command (Where the parameters will be needed to alter for your specific use case):

```aws cloudformation create-stack --stack-name TaggingVolumes --template-body file://Tagging_Root_volume.json --parameters ParameterKey=KeyName,ParameterValue=TestKey ParameterKey=InstanceType,ParameterValue=t2.micro ParameterKey=InstanceAZ,ParameterValue=eu-west-1 ParameterKey=WindowsAMIID,ParameterValue=ami-0d138b26f46625e2f ParameterKey=LinuxAMIID,ParameterValue=ami-0fad7378adf284ce0```

If you do not wish to utilize the CLI you can also create the template through the Console by:
 1) Navigate to the CloudFormation console - https://console.aws.amazon.com/cloudformation/home
 2) Choose Create Stack, and then choose Design template.
 3) At the bottom of the page, choose the Template tab.
 4) Copy the sample template the portion which will alter depending on the operating system and different tagging options you use is the UserData property.
 5) Choose the Create stack icon, choose Next, and type a name for your CloudFormation Stack.
 6) For Parameters, enter the values such as the SSH keyname pair you wish to use, the InstanceType you want the instance to be and most importantly the AMI to be used (Please note that the default being used is for the eu-west-1 region).
 7) Choose Next, and then choose Next again.
 8) Just before the Create Stack option you will need to tick a box to confirm that the CloudFormation stack could create an IAM resource, for example the IAM role assigned to the instances.
