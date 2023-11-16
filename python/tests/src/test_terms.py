import unittest
from unittest import mock

from terms import Terms


class UserTest(unittest.TestCase):
    @mock.patch("user.ApiObject.add_query")
    @mock.patch("user.ApiObject.request_data")
    @mock.patch("user.ApiObject.__init__")
    def test_related_terms(
        self, mock_api_object_init, mock_request_data, mock_add_query
    ):
        test_terms = Terms("test_api_config", "test_access_token")
        mock_api_object_init.assert_called_once_with(
            "test_api_config", "test_access_token"
        )

        mock_request_data.return_value = "test_response"
        mock_add_query.return_value = "/v5/terms/related?terms=test_terms"
        response = test_terms.get_related("test_terms")
        mock_add_query.assert_called_once_with(
            "/v5/terms/related", {"terms": "test_terms"}
        )
        mock_request_data.assert_called_once_with("/v5/terms/related?terms=test_terms")
        self.assertEqual(response, "test_response")

    @mock.patch("user.ApiObject.add_query")
    @mock.patch("user.ApiObject.request_data")
    @mock.patch("user.ApiObject.__init__")
    def test_suggested_terms_no_limit(
        self, mock_api_object_init, mock_request_data, mock_add_query
    ):
        test_terms = Terms("test_api_config", "test_access_token")

        mock_request_data.return_value = "test_response"
        mock_add_query.return_value = "/v5/terms/suggested?term=test_term"
        response = test_terms.get_suggested("test_term")
        mock_add_query.assert_called_once_with(
            "/v5/terms/suggested", {"term": "test_term"}
        )
        mock_request_data.assert_called_once_with("/v5/terms/suggested?term=test_term")
        self.assertEqual(response, "test_response")

    @mock.patch("user.ApiObject.add_query")
    @mock.patch("user.ApiObject.request_data")
    @mock.patch("user.ApiObject.__init__")
    def test_suggested_terms_with_limit(
        self, mock_api_object_init, mock_request_data, mock_add_query
    ):
        test_terms = Terms("test_api_config", "test_access_token")

        mock_request_data.return_value = "test_response"
        mock_add_query.return_value = "/v5/terms/suggested?term=test_term&limit=5"
        response = test_terms.get_suggested("test_term", limit=5)
        mock_add_query.assert_called_once_with(
            "/v5/terms/suggested", {"term": "test_term", "limit": 5}
        )
        mock_request_data.assert_called_once_with(
            "/v5/terms/suggested?term=test_term&limit=5"
        )
        self.assertEqual(response, "test_response")
