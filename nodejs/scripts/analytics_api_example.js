#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { AdMetricsAsyncReport } from '../src/ad_metrics_async_report.js';
import { Advertisers } from '../src/advertisers.js';
import { ApiConfig } from '../src/api_config.js';
import { DeliveryMetrics } from '../src/delivery_metrics.js';
import { common_arguments } from '../src/arguments.js';
import { download_file } from '../src/generic_requests.js';
import { Input } from '../src/utils.js';
import { Scope } from '../src/oauth_scope.js';
import { User } from '../src/user.js';

/**
 * This script shows how to use the Pinterest API asynchronous report functionality
 * to download advertiser delivery metrics reports. It is adapted from sample code
 * from a Pinterest Solutions Engineer that has been useful to advertiser and
 * partner engineers who need to fetch a wide range of metrics.
 * The documentation for this API is here:
 *   https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
 *
 * Synchronous metrics retrieval is demonstrated by the get_analytics script
 * in this directory.
 *
 * Using this script requires a login or an access token for a Pinterest
 * user account that has linked Advertiser IDs. (The relationship between User
 * and Advertiser is 1-to-many.) To get a report with useful metrics values,
 * at least one linked Advertiser needs to have an active advertising campaign.
 *
 * The sequence of steps in this script is as follows:
 * 1. Fetch an access token and print summary data about the associated User.
 * 2. Get the linked Advertiser IDs and select one of the Advertiser IDs.
 * 3. Print information about metrics. This step is not typical of a
 *    production application, but does show how to access information
 *    on delivery metrics from the Pinterest API.
 * 4. Configure the options for the asynchronous report, and run the report.
 * 5. Download the report to a file.
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Analytics API Example'
  });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // Get configuration from defaults and/or the environment.
  // Set the API configuration verbosity to 2 to show all of requests
  // and response statuses. To see the complete responses, set verbosity to 3.
  const api_config = new ApiConfig({
    verbosity: args.log_level
  });

  // Step 1: Fetch an access token and print summary data about the User.
  // Note that the OAuth will fail if your application does not
  // have access to the scope that is required to access
  // linked business accounts.

  const access_token = new AccessToken(api_config, { name: args.access_token });
  await access_token.fetch({ scopes: [Scope.READ_USERS, Scope.READ_ADVERTISERS] });

  // Sample: Get my user id
  // For a future call we need to know the user id associated with
  // the access token being used.
  const user = new User(api_config, access_token);
  const user_data = await user.get();
  user.print_summary(user_data);

  const user_id = user_data.id;
  console.log(`User id: ${user_id}`);

  // Step 2: Get Advertiser IDs available to my access token and select one of them.
  // One of the first challenges many developers run into is that the relationship
  // between User and Advertiser is 1-to-many.

  // In house developers typically don't have login credentials for the main Pinterest
  // account of their brand to OAuth against.
  // We often recommend that they set up a new 'developer' Pinterest user,
  // and then request that this new account is granted access to the
  // advertiser account via:
  //   https://help.pinterest.com/en/business/article/add-people-to-your-ad-account
  // This process is also touched on in the API docs:
  //   https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/Account-Sharing

  const advertisers = new Advertisers(user_id, api_config, access_token);
  const iterator = await advertisers.get();
  const advertiser_list = [];
  for await (const advertiser of iterator) {
    advertiser_list.push(advertiser);
  }
  const n_advertisers = advertiser_list.length;

  // An advertiser id is required to request an asynchronous report.
  if (n_advertisers === 0) {
    console.log('This user id does not have any linked advertiser ids.');
    process.exit(0);
  }

  // Prompt for the advertiser id to be used to pull a report.
  console.log('Advertiser accounts available to this access token:');
  advertisers.print_enumeration(advertiser_list, 'Ad Account');
  const prompt = `Please select an advertiser between 1 and ${n_advertisers}:`;
  const input = new Input();
  try {
    const index = await input.number(prompt, 1, n_advertisers) - 1;
    const advertiser_id = advertiser_list[index].id;

    // Use Case: pulling a report about how my ads are doing.
    // I want to pull a simple report showing paid impressions
    // and clicks my ads got in the last 30 days.

    // Step 3: Learn more about the metrics available
    //   https://developers.pinterest.com/docs/api/v5/#operation/delivery_metrics/get

    // the output of delivery_metrics.get() is too long to be printed
    const verbosity = api_config.verbosity;
    api_config.verbosity = Math.min(verbosity, 2);

    // Get the full list of all delivery metrics.
    // This call is not used much in day-to-day API code, but is a useful endpoint
    // for learning about the metrics.
    try {
      const delivery_metrics = new DeliveryMetrics(api_config, access_token);
      const metrics = await delivery_metrics.get();

      console.log('Here are a couple of interesting metrics...');
      for (const metric of metrics) {
        if (metric.name === 'CLICKTHROUGH_1' ||
            metric.name === 'IMPRESSION_1') {
          delivery_metrics.print(metric);
        }
      }

      // To print the long list of all metrics, uncomment the next line.
      // delivery_metrics.print_all(metrics);
    } catch (error) {
      // This endpoint is not essential, and is not supported by all API versions.
      // So, just print the error and move along.
      console.log(error.message);
    } finally {
      api_config.verbosity = verbosity; // restore verbosity
    }

    // Step 4: Configure the options for the report
    // For documentation on async reports, see:
    //  https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/reports
    console.log(`Requesting report for advertiser id ${advertiser_id}...`);

    // Configure the report. Request 30 days of data, up to the current date.
    // For a complete set of options, see the report documentation,
    // for the code in ../src/delivery_metrics.py

    const report = new AdMetricsAsyncReport(
      api_config, access_token, advertiser_id)
      .last_30_days()
      .level('PIN_PROMOTION')
      .granularity('DAY')
      .report_format('CSV')
      .filters([{ field: 'SPEND_IN_DOLLAR', operator: 'GREATER_THAN', values: [1] }])
      .metrics(['IMPRESSION_1', 'CLICKTHROUGH_1']);

    // Request (POST) and wait (GET) for the report until it is ready.
    // This is an async process with two API calls. The first is placing a request
    // for Pinterest to generate a specific report. The second is waiting for
    // report to generate. The code for this process is in ../src/async_report.js.
    await report.run();

    // Step 5: Download the report to a file.
    // First, input the path from the command line.
    const path = await input.path_for_write(
      'Please enter a file name for the report:', report.filename()
    );

    // This download_file is generic, because the report URL contains all of the
    // authentication information required to get the data. Note that the download
    // is a request to Amazon S3, not to the Pinterest API itself.
    download_file(report.url(), path);
  } finally {
    input.close();
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
