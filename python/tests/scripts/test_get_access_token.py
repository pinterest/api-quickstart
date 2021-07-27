import mock
import requests
import requests_mock
import sys

from integration_mocks import IntegrationMocks

class GetAccessTokenTest(IntegrationMocks):
    # real_http is required for the redirect in integration_mocks to work
    @requests_mock.Mocker(real_http=True)
    @mock.patch('builtins.print')
    def test_get_access_token(self, rm, mock_print):
        rm.put('https://api.pinterest.com/v3/oauth/access_token/',
               json={'status': 'test-status',
                     'scope': 'test-scope',
                     'access_token': 'test-access-token',
                     'data': {'refresh_token': 'test-refresh-token'}
                     })
        rm.get('https://api.pinterest.com/v3/users/me/',
               json={'data':
                     {'full_name': 'test fullname',
                      'id': 'test user id',
                      'about': 'test about',
                      'profile_url': 'test profile url',
                      'pin_count': 'pin count'
                      }
                     })

        from scripts.get_access_token import main # import here to see monkeypatches

        with mock.patch('builtins.open') as mock_open:
            with mock.patch.dict('os.environ', self.mock_os_environ, clear=True):
                mock_open.side_effect = FileNotFoundError # no access_token.json file
                with self.mock_redirect():
                    main() # run get_access_token

        # verify expected values printed. see unit tests for values
        mock_print.assert_any_call('mock_open_new: ' +
                                   'https://www.pinterest.com/oauth/?consumer_id=test-app-id' +
                                   '&redirect_uri=http://localhost:8085/&response_type=code&' +
                                   'refreshable=True')
        mock_print.assert_any_call('hashed access token: ' +
                                   '597480d4b62ca612193f19e73fe4cc3ad17f0bf9cfc16a7cbf4b5064131c4805')
        mock_print.assert_any_call('hashed refresh token: ' +
                                   '0a9b110d5e553bd98e9965c70a601c15c36805016ba60d54f20f5830c39edcde')
