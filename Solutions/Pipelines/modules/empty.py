"Empty the contents of a bucket"

# pylint: disable=too-many-locals,broad-exception-caught
# pylint: disable=broad-exception-raised,too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-arguments,too-many-positional-arguments

import logging
import json
import re
import boto3
import botocore
import urllib3

BUCKET_ARN = "BucketArn"
VERSIONS = "Versions"
DELETE_MARKERS = "DeleteMarkers"
VERSION_ID = "VersionId"
VERSION_ID_MARKER = "VersionIdMarker"
KEY_MARKER = "KeyMarker"
KEY = "Key"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def empty(event, context):
    "Empty bucket contents on Delete"
    try:
        logger.info("boto3 version: %s", boto3.__version__)
        logger.info("botocore version: %s", botocore.__version__)
        logger.info(event)

        if event["RequestType"] != "Delete":
            logger.info("Not a delete")
            send(event, context, SUCCESS, {})
            return

        props = event["ResourceProperties"]["Properties"]
        if BUCKET_ARN not in props:
            raise Exception(f"Missing {BUCKET_ARN}")
        bucket_name = props[BUCKET_ARN].replace("arn:aws:s3:::", "")

        is_test = props.get("Test", False)

        s3 = boto3.client("s3")

        objects_to_delete = []

        has_more_results = True
        next_key_marker = None
        next_version_id_marker = None

        while has_more_results:
            args = {"Bucket": bucket_name}
            if next_key_marker:
                args[KEY_MARKER] = next_key_marker
                args[VERSION_ID_MARKER] = next_version_id_marker
            logger.info("About to list object versions: %s", args)
            contents = s3.list_object_versions(**args)

            if VERSIONS not in contents and DELETE_MARKERS not in contents:
                msg = f"{VERSIONS} or {DELETE_MARKERS} not found in contents"
                logger.info(msg)
                break

            if VERSIONS in contents:
                for v in contents[VERSIONS]:
                    d = {KEY: v[KEY]}
                    if VERSION_ID in v and v[VERSION_ID] != "null":
                        d[VERSION_ID] = v[VERSION_ID]
                    objects_to_delete.append(d)

            if DELETE_MARKERS in contents:
                for v in contents[DELETE_MARKERS]:
                    d = {KEY: v[KEY]}
                    if VERSION_ID in v and v[VERSION_ID] != "null":
                        d[VERSION_ID] = v[VERSION_ID]
                    objects_to_delete.append(d)

            if len(objects_to_delete) == 0:
                logger.info("objects_to_delete is empty")
                break

            if contents["IsTruncated"] is True:
                has_more_results = True
                next_key_marker = contents["NextKeyMarker"]
                next_version_id_marker = contents["NextVersionIdMarker"]
                if next_key_marker is None or next_version_id_marker is None:
                    logger.info("NextKeyMarker and NextVersionIdMarker not set")
                    break
            else:
                has_more_results = False

        # Delete the contents
        logger.info("Bucket has %s objects to delete", len(objects_to_delete))

        # Break into chunks of 1000 or less
        def chunks(lst, n):
            "Break an array into chunks of n size"
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        for chunk in chunks(objects_to_delete, 1000):
            logger.info("About to delete chunk: %s", json.dumps(chunk, default=str))
            r = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": chunk})
            logger.info("delete_objects response: %s", json.dumps(r, default=str))

        logger.info("Done")
        if is_test:
            return
        send(event, context, SUCCESS, {})
    except Exception as e:
        logger.exception(e)
        if is_test:
            raise e
        send(event, context, FAILED, {})


SUCCESS = "SUCCESS"
FAILED = "FAILED"

http = urllib3.PoolManager()


def send(
    event,
    context,
    response_status,
    response_data,
    physical_resource_id=None,
    no_echo=False,
    reason=None,
):
    "Send a response to CloudFormation"

    response_url = event["ResponseURL"]

    response_body = {
        "Status": response_status,
        "Reason": reason
        or f"See the details in CloudWatch Log Stream: {context.log_stream_name}",
        "PhysicalResourceId": physical_resource_id or context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "NoEcho": no_echo,
        "Data": response_data,
    }

    json_response_body = json.dumps(response_body)

    logger.info("Response body:")
    logger.info(json_response_body)

    headers = {"content-type": "", "content-length": str(len(json_response_body))}

    try:
        response = http.request(
            "PUT", response_url, headers=headers, body=json_response_body
        )
        logger.info("Status code: %s", response.status)

    except Exception as e:

        logger.exception(
            "send(..) failed executing http.request(..): %s",
            mask_credentials_and_signature(e),
        )


def mask_credentials_and_signature(message):
    "Mask credentials"
    message = re.sub(
        r"X-Amz-Credential=[^&\s]+",
        "X-Amz-Credential=*****",
        message,
        flags=re.IGNORECASE,
    )
    return re.sub(
        r"X-Amz-Signature=[^&\s]+",
        "X-Amz-Signature=*****",
        message,
        flags=re.IGNORECASE,
    )
