import unittest
import mock
import os
import requests
import threading
import time
import webbrowser

import monkey

class GetBusinessesTest(unittest.TestCase):
    def mock_open_new(self, uri):
        print('mock_open_new: ' + uri)
        return True

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
        if (uri == 'https://api.pinterest.com/v3/users/me/'):
            self.requests_get_users_me_calls += 1
            response.json.return_value = {'data':
                                          {'full_name': 'test fullname',
                                           'about': 'test about',
                                           'profile_url': 'test profile url',
                                           'pin_count': 'pin count'
                                           }
                                          }
        elif (uri == 'https://api.pinterest.com/v3/users/me/businesses/'):
            self.requests_get_users_me_businesses_calls += 1
            response.json.return_value = {'data':
                                          {'full_name': 'test business name',
                                           'id': 'test-business-id-number'
                                           }
                                          }
        return response

    def setUp(self):
        print('setUp')
        self.originals = monkey.patch([('webbrowser', 'open_new', self.mock_open_new),
                                       ('requests', 'put', self.mock_requests_put),
                                       ('requests', 'get', self.mock_requests_get)])

    def tearDown(self):
        print('tearDown')
        monkey.patch(self.originals)
    
    mock_os_environ_minimal = {'PINTEREST_APP_ID': 'test-app-id',
                               'PINTEREST_APP_SECRET': 'test-app-secret',
                               'HTTPS_KEY_FILE': os.environ['HTTPS_KEY_FILE'],
                               'HTTPS_CERT_FILE': os.environ['HTTPS_CERT_FILE']
                               }

    @mock.patch.dict('os.environ', mock_os_environ_minimal, clear=True)
    def test_get_access_token(self):
        from scripts.get_businesses import main # import here to see monkeypatches
        webbrowser.open_new('http://oops') # test to make sure that the patch works

        """
        This function is used to emulate the redirect sent after OAuth 2.0
        authorization in the browser.
        """
        def send_test_redirect():
            while True:
                response = requests.request('GET', # use requests.request to avoid monkey-patched function
                                            'https://localhost:8085/?test-path&code=test-oauth-code',
                                            allow_redirects=False)
                print('response to redirect (301 expected): ' + str(response))
                if response.ok:
                    return
                # if at first you don't succeed, try try again. but not too fast.
                time.sleep(0.5)

        redirect_thread = threading.Thread(name='redirect', target=send_test_redirect)
        redirect_thread.start()

        self.requests_put_calls = 0
        self.requests_get_users_me_calls = 0
        self.requests_get_users_me_businesses_calls = 0

        main() # run get_access_token
        self.assertEqual(self.requests_put_calls, 1)
        self.assertEqual(self.requests_get_users_me_calls, 1)
        self.assertEqual(self.requests_get_users_me_businesses_calls, 1)

        print('waiting for child thread that sent the redirect to end...')
        redirect_thread.join()
