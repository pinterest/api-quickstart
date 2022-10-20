class RateLimitException(Exception):
    """Raised when API emits a HTTP 429 Too Many Requests Error"""

    pass


class SpamException(Exception):
    """Raised when API emits a HTTP 429 due to a spam issue"""


class ApiCommon:
    """Common code for using the Pinterest API"""

    def __init__(self, api_config):
        self.api_config = api_config

    def _check(self, response):
        if not hasattr(response, "ok") or not hasattr(response, "reason"):
            raise TypeError("unexpected response object: " + response)

    def check(self, response):
        """Check for errors and respond appropriately."""

        self._check(response)

        # Save a human-readable status for output and error handling.
        status = (
            "ok" if response.ok else "request failed with reason: " + response.reason
        )

        # Print a short summary of the response and and error message, if necessary.
        if self.api_config.verbosity >= 1:
            print(response)
            if not response.ok:
                print(status)

        # Handle errors.
        if not response.ok:
            if self.api_config.verbosity >= 2:
                print("x-pinterest-rid:", response.headers.get("x-pinterest-rid"))
            if response.status_code == 429:
                raise RateLimitException
            raise RuntimeError(status)

        if self.api_config.verbosity >= 3:
            print("x-pinterest-rid:", response.headers.get("x-pinterest-rid"))

    def unpack(self, response):
        """
        Check for errors, retrieve the response, and respond appropriately.

        The response argument is the return value of a REST transaction
        executed by the requests module.
        """
        self._check(response)

        # Save a human-readable status for output and error handling.
        status = (
            "ok" if response.ok else "request failed with reason: " + response.reason
        )

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
            raise RuntimeError("response does not have valid json content: " + str(err))

        # Handle errors.
        if not response.ok:
            if self.api_config.verbosity >= 2:
                print("x-pinterest-rid:", response.headers.get("x-pinterest-rid"))
                print(unpacked)
            if response.status_code == 429:
                detail = unpacked.get("message_detail") or unpacked.get("message")
                if (
                    detail and "spam" in detail.lower()
                ):  # reason for 429 response is spam
                    raise SpamException(detail)
                raise RateLimitException
            raise RuntimeError(status)

        # Continue normal processing.
        if self.api_config.verbosity >= 3:
            print("x-pinterest-rid:", response.headers.get("x-pinterest-rid"))
            print(unpacked)

        return unpacked
