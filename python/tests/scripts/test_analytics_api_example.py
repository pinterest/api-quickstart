import json
import mock
from mock import call

from integration_mocks import IntegrationMocks

class AnalyticsApiExampleTest(IntegrationMocks):
    """
    Test all of the different stages of the analytics API example.
    """
    report_url_filename = 'here_is_the_filename.txt' # filename in the report url
    download_filename = 'test_report_file.txt' # filename "entered" for download

    def mock_requests_post(self, uri, headers=None, data=None, allow_redirects=True):
        # request from AsyncReport.request_report
        print('mock_requests_post', uri, headers, data)
        self.requests_post_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'data': {'token': 'test-report-token'}}
        return response

    def mock_requests_get(self, uri, headers=None, data=None, stream=False, allow_redirects=True):
        print('mock_requests_get', uri, headers, data)
        self.requests_get_calls += 1
        report_url = f'test-report-url/x-y-z/{self.report_url_filename}?long-identifier-string'
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        if (uri == 'https://api.pinterest.com/v3/users/me/'):
            # request from User.get
            response.json.return_value = {'data':
                                          {'full_name': 'test fullname',
                                           'id': 'test_user_id',
                                           'about': 'test about',
                                           'profile_url': 'test profile url',
                                           'pin_count': 'pin count'
                                           }
                                          }
        elif (uri == 'https://api.pinterest.com/ads/v3/advertisers/?owner_user_id=test_user_id&include_acl=true'):
            # request from Advertisers.get
            response.json.return_value = {'data':
                                          [{'name': 'test advertiser 1', 'id': 'adv_1_id'},
                                           {'name': 'test advertiser 2', 'id': 'adv_2_id'},
                                           {'name': 'test advertiser 3', 'id': 'adv_3_id'}
                                           ]}
        elif (uri == 'https://api.pinterest.com/ads/v3/resources/delivery_metrics/'):
            # request from DeliveryMetrics.get
            response.json.return_value = {'data':
                                          {'metrics':
                                           [{'name': 'CLICKTHROUGH_1', 'definition': 'clickthrough description'},
                                            {'name': 'metric_3', 'definition': 'yet another metric'},
                                            {'name': 'IMPRESSION_1', 'definition': 'impression description'}
                                           ]}}
        elif (uri == 'https://api.pinterest.com/ads/v3/reports/async/adv_2_id/delivery_metrics/?token=test-report-token'):
            # request from AsyncReport.poll_report
            response.json.return_value = {'data': {'report_status': 'FINISHED', 'url': report_url}}
        elif (uri == report_url):
            # request from generic_requests.download_file
            response.__enter__.return_value = response # download_file uses a context manager
            response.iter_content.return_value = ['this is the content ', 'of the report']
        else:
            raise ValueError(f'unexpected GET: {uri}')
        return response

    def mock_input(self, prompt):
        print('mock_input', prompt)
        self.input_calls += 1
        if (prompt == '[1] '): # Please select an advertisers between 1 and N
            return '2' # select the second advertiser
        if (prompt == f'[{self.report_url_filename}] '): # Please enter a file name for the report
            return self.download_filename # check the retrieved filename and change it
        raise ValueError(f'unexpected input prompt: {prompt}')

    # @mock.patch('builtins.print')
    def test_analytics_api_example(self):
        from scripts.analytics_api_example import main # import here to see monkeypatches

        self.requests_post_calls = 0
        self.requests_get_calls = 0
        self.input_calls = 0

        access_token_dict = {'name': 'access_token_from_file',
                             'access_token': 'test access token from json',
                             'refresh_token': 'test refresh token from json'
                             }

        # Mock the access_token.json file in order to avoid having to
        # do the redirect through a webserver running on localhost,
        # which is tested in other scripts.
        mock_file = mock.MagicMock()
        mock_file.read.return_value = json.dumps(access_token_dict)
        # Mocking __enter__ provides for the open call in a context manager.
        mock_file.__enter__.return_value = mock_file

        with mock.patch('builtins.open') as mock_open:
            mock_open.return_value = mock_file
            main() # run analytics_api_example
            mock_open.assert_any_call(self.download_filename, 'wb')

        self.assertEqual(self.requests_post_calls, 1)
        self.assertEqual(self.requests_get_calls, 5)
        self.assertEqual(self.input_calls, 2)
        mock_file.write.assert_has_calls([call('this is the content '),
                                          call('of the report')])
