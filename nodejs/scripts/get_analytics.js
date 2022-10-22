#!/usr/bin/env node
import fs from 'fs';

import { AccessToken } from '../src/access_token.js';
import { Advertisers } from '../src/advertisers.js';
import { ApiConfig } from '../src/api_config.js';
import { ArgumentParser } from 'argparse';
import { common_arguments } from '../src/arguments.js';
import { Input } from '../src/utils.js';
import { Scope } from '../src/oauth_scope.js';
import { User } from '../src/user.js';
import { UserAnalytics, PinAnalytics, AdAnalytics } from '../src/analytics.js';

/**
 * This script shows how to use the Pinterest API synchronous analytics endpoints
 * to download reports for a User, Ad Account, Campaign, Ad Group, or Ad.
 *
 * This script fetches user analytics by default, which just requires an
 * access token with READ_USERS scope.
 *
 * Using this script for advertising analytics requires a login or an access token
 * for a Pinterest user account that has linked Ad Accounts. (The relationship
 * between User and Ad Accounts is 1-to-many.) To get a report with useful
 * metrics values, at least one linked Ad Account needs to have an active
 * advertising campaign. The access token requires READ_USERS and
 * READ_ADVERTISERS scopes.
 */

// This class encapsulates information about a level of the Ads structure.
class AdsEntity {
  constructor(object, kind, parent, getfn, analyticsfn, identifier) {
    this.object = object; // name as specified in command-line arguments
    this.kind = kind; // name for printing on the console
    this.parent = parent; // name of the parent entity for printing
    this.getfn = getfn; // advertisers function used to get the entity
    this.analyticsfn = analyticsfn; // analytics function used for the entity
    this.identifier = identifier; // identifier specified at this level (may be null)
  }
}

// This class is used to navigate to the appropriate level of the Ads structure
// and then get the requested analytics.
class FindAndGetAnalytics {
  constructor(advertisers, analytics, analytics_object, input, ads_entities) {
    this.advertisers = advertisers; // Advertisers instance
    this.analytics = analytics; // Analytics or AdAnalytics instance
    this.analytics_object = analytics_object; // requested type of analytics
    this.input = input; // Input instance
    this.ads_entities = ads_entities; // Array of AdsEntity
  }

  // Recursive function that prints out one level of advertising entity
  // and then calls itself to print entities at lower levels.
  async run(get_args) {
    let level = get_args.length;
    const entity = this.ads_entities[level]; // information about the entity
    const kind = entity.kind; // human readable entity type
    let entity_id;

    if (entity.identifier) {
      entity_id = entity.identifier;
      console.log(`Using the ${kind} with identifier: ${entity_id}`);
    } else {
      // Get all of the entities using the paged iterator.
      // Note: Array.from does not work with asynchronous iterators.
      const iterator = await this.advertisers[entity.getfn](...get_args);
      const entity_list = [];
      for await (const entity of iterator) {
        entity_list.push(entity);
      }

      const n_entities = entity_list.length; // number of entities found

      if (n_entities === 0) { // no entities found
        console.log(`This ${entity.parent} has no ${kind}s.`);
        return null;
      }

      this.advertisers.print_enumeration(entity_list, kind);
      // Prompt to get the entity index.
      const prompt = `Please select the ${kind} number between 1 and ${n_entities}:`;
      const index = await this.input.number(prompt, 1, n_entities);
      entity_id = entity_list[index - 1].id;
    }

    get_args.push(entity_id);

    if (entity.object === this.analytics_object) {
      return await this.analytics[entity.analyticsfn](...get_args);
    }

    level += 1;
    if (level === this.ads_entities.length) {
      return null;
    }

    // recursively traverse entities in the hierarchy below this entity
    return await this.run(get_args);
  }
}

