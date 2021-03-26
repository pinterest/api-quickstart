import mock

from integration_mocks import IntegrationMocks

class RefreshExampleTest(IntegrationMocks):
    def mock_requests_put(self, uri, headers=None, data=None):
        print('mock_requests_put', uri, headers, data)
        self.requests_put_calls += 1
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'status': 'test-status',
                                      'scope': 'test-scope',
                                      # response needs to be different each time
                                      'access_token': 'test-access-token-' + str(self.requests_put_calls),
                                      'data': {'refresh_token': 'test-refresh-token'}
                                      }
        return response

    def mock_requests_get(self, uri, headers=None, data=None):
        print('mock_requests_get', uri, headers, data)
        response = mock.MagicMock()
        response.__str__.return_value = '<Response [200]>'
        response.json.return_value = {'data':
                                      {'full_name': 'test fullname',
                                       'about': 'test about',
                                       'profile_url': 'test profile url',
                                       'pin_count': 'pin count'
                                       }
                                      }
        return response

    @mock.patch('builtins.print')
    def test_refresh_example(self, mock_print):
        from scripts.refresh_example import main # import here to see monkeypatches

        self.requests_put_calls = 0

        with self.mock_redirect():
            main() # run refresh_example

        self.assertEqual(self.requests_put_calls, 3)

        # verify expected values printed.
        # echo -n test-access-token-1 | shasum -a 256
        mock_print.assert_any_call('hashed access token: ' +
                                   '74e67193d034054f052777eb0b06d0d7fe72016282e2259d466afd6e9f8cc76a')
        # echo -n test-refresh-token | shasum -a 256
        mock_print.assert_any_call('hashed refresh token: ' +
                                   '0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde')
        # echo -n test-access-token-2 | shasum -a 256
        mock_print.assert_any_call('hashed access token: ' +
                                   '53f55e6fc30e86f042340fe6deec5b3ab5d5d6da11e3e697d41c46143a9cbc2d')
        # echo -n test-access-token-3 | shasum -a 256
        mock_print.assert_any_call('hashed access token: ' +
                                   'f7bba4838772249663c5967b48659745d782ad13bc3abc4a39580eda154ceb97')
