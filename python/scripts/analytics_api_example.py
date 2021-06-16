#!/usr/bin/env python
from os.path import dirname, abspath, join
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from access_token import AccessToken
from api_config import ApiConfig
from generic_requests import download_file
from utils import input_number
from utils import input_path_for_write

def main():
    """
    This script shows how to use the Pinterest API asynchronous report functionality
    to download advertiser delivery metrics reports. It is adapted from sample code
    from a Pinterest Solutions Engineer that has been useful to advertiser and
    partner engineers who need to fetch a wide range of metrics.
    The documentation for this API is here:
      https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports

    Using this script requires a login or an access token for a Pinterest
    user account that has linked Advertiser IDs. (The relationship between User
    and Advertiser is 1-to-many.) To get a report with useful metrics values,
    at least one linked Advertiser needs to have an active advertising campaign.

    The sequence of steps in this script is as follows:
    1. Fetch an access token and print summary data about the associated User.
    2. Get the linked Advertiser IDs and select one of the Advertiser IDs.
    3. Print information about metrics. This step is not typical of a
       production application, but does show how to access information
       on delivery metrics from the Pinterest API.
    4. Configure the options for the asynchronous report, and run the report.
    5. Download the report to a file.
    """
    # get configuration from defaults and/or the environment
    api_config = ApiConfig()

    # Set the API configuration verbosity to 2 to show all of requests
    # and response statuses. To see the complete responses, set verbosity to 3.
    api_config.verbosity = 2

    # imports that depend on the version of the API
    from advertisers import Advertisers
    from delivery_metrics import DeliveryMetrics
    from delivery_metrics import DeliveryMetricsAsyncReport
    from oauth_scope import Scope
    from user import User

    # Step 1: Fetch an access token and print summary data about the User.
    # Note that the OAuth will fail if your application does not
    # have access to the scope that is required to access
    # linked business accounts.
    access_token = AccessToken(api_config)
    access_token.fetch(scopes=[Scope.READ_USERS,Scope.READ_ADVERTISERS])

    # Sample: Get my user id
    # For a future call we need to know the user id associated with the access token being used
    user_me = User('me', api_config, access_token)
    user_me_data = user_me.get()
    user_me.print_summary(user_me_data)

    user_id = user_me_data['id']
    print(f'User id: {user_id}')

    # Step 2: Get Advertiser IDs available to my access token and select one of them.
    # One of the first challenges many developers run into is that the relationship between User and Advertiser is 1-to-many
    # In house developers typically don't have login credentials for the main Pinterest account of their brand to OAuth against.
    # We often reccomend that they set up a new "developer" Pinterest user, and then request that this new account is granted
    # access to the advertiser account via https://help.pinterest.com/en/business/article/add-people-to-your-ad-account
    # This process is also touched on in the API docs https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/Account-Sharing
    advertisers = Advertisers(user_id, api_config, access_token)
    advertisers_data = advertisers.get()
    advertisers.print_summary(advertisers_data)
    n_advertisers = len(advertisers_data)

    # An advertiser id is required to request an asynchronous report.
    if not n_advertisers:
        exit('This user id does not have any linked advertiser ids.')

    # Prompt for the advertiser id to be used to pull a report.
    prompt = f'Please select an advertiser between 1 and {n_advertisers}:'
    index = input_number(prompt, 1, n_advertisers) - 1
    advertiser_id = advertisers_data[index]['id']

    # Case: pulling a report about how my ads are doing. I want to pull a simple report showing paid impressions
    # and clicks my ads got in the last 30 days.

    # Step 3: Learn more about the metrics available
    # https://developers.pinterest.com/docs/redoc/combined_reporting/#operation/ads_v3_get_delivery_metrics_handler_GET

    # the output of delivery_metrics.get() is too long to be printed
    verbosity = api_config.verbosity
    api_config.verbosity = min(verbosity, 2)

    # Get the full list of all delivery metrics.
    # This call is not used much in day-to-day API code, but is a useful endpoint
    # for learning about the metrics.
    delivery_metrics = DeliveryMetrics(api_config, access_token)
    metrics = delivery_metrics.get()

    api_config.verbosity = verbosity # restore verbosity

    print('Here are a couple of interesting metrics...')
    for metric in metrics:
        if metric['name'] == 'CLICKTHROUGH_1' or metric['name'] == 'IMPRESSION_1':
            delivery_metrics.print(metric)

    # To print the long list of all metrics, uncomment the next line.
    # delivery_metrics.print_all(metrics)

    # Step 4: Configure the options for the report
    # For documentation on async reports, see:
    #   https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
    print(f'Requesting report for advertiser id {advertiser_id}...')
    # Configure the report. Request 30 days of data, up to the current date.
    # For a complete set of options, see the report documentation,
    # or the code in ../src/delivery_metrics.py
    report = DeliveryMetricsAsyncReport(api_config, access_token, advertiser_id) \
             .last_30_days() \
             .level('PIN_PROMOTION') \
             .metrics({'IMPRESSION_1', 'CLICKTHROUGH_1'}) \
             .tag_version(3)

    # Request (POST) and wait (GET) for the report until it is ready.
    # This is an async process with two API calls. The first is placing a request
    # for Pinterest to generate a specific report. The second is waiting for report to generate.
    # The code for this process is in ../src/async_report.py.
    report.run()

    # Step 5: Download the report to a file.
    # First, input the path from the command line.
    path = input_path_for_write('Please enter a file name for the report:',
                                report.filename())

    # This download_file is generic, because the report URL contains all of the
    # authentication information required to get the data. Note that the download
    # is a request to Amazon S3, not to the Pinterest API itself.
    download_file(report.url(), path)

if __name__ == '__main__':
    main()
