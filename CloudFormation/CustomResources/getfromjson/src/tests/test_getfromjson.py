"""Tests for the getfromjson.py module."""

from typing import (
    Any,
    Dict,
)
from unittest.mock import patch

import cfnresponse  # type: ignore
from pytest import raises

from .. import getfromjson


def test_given_json_list_when_traversed_with_invalid_search_then_it_should_raise_exception() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    data_from_json = ["test0", "test1", "test2"]
    search = "[3]"

    with raises(IndexError):
        getfromjson._traverse(  # pylint: disable=W0212
            data_from_json=data_from_json,
            search=search,
        )


def test_given_json_list_when_traversed_with_valid_search_then_it_should_return_valid_value() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    data_from_json = ["test0", "test1", "test2"]
    search = "[2]"

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "test2"


def test_given_json_map_when_traversed_with_invalid_search_then_it_should_raise_exception() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    data_from_json = {"test": {"test-1": ["x", "y"]}}
    search = '["test"]["test-2"][1]'

    with raises(KeyError):
        getfromjson._traverse(  # pylint: disable=W0212
            data_from_json=data_from_json,
            search=search,
        )


def test_given_json_map_when_traversed_with_valid_search_then_it_should_return_valid_value() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    data_from_json = {"test": {"test-1": ["x", "y"]}}
    search = '["test"]["test-1"][1]'

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "y"


def test_given_json_map_with_allowed_index_keys_when_traversed_with_valid_search_then_it_should_return_valid_value() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    data_from_json = {"testTest012-_": {"test-1": ["x", "y"]}}
    search = '["testTest012-_"]["test-1"][1]'

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "y"


def test_given_json_list_with_unicode_values_when_traversed_with_valid_search_then_it_should_return_expected_values() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    data_from_json = ["√√ test0", "√√ test1", "√√ test2"]
    search = "[2]"

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "√√ test2"


def test_given_json_map_with_unicode_values_when_traversed_with_valid_search_then_it_should_return_expected_values() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    data_from_json = {"testTest012-_": {"test-1": ["x", "√√ test"]}}
    search = '["testTest012-_"]["test-1"][1]'

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "√√ test"


def test_given_search_with_single_quotes_when_traversing_map_then_it_should_return_expected_values() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    data_from_json = {"testTest012-_": {"test-1": ["x", "y"]}}
    search = "['testTest012-_']['test-1'][1]"

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "y"


def test_given_search_with_alternate_single_and_double_quotes_across_tokens_when_traversing_map_then_it_should_return_expected_values() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    data_from_json = {"testTest012-_": {"test-1": ["x", "y"]}}
    search = "['testTest012-_'][\"test-1\"][1]"

    value = getfromjson._traverse(  # pylint: disable=W0212
        data_from_json=data_from_json,
        search=search,
    )

    assert value == "y"


def test_given_json_data_max_bytes_exceeded_when_consumed_then_request_should_return_false() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    json_data_max_bytes_current = getfromjson.JSON_DATA_MAX_BYTES
    getfromjson.JSON_DATA_MAX_BYTES = 1

    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = True

    json_data = '["test0", "test1", "test2"]'
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search

    assert getfromjson.lambda_handler(event, None) is False

    getfromjson.JSON_DATA_MAX_BYTES = json_data_max_bytes_current

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_search_max_bytes_exceeded_when_consumed_then_request_should_return_false() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    search_max_bytes_current = getfromjson.SEARCH_MAX_BYTES
    getfromjson.SEARCH_MAX_BYTES = 1

    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = True

    json_data = '["test0", "test1", "test2"]'
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search

    assert getfromjson.lambda_handler(event, None) is False

    getfromjson.SEARCH_MAX_BYTES = search_max_bytes_current

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_invalid_json_data_when_consumed_then_request_should_return_false() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = True

    json_data = "invalid"
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search

    assert getfromjson.lambda_handler(event, None) is False

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_invalid_search_when_consumed_then_request_should_return_false() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = True

    json_data = '["test0", "test1", "test2"]'
    search = "invalid"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search

    assert getfromjson.lambda_handler(event, None) is False

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_valid_json_data_and_search_when_consumed_then_request_should_return_true() -> (  # noqa: D103 E501 # pylint: disable=C0116
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = True

    json_data = '["test0", "test1", "test2"]'
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search

    assert getfromjson.lambda_handler(event, None) is True

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_delete_request_type_when_consumed_then_cfnresponse_should_be_called_with_success_response() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = False

    json_data = '["test0", "test1", "test2"]'
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search
    event["RequestType"] = "Delete"

    with patch(
        "src.getfromjson._send_response",
        return_value=None,
    ):
        assert getfromjson.lambda_handler(event, None) is True

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_non_delete_request_type_when_valid_input_is_consumed_then_cfnresponse_should_be_called_with_success_response() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = False

    json_data = '["test0", "test1", "test2"]'
    search = "[2]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search
    event["RequestType"] = "Create"

    with patch(
        "src.getfromjson._send_response",
        return_value=None,
    ):
        assert getfromjson.lambda_handler(event, None) is True

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_non_delete_request_type_when_invalid_input_is_consumed_then_cfnresponse_should_be_called_with_failed_response() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    is_local_testing_current = getfromjson.IS_LOCAL_TESTING
    getfromjson.IS_LOCAL_TESTING = False

    json_data = '["test0", "test1", "test2"]'
    search = "[3]"

    event: Dict[str, Any] = {}
    event["ResourceProperties"] = {}
    event["ResourceProperties"]["json_data"] = json_data
    event["ResourceProperties"]["search"] = search
    event["RequestType"] = "Create"

    with patch(
        "src.getfromjson._send_response",
        return_value=None,
    ):
        assert getfromjson.lambda_handler(event, None) is False

    getfromjson.IS_LOCAL_TESTING = is_local_testing_current


def test_given_response_to_send_when_sent_with_cfnresponse_then_it_should_return_true() -> (  # noqa: D103 E501 # pylint: disable=C0116,C0301
    None
):
    class Context:  # pylint: disable=R0903
        """Mock Context class."""

        def __init__(self) -> None:
            self.log_stream_name = "test"

    event = {}
    event["ResponseURL"] = "https://mock_value"
    event["StackId"] = "mock_value"
    event["RequestId"] = "mock_value"
    event["LogicalResourceId"] = "mock_value"

    with patch(
        "cfnresponse.send",
        return_value=None,
    ):
        value = getfromjson._send_response(  # pylint: disable=W0212
            event,
            Context(),
            cfnresponse.SUCCESS,  # noqa: E501 # pylint: disable=E0606
            {},
        )

        assert value is True
