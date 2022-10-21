// Set command line arguments that are common to all of the scripts.
export function common_arguments(parser) {
  parser.add_argument('-a', '--access-token', { help: 'access token name' });
  parser.add_argument('-l', '--log-level', { type: 'int', default: 2, help: 'level of logging verbosity' });
}
