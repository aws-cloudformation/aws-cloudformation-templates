"""getfromjson.py module."""

import json
import logging
import re
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

# When running in AWS Lambda, this function's "__name__" is "index",
# and it's "getfromjson" otherwise (such as, when you run code in this
# module in your machine for development/testing). For the former, see
# the "Handler: index.lambda_handler" line in the getfromjson.yml
# CloudFormation template that embeds code in this module.
IS_LOCAL_TESTING = __name__ == "getfromjson"
if not IS_LOCAL_TESTING:  # pragma: no cover
    import cfnresponse  # type: ignore

# Max allowed input length for JSON data and search queries.
JSON_DATA_MAX_BYTES = 4096
SEARCH_MAX_BYTES = 256

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
# LOGGER.setLevel(logging.DEBUG)


def lambda_handler(
    event: Dict[str, Any],
    context: Any,
) -> bool:
    """Lambda function entry-point."""
    try:
        json_data = event["ResourceProperties"]["json_data"]
        search = event["ResourceProperties"]["search"]

        _validate_input(
            json_data=json_data,
            search=search,
        )

        if not IS_LOCAL_TESTING:
            if event["RequestType"] == "Delete":
                _send_response(event, context, cfnresponse.SUCCESS, {})
                # Return True only if the request type is "Delete".
                return True

        response_data = {}
        response_data["Data"] = _traverse(
            data_from_json=json.loads(json_data),
            search=search,
        )
        LOGGER.debug(response_data)

        if not IS_LOCAL_TESTING:
            _send_response(event, context, cfnresponse.SUCCESS, response_data)

        return True
    except (IndexError, KeyError, ValueError) as invalid_input:
        message = f"Error: {str(invalid_input)}"
        LOGGER.error(message)
        if not IS_LOCAL_TESTING:
            _send_response(event, context, cfnresponse.FAILED, {}, message)

        return False


def _validate_input(
    json_data: str,
    search: str,
) -> None:
    """Validate provided input."""
    if len(json_data.encode()) > JSON_DATA_MAX_BYTES:
        raise ValueError(
            f"json_data limit ({JSON_DATA_MAX_BYTES} bytes) exceeded."
        )

    if len(search.encode()) > SEARCH_MAX_BYTES:
        raise ValueError(f"query limit ({SEARCH_MAX_BYTES} bytes) exceeded.")

    # Accepted input search values include:
    #
    #   - bracket-enclosed input values represented as alphanumeric
    #     string keys (that might also contain dashes and
    #     underscores), like ["mytest"], whereas the string key itself
    #     is enclosed in double quotes and the trailing quote is not
    #     escaped, or
    #
    #   - like the above, but with single quotes wrapping the value,
    #     like ['mytest'], or
    #
    #   - integer values wrapped in brackets, like [0].
    #
    # The following regular expression encompasses the three cases
    # above, whereas each case is delimited by a logical OR ("|")
    # character, and the check for the unescaped trailing quote is
    # implemented with a negative lookbehind regex: "(?<!\\\\)".
    search_pattern = "^((\\[\"[a-zA-Z0-9_-]+(?<!\\\\)\"\\])+)|((\\['[a-zA-Z0-9_-]+(?<!\\\\)'\\])+)|((\\[[0-9]+\\])+)$"  # noqa: E501 # pylint: disable=C0301

    LOGGER.debug("search: %s", search)
    LOGGER.debug("Validate search query against pattern: %s", search_pattern)
    if not re.match(
        pattern=search_pattern,
        string=search,
    ):
        raise ValueError("Invalid search query.")


def _traverse(
    data_from_json: Union[Dict[str, Any] | List[Any]],
    search: str,
) -> Any:
    """Traverses the data structure, and returns the value matching search."""
    LOGGER.debug("data_from_json: %s", data_from_json)

    search_tokens = _get_search_tokens(
        search=search,
    )

    # Used when removing quotes enclosing a token representing a map's
    # key string: match map keys (alphanumeric characters, dashes,
    # underscores) enclosed in quotes, whose trailing quote is not
    # escaped.
    search_token_map_key_pattern = "^((\"[a-zA-Z0-9_-]+(?<!\\\\)\")+)|(('[a-zA-Z0-9_-]+(?<!\\\\)')+)$"  # nosec B105 # noqa: E501 # pylint: disable=C0301
    LOGGER.debug("search_token_pattern: %s", search_token_map_key_pattern)

    value = data_from_json
    for search_token in search_tokens:
        if re.match(
            pattern=search_token_map_key_pattern,
            string=search_token,
        ):
            # Remove wrapping quotes.
            search_token = search_token[
                1 : len(search_token) - 1  # noqa: E203
            ]
        else:
            # Otherwise, use as an integer for a list's index.
            search_token = int(search_token)
        LOGGER.debug(
            "search_token: %s, type: %s", search_token, type(search_token)
        )
        value = value[search_token]
        LOGGER.debug("Value: %s", str(value))

    return str(value)


def _get_search_tokens(
    search: str,
) -> List[Any]:
    """Get tokens enclosed in brackets from search."""
    # Find all the tokens in square brackets from the search string;
    # for example, '["test"]["test1"][1]' has 3 tokens: ["test"],
    # ["test1"], and [1].
    search_tokens_pattern = "\\[(['\"a-zA-Z0-9_-]+)\\]"
    LOGGER.debug("search_tokens_pattern: %s", search_tokens_pattern)
    search_tokens = re.findall(
        pattern=search_tokens_pattern,
        string=search,
    )
    LOGGER.debug("search tokens found: %s", search_tokens)

    return search_tokens


def _send_response(
    event: Dict[str, Any],
    context: Any,
    response_status: str,
    response_data: Dict[str, Any],
    reason: Optional[str] = None,
) -> bool:
    """Define a wrapper for send() in the cfnresponse module."""
    cfnresponse.send(
        event, context, response_status, response_data, None, reason=reason
    )

    return True
