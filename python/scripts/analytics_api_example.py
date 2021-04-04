#!/usr/bin/env python
from os.path import dirname, abspath, join
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from access_token import AccessToken
from advertisers import Advertisers
from api_config import ApiConfig
from delivery_metrics import DeliveryMetrics
from delivery_metrics import DeliveryMetricsAsyncReport
from generic_requests import download_file
from oauth_scope import Scope
from user import User
from utils import input_number
from utils import input_path_for_write

def main():
    # get configuration from defaults and/or the environment
    api_config = ApiConfig()

    # Set the API configuration verbosity to 2 to show all of requests
    # and response statuses. To see the complete responses, set verbosity to 3.
    api_config.verbosity = 2

    # Note that the OAuth will fail if your application does not
    # have access to the scope that is required to access
    # linked business accounts.
    access_token = AccessToken(api_config)
    access_token.fetch(scopes=[Scope.READ_USERS,Scope.READ_ADVERTISERS])

    # use the access token to get information about the user
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    user_id = user_me_data['id']
    print(f'User id: {user_id}')

    advertisers = Advertisers(user_id, api_config, access_token)
    advertisers_data = advertisers.get()
    advertisers.print_summary(advertisers_data)

    n_advertisers = len(advertisers_data)
    prompt = f'Please select an advertiser between 1 and {n_advertisers}:'
    index = input_number(prompt, 1, n_advertisers) - 1
    advertiser_id = advertisers_data[index]['id']

    # the output of delivery_metrics.get() is too long to be printed
    verbosity = api_config.verbosity
    api_config.verbosity = min(verbosity, 2)

    # get the full list of all delivery metrics
    delivery_metrics = DeliveryMetrics(api_config, access_token)
    metrics = delivery_metrics.get()

    api_config.verbosity = verbosity # restore verbosity

    print('Here are a couple of interesting metrics...')
    for metric in metrics:
        if metric['name'] == 'CLICKTHROUGH_1' or metric['name'] == 'IMPRESSION_1':
            delivery_metrics.print(metric)

    # To print the long list of all metrics, uncomment the next line.
    # delivery_metrics.print_all(metrics)

    # For documentation on async reports, see:
    #   https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
    print(f'Requesting report for advertiser id {advertiser_id}...')
    # Configure the report. Request 30 days of data, up to the current date.
    # For a complete set of options, see the report documentation,
    # or the code in ../src/delivery_metrics.py
    report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
             .last_30_days() \
             .level('PIN_PROMOTION') \
             .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'})

    # Request and wait for the report until it is ready.
    # The code for this process is in ../src/async_report.py.
    report.run()

    # Download the report to a file.
    # First, input the path from the command line.
    path = input_path_for_write('Please enter a file name for the report:',
                                report.filename())

    # This download_file is generic, because the report URL contains all of the
    # authentication information required to get the data. Note that the download
    # is a request to Amazon S3, not to the Pinterest API itself.
    download_file(report.url(), path)

if __name__ == '__main__':
    main()
