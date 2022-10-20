import time
from urllib.parse import urlencode

import requests

from api_common import ApiCommon
from utils import input_one_of


class PagedIterator:
    """
    This class implements paging on top of the bookmark functionality provided
    by the Pinterest API class. It hides the paging mechanism behind an iterator.
    """

    def _get_response(self, path_maybe_with_bookmark):
        """
        Use api_object to run HTTP GET. Then, look for bookmark in response.
        """
        response = self.api_object.get_response(path_maybe_with_bookmark)
        unpacked = self.api_object.unpack(response)
        # the field with the items container is determined in the iterator constructor
        self.items = unpacked.get("items")
        self.bookmark = unpacked.get("bookmark")
        self.index = 0

    def __init__(self, api_object, path):
        """
        Save the api_object and path for subsequent pages of information.
        """
        self.api_object = api_object
        self.path = path  # to be used with the bookmark on subsequent requests
        self._get_response(path)  # first time, get response without bookmark

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.items):
            # need to fetch more data, if there is a bookmark
            if self.bookmark:
                # Determine whether the query needs to be added to the path or
                # if the bookmark will be an additional parameter at the end
                # of the query.
                delimiter = "&" if "?" in self.path else "?"
                path_with_bookmark = self.path + delimiter + "bookmark=" + self.bookmark
                self._get_response(path_with_bookmark)
                if not self.items:  # in case there is some sort of error
                    raise StopIteration
            else:
                raise StopIteration  # no bookmark => all done

        retval = self.items[self.index]  # get the current element
        self.index += 1  # increment the index for the next time
        return retval


class ApiObject(ApiCommon):
    def __init__(self, api_config, access_token):
        super().__init__(api_config)
        self.api_uri = api_config.api_uri
        self.access_token = access_token

    def get_response(self, path):
        if self.api_config.verbosity >= 2:
            print(f"GET {self.api_uri + path}")
        return requests.get(
            self.api_uri + path,
            headers=self.access_token.header(),
            allow_redirects=False,
        )

    def request_data(self, path):
        return self.unpack(self.get_response(path))

    def put_data(self, path, put_data):
        if self.api_config.verbosity >= 2:
            print(f"PUT {self.api_uri + path}")
            if self.api_config.verbosity >= 3:
                print(put_data)
        response = requests.put(
            self.api_uri + path,
            data=put_data,
            headers=self.access_token.header(),
            allow_redirects=False,
        )
        return self.unpack(response)

    def post_data(self, path, post_data=None):
        if self.api_config.verbosity >= 2:
            print(f"POST {self.api_uri + path}")
            if self.api_config.verbosity >= 3:
                print(post_data)
        response = requests.post(
            self.api_uri + path,
            json=post_data,
            headers=self.access_token.header(),
            allow_redirects=False,
        )
        return self.unpack(response)

    def delete_and_check(self, path):
        if self.api_config.verbosity >= 2:
            print(f"DELETE {self.api_uri + path}")
        response = requests.delete(
            self.api_uri + path,
            headers=self.access_token.header(),
            allow_redirects=False,
        )
        self.check(response)  # throws an exception if anything goes wrong

    def reset_backoff(self):
        """
        Reset the exponential backoff algorithm.
        """
        self.backoff = 1  # delay for backoff algorithm in seconds
        self.backoff_string = "a second"  # for human-readable output of delay

    def wait_backoff(self, message=None):
        """
        Provides an exponential backoff algorithm (up to a 10 second maximum delay)
        to determine the appropriate amount of time to wait between asynchronous
        API requests
        """
        if message:
            print(f"{message} Waiting {self.backoff_string}...")

        time.sleep(self.backoff)
        self.backoff = min(self.backoff * 2, 10)
        self.backoff_string = f"{self.backoff} seconds"

    def add_query(self, path, query_parameters=None):
        if query_parameters:
            delimiter = "&" if ("?" in path) else "?"
            path += delimiter + urlencode(query_parameters)
        return path

    def get_iterator(self, path, query_parameters=None):
        return PagedIterator(self, self.add_query(path, query_parameters))

    @classmethod
    def print_multiple(cls, page_size, object_name, object_class, paged_iterator):
        """
        Use the PagedIterator to print multiple objects.
        """
        index = 1
        page_index = 1
        for object_data in paged_iterator:
            # do this check after fetching a new page to make sure that
            # there are more pins
            if page_index > page_size:
                if "yes" == input_one_of(
                    f"Continue printing {object_name} list?", ["yes", "no"], "yes"
                ):
                    page_index = 1
                else:
                    break

            # print the object
            print(f"[{index}] ", end="")
            object_class.print_summary(object_data)

            # increment counters
            index += 1
            page_index += 1
