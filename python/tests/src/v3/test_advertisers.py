import unittest
import mock
from mock import call
from src.v3.advertisers import Advertisers

class AdvertisersTest(unittest.TestCase):
    @mock.patch('builtins.print')
    @mock.patch('src.v3.user.ApiObject.request_data')
    @mock.patch('src.v3.user.ApiObject.__init__')
    def test_user_get(self, mock_api_object_init, mock_api_object_request_data, mock_print):
        test_advertisers = Advertisers('test_user_id', 'test_api_uri', 'test_access_token')
        mock_api_object_init.assert_called_once_with('test_api_uri', 'test_access_token')

        mock_api_object_request_data.return_value = [{'name': 'advertiser 1',
                                                      'id': 'advertiser_1_id'},
                                                     {'name': 'advertiser 2',
                                                      'id': 'advertiser_2_id'}]
        advertisers_data = test_advertisers.get()
        mock_api_object_request_data.assert_called_once_with(
            '/ads/v3/advertisers/?owner_user_id=test_user_id&include_acl=true')

        test_advertisers.print_summary(advertisers_data)
        mock_print.assert_has_calls(
            [call('Advertiser accounts available to this access token:'),
             call('[1] Name: advertiser 1, Advertiser ID: advertiser_1_id'),
             call('[2] Name: advertiser 2, Advertiser ID: advertiser_2_id')])
