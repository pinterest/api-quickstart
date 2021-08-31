#!/usr/bin/env node
import { ArgumentParser } from 'argparse';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Input } from '../src/utils.js';

/**
 * This script shows how to use the Pinterest API endpoints to download
 * information about Ad Accounts, Campaigns, Ad Groups, and Ads.

 * Using this script requires a login or an access token for a Pinterest
 * user account that has linked Ad Accounts. (The relationship between User
 * and Ad Accounts is 1-to-many.) To get a report with useful metrics values,
 * at least one linked Ad Account needs to have an active advertising campaign.
 */

// Recursive function that prints out one level of advertising entity
// and then calls itself to print entities at lower levels.
async function fetch_and_print(
  advertisers, input, ads_entities, get_args, level) {
  const entity = ads_entities[level]; // information about the entity
  const kind = entity.kind; // human readable entity type

  // Get all of the entities using the paged iterator.
  // Note: Array.from does not work with asynchronous iterators.
  const iterator = await advertisers[entity.getfn](...get_args);
  const entity_list = [];
  for await (const entity of iterator) {
    entity_list.push(entity);
  }

  const n_entities = entity_list.length; // number of entities found
  const indent = input ? '' : '  '.repeat(level); // used for printing

  if (n_entities === 0) { // no entities found
    console.log(`${indent}This ${entity.parent} has no ${kind}s.`);
    return;
  }

  // decide which entities to do next
  level += 1;
  const print_all = !input || level === ads_entities.length;
  let range; // entities for iteration at the end of this function
  if (print_all) { // keep going for all entities
    range = entity_list;
  } else { // ask the user which entity
    advertisers.print_enumeration(entity_list, kind);
    // Prompt to get the entity index.
    const prompt = `Please select the ${kind} number between 1 and ${n_entities}:`;
    const index = await input.number(prompt, 1, n_entities);
    range = entity_list.slice(index - 1, index);
  }

  // for either the user-selected entity or all entities...
  for (const entity of range) {
    if (print_all) { // print the entity
      console.log(`${indent}${advertisers.summary(entity, kind)}`);
    }

    // recursively fetch the entities in the hierarchy below this entity
    if (level < ads_entities.length) {
      get_args.push(entity.id); // descend into this entity
      await fetch_and_print(advertisers, input, ads_entities, get_args, level);
      get_args.pop(entity.id); // restore for the next entity
    }
  }
}

// This main routine uses the above function to walk the ads entity
// structures, print information, and ask the user for directions.
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Advertisers API Example'
  });
  parser.add_argument('--all-ads', {
    action: 'store_true',
    help: 'print all ads information'
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
  const { Scope } = await import(`../src/${api_config.version}/oauth_scope.js`);
  const { User } = await import(`../src/${api_config.version}/user.js`);

  // Step 1: Fetch an access token and print summary data about the User.
  // Note that the OAuth will fail if your application does not
  // have access to the scope that is required to access
  // linked business accounts.

  const access_token = new AccessToken(api_config, { name: args.access_token });
  await access_token.fetch({ scopes: [Scope.READ_USERS, Scope.READ_ADVERTISERS] });

  // Sample: Get my user id
  // For a future call we need to know the user id associated with
  // the access token being used.
  const user_me = new User('me', api_config, access_token);
  const user_me_data = await user_me.get();
  user_me.print_summary(user_me_data);

  // Step 2: Walk the ads entity structure.
  // One of the first challenges many developers run into is that the relationship
  // between User and Ad Accounts is 1-to-many.
  // In house developers typically don't have login credentials for the main Pinterest
  // account of their brand to OAuth against.
  // We often recommend that they set up a new "developer" Pinterest user,
  // and then request that this new account is granted access to the
  // advertiser account via:
  //   https://help.pinterest.com/en/business/article/add-people-to-your-ad-account
  // This process is also touched on in the API docs:
  //   https://developers.pinterest.com/docs/redoc/combined_reporting/#tag/Account-Sharing
  const advertisers = new Advertisers(
    user_me_data.id, api_config, access_token);

  const ads_entities = [
    { kind: 'Ad Account', parent: 'User', getfn: 'get' },
    { kind: 'Campaign', parent: 'Ad Account', getfn: 'get_campaigns' },
    { kind: 'Ad Group', parent: 'Campaign', getfn: 'get_ad_groups' },
    { kind: 'Ad', parent: 'Ad Group', getfn: 'get_ads' }
  ];

  const input = args.all_ads ? null : new Input();
  try {
    await fetch_and_print(advertisers, input, ads_entities, [], 0);
  } finally {
    if (input) {
      input.close();
    }
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
