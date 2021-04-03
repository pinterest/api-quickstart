#!/usr/bin/env python
from os.path import dirname, abspath, join
import sys

sys.path.append(abspath(join(dirname(__file__), '..', 'src')))

from access_token import AccessToken
from advertisers import Advertisers
from api_config import ApiConfig
from delivery_metrics import DeliveryMetrics
from generic_requests import download_file
from oauth_scope import Scope
from user import User
from utils import input_number
from utils import input_path_for_write

def main():
    # get configuration from defaults and/or the environment
    api_config = ApiConfig()

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

    delivery_metrics = DeliveryMetrics(api_config, access_token)
    metrics = delivery_metrics.get()

    print('Here are a couple of interesting metrics...')
    for metric in metrics:
        if metric['name'] == 'CLICKTHROUGH_1' or metric['name'] == 'IMPRESSION_1':
            delivery_metrics.print(metric)

    # delivery_metrics.print_all(metrics)

    print(f'Requesting report for advertiser id {advertiser_id}...')
    report_token = delivery_metrics.request_report(advertiser_id,
                                                   '2021-01-01', '2021-04-02',
                                                   'PIN_PROMOTION',
                                                   ['IMPRESSION_1', 'CLICKTHROUGH_1'])
    report_url = delivery_metrics.wait_report(advertiser_id, report_token)
    download_file(report_url, input_path_for_write('Please enter a file name for the report:',
                                                   report_url.split('/')[-1].split('?')[0]))

if __name__ == '__main__':
    main()
