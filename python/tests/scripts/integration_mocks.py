import contextlib
import mock
import os
import requests
import sys
import threading
import time
import unittest
import webbrowser

class IntegrationMocks(unittest.TestCase):
    def monkeypatch(self, patches):
        MODULE = 0
        FUNCTION = 1
        VALUE = 2

        originals = [] # contains unpatched values
        for patch in patches:
            module = patch[MODULE]
            function = patch[FUNCTION]

            # remember existing value
            originals.append((module, function, getattr(sys.modules[module], function)))

            # set patched value
            print('patching ' + module + '[' + function + '] = ' + str(patch[VALUE]))
            setattr(sys.modules[module], function, patch[VALUE])

        return originals

    def mock_open_new(self, uri):
        print('mock_open_new: ' + uri)
        return True

    def mock_requests_get(self, uri, headers=None, data=None):
        assert False, 'Override mock_requests_get for this test to run.'
        
    def mock_requests_put(self, uri, headers=None, data=None):
        assert False, 'Override mock_requests_put for this test to run.'
        
    def mock_requests_post(self, uri, headers=None, data=None):
        assert False, 'Override mock_requests_post for this test to run.'
        
    def setUp(self):
        print('setUp')
        mock.patch.dict('os.environ', self.mock_os_environ, clear=True)
        self.originals = self.monkeypatch([
            ('webbrowser', 'open_new', self.mock_open_new),
            ('requests', 'put', self.mock_requests_put),
            ('requests', 'post', self.mock_requests_post),
            ('requests', 'get', self.mock_requests_get)])

    def tearDown(self):
        print('tearDown')
        self.monkeypatch(self.originals)

    # The integration tests start a web server on localhost and send a response to it.
    # So, the https certificate set-up and an appropriate api_env are required.
    # See the README file at the top-level of this repository for more information
    # on the required set-up.
    if not os.environ.get('HTTPS_KEY_FILE') or not os.environ.get('HTTPS_KEY_FILE'):
        raise RuntimeError('Certificate set up is required for integration tests. See top-level README.')

    mock_os_environ = {'PINTEREST_APP_ID': 'test-app-id',
                       'PINTEREST_APP_SECRET': 'test-app-secret',
                       'HTTPS_KEY_FILE': os.environ['HTTPS_KEY_FILE'],
                       'HTTPS_CERT_FILE': os.environ['HTTPS_CERT_FILE']
                       }

    
    """
    This function is used to start a thread that emulates the redirect sent
    after OAuth 2.0 authorization in the browser.
    """
    @contextlib.contextmanager
    def mock_redirect(self):
        # This is the function that is run by the thread.
        def send_test_redirect():
            while True:
                # use requests.request to avoid monkey-patched function
                response = requests.request(
                    'GET',
                    'https://localhost:8085/?test-path&code=test-oauth-code',
                    allow_redirects=False)
                print('response to redirect (301 expected): ' + str(response))
                if response.ok:
                    return
                # if at first you don't succeed, try try again. but not too fast.
                time.sleep(0.5)

        redirect_thread = threading.Thread(name='redirect', target=send_test_redirect)
        redirect_thread.start()
        try:
            yield
        finally:
            print('waiting for child thread that sent the redirect to end...')
            redirect_thread.join()