// This main routine uses the above function to walk the ads entity
// structures, ask the user for directions, and get analytics.
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Get Analytics'
  });
  parser.add_argument('-o', '--analytics-object', {
    default: 'user',
    choices: ['user', 'pin', 'ad_account_user', 'ad_account', 'campaign', 'ad_group', 'ad'],
    help: 'kind of object used to fetch analytics'
  });
  parser.add_argument('--pin-id', {
    help: 'Get analytics for this pin identifier.'
  });
  parser.add_argument('--ad-account-id', {
    help: 'Get analytics for this ad account identifier.'
  });
  parser.add_argument('--campaign-id', {
    help: 'Get analytics for this campaign identifier.'
  });
  parser.add_argument('--ad-group-id', {
    help: 'Get analytics for this ad group identifier.'
  });
  parser.add_argument('--ad-id', {
    help: 'Get analytics for this ad identifier.'
  });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // Specifying identifier at one level requires specifying identifier at levels above.
  if (args.campaign_id && !args.ad_account_id) {
    console.log('Ad account identifier must be specified when using campaign identifier');
    process.exit(1);
  }
  if (args.ad_group_id && !args.campaign_id) {
    console.log('Campaign identifier must be specified when using ad group identifier');
    process.exit(1);
  }
  if (args.ad_id && !args.ad_ad_group_id) {
    console.log('Ad group identifier must be specified when using ad identifier');
    process.exit(1);
  }

  const api_config = new ApiConfig({
    verbosity: args.log_level
  });

  // Requesting pin analytics requires a pin_id.
  if (args.analytics_object === 'pin' && !args.pin_id) {
    console.log('Pin analytics require a pin identifier.');
    process.exit(1);
  }

  // Fetch an access token and print summary data about the User.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  const scopes = [Scope.READ_USERS];
  if (args.analytics_object !== 'user') {
    scopes.push(Scope.READ_ADVERTISERS);
  }
  await access_token.fetch({ scopes: scopes });

  // Get the user record. Some versions of the Pinterest API require the
  // user id associated with the access token.
  const user = new User(api_config, access_token);
  const user_data = await user.get();
  user.print_summary(user_data);

  let results;
  const input = new Input();
  try {
    if (args.analytics_object === 'user') {
      // Get analytics for the user account associated with the access token.
      const analytics = new UserAnalytics(
        user_data.id, api_config, access_token)
        .last_30_days()
        .metrics(['IMPRESSION', 'PIN_CLICK_RATE']);

      results = await analytics.get(null); // not calling with an ad_account_id argument
    } else if (args.analytics_object === 'pin') {
      // Get analytics for the pin.
      const analytics = new PinAnalytics(
        args.pin_id, api_config, access_token)
        .last_30_days()
        .metrics(['IMPRESSION', 'PIN_CLICK']);

      results = await analytics.get(args.ad_account_id);
    } else if (args.analytics_object === 'ad_account_user') {
      // Get analytics for the user account associated with an ad account.
      const analytics = new UserAnalytics(
        user_data.id, api_config, access_token)
        .last_30_days()
        .metrics(['IMPRESSION', 'PIN_CLICK_RATE']);

      const advertisers = new Advertisers(user_data.id, api_config, access_token);
      // When using find_and_get_analytics, analytics.get() will be called with
      // an ad_account_id argument.
      const finder = new FindAndGetAnalytics(
        advertisers, analytics, 'ad_account', input, [
          new AdsEntity('ad_account', 'Ad Account', 'User', 'get', 'get', args.ad_account_id)
        ]);
      results = await finder.run([]);
    } else {
      // Get advertising analytics for the appropriate kind of object.
      const analytics = new AdAnalytics(api_config, access_token)
        .last_30_days()
        .metrics(['SPEND_IN_DOLLAR', 'TOTAL_CLICKTHROUGH'])
        .granularity('DAY');

      const advertisers = new Advertisers(user_data.id, api_config, access_token);
      const finder = new FindAndGetAnalytics(
        advertisers, analytics, args.analytics_object, input, [
          new AdsEntity(
            'ad_account', 'Ad Account', 'User', 'get', 'get_ad_account', args.ad_account_id),
          new AdsEntity(
            'campaign', 'Campaign', 'Ad Account', 'get_campaigns', 'get_campaign', args.campaign_id),
          new AdsEntity(
            'ad_group', 'Ad Group', 'Campaign', 'get_ad_groups', 'get_ad_group', args.ad_group_id),
          new AdsEntity(
            'ad', 'Ad', 'Ad Group', 'get_ads', 'get_ad', args.ad_id)
        ]);
      results = await finder.run([]);
    }

    if (!results || results.length === 0) {
      console.log('There are no analytics results.');
      return;
    }

    // Prompt for the name of an output file and write the analytics results.
    const path = await input.path_for_write(
      'Please enter a file name for the analytics output:', 'analytics_output.json'
    );
    fs.writeFileSync(path, JSON.stringify(results, null, 2));
  } finally {
    input.close();
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
