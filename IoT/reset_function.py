"Group Deployment Reset Function"

# pylint: disable=line-too-long,logging-fstring-interpolation

import os
import sys
import json
import logging
import cfnresponse
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
region = os.environ["AWS_REGION"]
partition = session.get_partition_for_region(region)
c = session.client("greengrass")
iam = session.client("iam")
role_name = f"greengrass_cfn_{os.environ['STACK_NAME']}_ServiceRole"


def find_group(thingName):
    "Find the group based on the name"

    response_auth = ""

    response = c.list_groups()
    for group in response["Groups"]:
        thingfound = False
        group_version = c.get_group_version(
            GroupId=group["Id"], GroupVersionId=group["LatestVersion"]
        )

        core_arn = group_version["Definition"].get("CoreDefinitionVersionArn", "")
        if core_arn:
            core_id = core_arn[
                core_arn.index("/cores/") + 7 : core_arn.index("/versions/")
            ]
            core_version_id = core_arn[
                core_arn.index("/versions/") + 10 : len(core_arn)
            ]
            thingfound = False
            response_core_version = c.get_core_definition_version(
                CoreDefinitionId=core_id, CoreDefinitionVersionId=core_version_id
            )
            if "Cores" in response_core_version["Definition"]:
                for thing_arn in response_core_version["Definition"]["Cores"]:
                    if thingName == thing_arn["ThingArn"].split("/")[1]:
                        thingfound = True
                        break
        if thingfound:
            logger.info(f"found thing: {thingName}, group id is: {group['Id']}")
            response_auth = group["Id"]
            return response_auth

    return ""


def manage_greengrass_role(cmd):
    "Greengrass role"

    if cmd == "CREATE":
        r = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument='{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "greengrass.amazonaws.com"},"Action": "sts:AssumeRole"}]}',
            Description="Role for CloudFormation blog post",
        )
        role_arn = r["Role"]["Arn"]
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=f"arn:{partition}:iam::policy/service-role/AWSGreengrassResourceAccessRolePolicy",
        )
        c.associate_service_role_to_account(RoleArn=role_arn)
        logger.info(f"Created and associated role {role_name}")
    else:
        try:
            r = iam.get_role(RoleName=role_name)
            role_arn = r["Role"]["Arn"]
            c.disassociate_service_role_from_account()
            iam.delete_role(RoleName=role_name)
            logger.info(f"Disassociated and deleted role {role_name}")
        except ClientError:
            return


def handler(event, context):
    "Lambda handler"

    responseData = {}
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        result = cfnresponse.FAILED
        thingName = event["ResourceProperties"]["ThingName"]
        if event["RequestType"] == "Create":
            try:
                c.get_service_role_for_account()
                result = cfnresponse.SUCCESS
            except ClientError:
                manage_greengrass_role("CREATE")
                logger.info("Greengrass service role created")
                result = cfnresponse.SUCCESS
        elif event["RequestType"] == "Delete":
            group_id = find_group(thingName)
            logger.info(f"Group id to delete: {group_id}")
            if group_id:
                c.reset_deployments(Force=True, GroupId=group_id)
                result = cfnresponse.SUCCESS
                logger.info("Forced reset of Greengrass deployment")
                manage_greengrass_role("DELETE")
            else:
                logger.error(f"No group Id for thing: {thingName} found")
    except ClientError as e:
        logger.error(f"Error: {e}")
        result = cfnresponse.FAILED
    logger.info(f"Returning response of: {result}, with result of: {responseData}")
    sys.stdout.flush()
    cfnresponse.send(event, context, result, responseData)
