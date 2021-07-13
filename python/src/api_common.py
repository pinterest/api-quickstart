class RateLimitException(Exception):
    """Raised when API emits a HTTP 429 Too Many Requests Error"""
    pass

class SpamException(Exception):
    """Raised when API emits a HTTP 429 due to a spam issue"""

class ApiCommon:
    """Common code for using the Pinterest API"""
    def __init__(self, api_config):
        self.api_config = api_config

    def check(self, response):
        """Check for errors and respond appropriately."""
        # Save a human-readable status for output and error handling.
        status = 'ok' if response.ok else 'request failed with reason: ' + response.reason

        # Print a short summary of the response and and error message, if necessary.
        if self.api_config.verbosity >= 1:
            print(response)
            if not response.ok:
                print(status)

        # Handle errors.
        if not response.ok:
            if self.api_config.verbosity >= 2:
                print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
            if response.status_code == 429:
                raise RateLimitException
            raise RuntimeError(status)

        if self.api_config.verbosity >= 3:
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))

    def unpack(self, response, raw=True):
        """
        Check for errors, retrieve the response, and respond appropriately.

        The response argument is the return value of a REST transaction
        executed by the requests module.

        The raw argument is used to modify the data that is returned by this function,
        so that the same ApiObject class can handle responses from both v3 and v5.
        - When raw is True, the return value is just the deserialized JSON response.
        - When raw is False, the return value for v5 is the same (the deserialized JSON
          response) but for v3 includes only the "cooked" data container inside the response.
        """

        # Save a human-readable status for output and error handling.
        status = 'ok' if response.ok else 'request failed with reason: ' + response.reason

        # Print a short summary of the response and and error message, if necessary.
        if self.api_config.verbosity >= 1:
            print(response)
            if not response.ok:
                print(status)

        # The response should always have JSON content. If the response is empty or if
        # the JSON is not valid, raise an appropriate error.
        try:
            unpacked = response.json()
        except Exception as err:
            raise RuntimeError('response does not have valid json content: ' + str(err))

        # Handle errors.
        if not response.ok:
            if self.api_config.verbosity >= 2:
                print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
                print(unpacked)
            if response.status_code == 429:
                detail = unpacked.get('message_detail') or unpacked.get('message')
                if detail and 'spam' in detail.lower(): # reason for 429 response is spam
                    raise SpamException(detail)
                raise RateLimitException
            raise RuntimeError(status)

        # Continue normal processing.
        if self.api_config.verbosity >= 3:
            print('x-pinterest-rid:', response.headers.get('x-pinterest-rid'))
            print(unpacked)

        if raw or self.api_config.version == 'v5':
            return unpacked

        # API version v3 uses a data container that is useful to unpack
        return unpacked.get('data')
