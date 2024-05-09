"Lambda handler for the ExecutionRoleBuilder macro"

#pylint: disable=broad-exception-raised
#pylint: disable=unused-wildcard-import

import json
import uuid

#pylint: disable=wildcard-import
from policytemplates import *

# Variable for the default role path, if a role path is not provided
defaultrolepath = "/boundedexecutionroles/"


# Core function handler
def handler(event, _):
    "Lambda handler"

    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": convert_template(event["fragment"]),
    }


# Function to convert/expand the template
def convert_template(fragment):
    "Convert the template fragment"

    print(f"This was the fragment: {fragment}")

    # Loop through each resource in the template
    resources = fragment["Resources"]
    for resource in resources:
        print(f"Determining if {resource} is an IAM role")
        resourcejson = resources[resource]
        # If the resource is an IAM Role, expand the shorthand notation to the proper
        # CloudFormation using the function below, otherwise leave the resource as is
        if resourcejson["Type"] == "AWS::IAM::Role":
            print(f"Found a role: {resource}")
            # Expanding role
            resources[resource] = expand_role(resourcejson)

    # Debug output
    print(f"This is the transformed fragment: {fragment}")
    # Return the converted/expanded template fragment
    return fragment


def expand_role(rolefragment):
    "Function to expand shorthand role definitions into proper CloudFormation"

    # Debug output
    print(f"This is the role fragment: {rolefragment}")

    # Extract shorthand properties for role type, name, and desired permissions
    roletype = rolefragment["Properties"]["Type"]
    rolename = rolefragment["Properties"]["Name"]
    permissions = rolefragment["Properties"]["Permissions"]

    # Get the basic role template (from policytemplates.py) and do a simple
    # string replace to set the name and the AWS service principal for the
    # trust policy (e.g. lambda)
    returnval = roletemplate.replace("<ROLETYPE>", roletype.lower())
    returnval = returnval.replace("<ROLENAME>", rolename)
    # Load this as json to form the initial basis of the function return value
    returnvaljson = json.loads(returnval)

    # If the shorthand notation included a list of managed policy ARNs pass
    # those though as-is
    if "ManagedPolicyArns" in rolefragment["Properties"]:
        returnvaljson["Properties"]["ManagedPolicyArns"] = rolefragment["Properties"][
            "ManagedPolicyArns"
        ]

    # If the shorthand notation included a permission boundary pass that through as-is
    if "PermissionsBoundary" in rolefragment["Properties"]:
        returnvaljson["Properties"]["PermissionsBoundary"] = rolefragment["Properties"][
            "PermissionsBoundary"
        ]

    # If the shorthand notation included a role path pass that through as-is If
    # it did not, provide an opinionated configuration using the variable above
    if "Path" in rolefragment["Properties"]:
        returnvaljson["Properties"]["Path"] = rolefragment["Properties"]["Path"]
    else:
        returnvaljson["Properties"]["Path"] = defaultrolepath

    # Loop through each of the short hand permissions
    for permission in permissions:
        # Debug output
        print(f"permission: {permission}")
        # Split each shorthand permission into an action group (e.g. ReadOnly)
        # and the associated Resource
        for actiongroup, resource in permission.items():
            print(f"actiongroup: {actiongroup}, resource: {resource}")
            # Use the function below to extract the service (e.g. S3) from the resource ARN
            service = servicefromresource(resource)
            print(f"service: {service}")
            # Lookup the given policy snippet from policytemplates.py based on
            # the service & action group If the necessary snippet isn't
            # included in policytemplates.py err out
            if service in policytemplates and actiongroup in policytemplates[service]:
                policytemplate = policytemplates[service][actiongroup]
            else:
                raise Exception(f"No policy template found for service: {service} " + 
                                f"and actiongroup: {actiongroup}")
            # Substitute the placeholder in the template for the actual resource
            policytemplate = policytemplate.replace("<RESOURCE>", resource)
            # Policy names must be unique, appending a UUID is a simple way to
            # guarantee that
            uuidval = str(uuid.uuid4())
            policytemplate = policytemplate.replace("<UUID>", uuidval)
            # Convert the policy snippet to json and add it as an inline policy
            # to the overall return values
            policytemplatejson = json.loads(policytemplate)
            print(f"adding policy: {policytemplate}")
            returnvaljson["Properties"]["Policies"].append(policytemplatejson)

    # In addition to the permissions in the shorthand notation add the
    # 'allroles' policy template This template is used to provide permissions
    # like CloudWatchLogs instead of forcing each developer to repeatedly
    # specify common permissions
    uuidval = str(uuid.uuid4())
    allrolespolicytemplate = policytemplates["allroles"]["default"]
    allrolespolicytemplate = allrolespolicytemplate.replace("<UUID>", uuidval)
    allrolespolicytemplatejson = json.loads(allrolespolicytemplate)
    print(f"adding policy: {allrolespolicytemplate}")
    returnvaljson["Properties"]["Policies"].append(allrolespolicytemplatejson)

    # Return the expanded proper CloudFormation
    return returnvaljson


def servicefromresource(resource):
    "Simple function to return the AWS service (e.g. S3) from a given resource ARN"
    return resource.split(":")[2]
