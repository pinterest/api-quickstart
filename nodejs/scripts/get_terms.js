#!/usr/bin/env node
import { ArgumentParser } from 'argparse';

import { AccessToken } from '../src/access_token.js';
import { ApiConfig } from '../src/api_config.js';
import { common_arguments } from '../src/arguments.js';
import { Scope } from '../src/oauth_scope.js';
import { Terms } from '../src/terms.js';

/**
 * This script shows how to use the Terms endpoint to
 * view related and suggested terms for ads targeting.
 */
async function main(argv) {
  const parser = new ArgumentParser({
    description: 'Get Related or Suggested Terms'
  });
  parser.add_argument('terms', { help: 'Comma-separated list of terms' });
  parser.add_argument('-r', '--related', { help: 'Get related terms', action: 'store_true' });
  parser.add_argument('-s', '--suggested', { help: 'Get suggested terms', action: 'store_true' });
  // limit has to be n because -l is already used for --log-level
  parser.add_argument('-n', '--limit', { help: 'Limit the number of suggested terms' });
  common_arguments(parser);
  const args = parser.parse_args(argv);

  // exactly one of --related or --suggested must be specified
  if (!args.related && !args.suggested) {
    parser.error('Please specify --related or --suggested');
  }

  if (args.related && args.suggested) {
    parser.error('Please specify only one of --related or --suggested');
  }

  // --limit can only be used with --suggested
  if (args.related && args.limit) {
    parser.error('Please do not specify --limit with --related');
  }

  // suggested terms can only take one term
  if (args.suggested && args.terms.includes(',')) {
    parser.error('Please specify only one term with --suggested');
  }

  // get configuration from defaults and/or the environment
  const api_config = new ApiConfig({ verbosity: args.log_level });

  // Note: It's possible to use the same API configuration with
  // multiple access tokens, so these objects are kept separate.
  const access_token = new AccessToken(api_config, { name: args.access_token });
  await access_token.fetch({ scopes: [Scope.READ_ADS] });

  const terms = new Terms(api_config, access_token);
  if (args.related) {
    const related_terms = await terms.get_related(args.terms);
    terms.print_related_terms(related_terms);
  } else { // must be args.suggested
    const suggested_terms = await terms.get_suggested(args.terms, { limit: args.limit });
    terms.print_suggested_terms(suggested_terms);
  }
}

if (!process.env.TEST_ENV) {
  main(process.argv.slice(2));
}
