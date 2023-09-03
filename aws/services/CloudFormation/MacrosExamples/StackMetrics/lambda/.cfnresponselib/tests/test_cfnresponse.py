import unittest
from unittest.mock import Mock, patch
import cfnresponse
from cfnresponse import (
    register_handler,
    send,
    CustomLambdaException,
    InvalidRequestTypeException,
    HookException,
    lambda_handler,
)
import json

class TestCFNResponse(unittest.TestCase):
    def setUp(self):
        cfnresponse._registered_handlers["create"] = None
        cfnresponse._registered_handlers["update"] = None
        cfnresponse._registered_handlers["delete"] = None

    def tearDown(self):
        cfnresponse._registered_handlers["create"] = None
        cfnresponse._registered_handlers["update"] = None
        cfnresponse._registered_handlers["delete"] = None

    def test_handler_registration(self):
        self.assertIsNone(cfnresponse._registered_handlers["create"])
        self.assertIsNone(cfnresponse._registered_handlers["update"])
        self.assertIsNone(cfnresponse._registered_handlers["delete"])
        
        @register_handler("create", "update")
        def custom_action(event, context):
            return "Custom create_or_update executed"
        
        @register_handler("delete")
        def delete_action(event, context):
            return "Custom delete executed"

        self.assertEqual(cfnresponse._registered_handlers["create"], custom_action)
        self.assertEqual(cfnresponse._registered_handlers["update"], custom_action)
        self.assertEqual(cfnresponse._registered_handlers["delete"], delete_action)

    @patch("cfnresponse.send")
    def test_create_lambda_handler(self, mock_send):
        sample_event = {
            "RequestType": "Create",
            "ResponseURL": "http://example.com",
            "StackId": "stack-id",
            "RequestId": "request-id",
            "LogicalResourceId": "logical-id",
        }
        @register_handler("create")
        def custom_action(event, context):
            return {"message": "Custom create executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_once_with(
            sample_event, sample_context, "SUCCESS", {"message": "Custom create executed."}
        )

    @patch("cfnresponse.send")
    def test_update_lambda_handler(self, mock_send):
        sample_event = {
            "RequestType": "Update",
            "ResponseURL": "http://example.com",
            "StackId": "stack-id",
            "RequestId": "request-id",
            "LogicalResourceId": "logical-id",
        }
        @register_handler("update")
        def custom_action(event, context):
            return {"message": "Custom update executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_once_with(
            sample_event, sample_context, "SUCCESS", {"message": "Custom update executed."}
        )

    @patch("cfnresponse.send")
    def test_create_or_update_lambda_handler(self, mock_send):
        sample_event = {
            "RequestType": "Update",
            "ResponseURL": "http://example.com",
            "StackId": "stack-id",
            "RequestId": "request-id",
            "LogicalResourceId": "logical-id",
        }
        @register_handler("update", "create")
        def custom_action(event, context):
            return {"message": "Custom create_or_update executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_with(
            sample_event, sample_context, "SUCCESS", {"message": "Custom create_or_update executed."}
        )
        
        sample_event["RequestType"] = "Create"
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_with(
            sample_event, sample_context, "SUCCESS", {"message": "Custom create_or_update executed."}
        )
        
        self.assertEqual(mock_send.call_count, 2)
        
    @patch("cfnresponse.send")
    def test_delete_lambda_handler(self, mock_send):
        sample_event = {
            "RequestType": "Delete",
            "ResponseURL": "http://example.com",
            "StackId": "stack-id",
            "RequestId": "request-id",
            "LogicalResourceId": "logical-id",
        }
        @register_handler("delete")
        def custom_action(event, context):
            return {"message": "Custom delete executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_once_with(
            sample_event, sample_context, "SUCCESS", {"message": "Custom delete executed."}
        )
        
    @patch("cfnresponse.send")
    def test_invalid_request_type_exception(self, mock_send):
        sample_event = {}
        @register_handler("create")
        def custom_action(event, context):
            return {"message": "Custom delete executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_once_with(
            sample_event, sample_context, 'FAILED', {'message': InvalidRequestTypeException.message, 'event': json.dumps(sample_event)}
        )

    @patch("cfnresponse.send")
    def test_hook_exception(self, mock_send):
        sample_event = {
            "RequestType": "Create",
            "ResponseURL": "http://example.com",
            "StackId": "stack-id",
            "RequestId": "request-id",
            "LogicalResourceId": "logical-id",
        }
        @register_handler("wrong")
        def custom_action(event, context):
            return {"message": "Custom delete executed."}
        
        sample_context = Mock(log_stream_name="log-stream")
        lambda_handler(sample_event, sample_context)
        mock_send.assert_called_once_with(
            sample_event, sample_context, 'FAILED', {'message': HookException.message, 'event': json.dumps(sample_event)}
        )
if __name__ == "__main__":
    unittest.main()
