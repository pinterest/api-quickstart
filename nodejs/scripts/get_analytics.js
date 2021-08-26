#!/usr/bin/env node
import fs from 'fs';

import { ArgumentParser } from 'argparse';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Input } from '../src/utils.js';

/**
 * This script shows how to use the Pinterest API synchronous analytics endpoints
 * to download reports for a User, Ad Account, Campaign, Ad Group, or Ad. The
 * analytics_api_example script shows how to use Pinterest API v3 to retrieve
 * similar metrics using asynchronous reporting functionality.
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
  constructor(object, kind, parent, getfn, analyticsfn) {
    this.object = object; // name as specified in command-line arguments
    this.kind = kind; // name for printing on the console
    this.parent = parent; // name of the parent entity for printing
    this.getfn = getfn; // advertisers function used to get the entity
    this.analyticsfn = analyticsfn; // analytics function used for the entity
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
    const entity_id = entity_list[index - 1].id;

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
    choices: ['user', 'ad_account_user', 'ad_account', 'campaign', 'ad_group', 'ad'],
    help: 'kind of object used to fetch analytics'
  });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  const api_config = new ApiConfig({
    verbosity: args.log_level,
    version: args.api_version
  });

  // imports that depend on the version of the API
  const { AccessToken } = await import(`../src/${api_config.version}/access_token.js`);
  const { Advertisers } = await import(`../src/${api_config.version}/advertisers.js`);
  const { Analytics, AdAnalytics } = await import(`../src/${api_config.version}/analytics.js`);
  const { Scope } = await import(`../src/${api_config.version}/oauth_scope.js`);
  const { User } = await import(`../src/${api_config.version}/user.js`);

  // This API edge case is best handled up right after API set-up...
  if (api_config.version < 'v5' && args.analytics_object === 'ad_account_user') {
    console.log('User account analytics for shared accounts are');
    console.log('supported by Pinterest API v5, but not v3 or v4.');
    console.log('Try using -v5 or an analytics object besides ad_account_user.');
    process.exit(1);
  }

  // Fetch an access token and print summary data about the User.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  const scopes = [Scope.READ_USERS];
  if (args.analytics_object !== 'user') {
    scopes.push(Scope.READ_ADVERTISERS);
  }
  access_token.fetch({ scopes: scopes });

  // Get the user record. Some versions of the Pinterest API require the
  // user id associated with the access token.
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  let results;
  const input = new Input();
  try {
    if (args.analytics_object === 'user') {
      // Get analytics for the user account associated with the access token.
      const analytics = new Analytics(
        user_me_data.id, api_config, access_token)
        .last_30_days()
        .metrics(['IMPRESSION', 'PIN_CLICK_RATE']);

      results = await analytics.get(null); // not calling with an ad_account_id argument
    } else if (args.analytics_object === 'ad_account_user') {
      // Get analytics for the user account associated with an ad account.
      const analytics = new Analytics(
        user_me_data.id, api_config, access_token)
        .last_30_days()
        .metrics(['IMPRESSION', 'PIN_CLICK_RATE']);

      const advertisers = new Advertisers(user_me_data.id, api_config, access_token);
      // When using find_and_get_analytics, analytics.get() will be called with
      // an ad_account_id argument.
      const finder = new FindAndGetAnalytics(
        advertisers, analytics, 'ad_account', input, [
          new AdsEntity('ad_account', 'Ad Account', 'User', 'get', 'get')
        ]);
      results = await finder.run([]);
    } else {
      // Get advertising analytics for the appropriate kind of object.
      const analytics = new AdAnalytics(api_config, access_token)
        .last_30_days()
        .metrics(['SPEND_IN_DOLLAR', 'TOTAL_CLICKTHROUGH'])
        .granularity('DAY');

      const advertisers = new Advertisers(user_me_data.id, api_config, access_token);
      const finder = new FindAndGetAnalytics(
        advertisers, analytics, args.analytics_object, input, [
          new AdsEntity(
            'ad_account', 'Ad Account', 'User', 'get', 'get_ad_account'),
          new AdsEntity(
            'campaign', 'Campaign', 'Ad Account', 'get_campaigns', 'get_campaign'),
          new AdsEntity(
            'ad_group', 'Ad Group', 'Campaign', 'get_ad_groups', 'get_ad_group'),
          new AdsEntity(
            'ad', 'Ad', 'Ad Group', 'get_ads', 'get_ad')
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
