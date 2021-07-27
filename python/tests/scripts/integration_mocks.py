import contextlib
import mock
import os
import requests
import ssl
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

    # Note: mock_open_new has strange behavior with respect to setting instance
    # variables via the self variable. However, output via print can be observed
    # by mocking builtins.print.
    def mock_open_new(self, uri):
        print('mock_open_new: ' + uri)
        return True

    def mock_input(self, prompt):
        assert False, 'Override mock_input for this test to run.'
        
    def setUp(self):
        print('setUp')
        self.originals = self.monkeypatch([
            ('webbrowser', 'open_new', self.mock_open_new),
            ('builtins', 'input', self.mock_input)])

    def tearDown(self):
        print('tearDown')
        self.monkeypatch(self.originals)

    # The integration tests start a web server on localhost and send a response to it.
    mock_os_environ = {'PINTEREST_APP_ID': 'test-app-id',
                       'PINTEREST_APP_SECRET': 'test-app-secret',
                       'PINTEREST_API_VERSION': 'v3'
                       }

    
    """
    This function is used to start a thread that emulates the redirect sent
    after OAuth 2.0 authorization in the browser.
    """
    @contextlib.contextmanager
    def mock_redirect(self):
        """
        This is the function that is run by the thread. It needs to keep trying
        to mock the redirect until the test application is ready.
        """
        def send_test_redirect():
            for attempt in range(20): # try for 2 seconds
                time.sleep(0) # yield so that the test thread can start
                try:
                    # The real_http parameter of requests_mock must be set to True for this request to work.
                    response = requests.get(
                        'http://localhost:8085/?test-path&code=test-oauth-code',
                        allow_redirects=False)
                    print('response to redirect (301 expected): ' + str(response))
                    if response.ok:
                        return
                except:
                    # most likely, the test has not yet started the local web server yet
                    pass

                # if at first you don't succeed, try try again. but not too fast.
                time.sleep(0.1)

        # start the thread and then yield to the test application
        redirect_thread = threading.Thread(name='redirect', target=send_test_redirect)
        redirect_thread.start()
        try:
            yield
        finally:
            print('waiting for child thread that sent the redirect to end...')
            redirect_thread.join()
