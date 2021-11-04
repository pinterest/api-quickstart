import Enum from 'enum';

// Enumerate the valid OAuth scopes.
// For details, see: https://developers.pinterest.com/docs/api/v5/#tag/Scopes
export const Scope = new Enum({
  // scopes names that are compatible across different API versions
  READ_ADS: 'ads:read',
  READ_BOARDS: 'boards:read',
  WRITE_BOARDS: 'boards:write',
  READ_PINS: 'pins:read',
  WRITE_PINS: 'pins:write',
  READ_USERS: 'user_accounts:read',
  READ_SECRET_BOARDS: 'boards:read_secret',
  WRITE_SECRET_BOARDS: 'boards:write_secret',
  READ_SECRET_PINS: 'pins:read_secret',
  WRITE_SECRET_PINS: 'pins:write_secret',
  READ_ADVERTISERS: 'ads:read',

  // Scope names that are specific to v5.
  // Keys for this Enum should always be converted to upper case
  // to provide case independence.
  'ADS:READ': 'ads:read',
  'BOARDS:READ': 'boards:read',
  'BOARDS:READ_SECRET': 'boards:read_secret',
  'BOARDS:WRITE': 'boards:write',
  'BOARDS:WRITE_SECRET': 'boards:write_secret',
  'PINS:READ': 'pins:read',
  'PINS:READ_SECRET': 'pins:read_secret',
  'PINS:WRITE': 'pins:write',
  'PINS:WRITE_SECRET': 'pins:write_secret',
  'USER_ACCOUNTS:READ': 'user_accounts:read'
});

export function print_scopes() {
  console.log(`
Valid OAuth 2.0 scopes for Pinterest API version v5:
  ads:read            Read access to advertising data

  boards:read         Read access to boards
  boards:read_secret  Read access to secret boards
  boards:write        Write access to create, update, or delete boards
  boards:write_secret Write access to create, update, or delete secret boards

  pins:read           Read access to Pins
  pins:read_secret    Read access to secret Pins
  pins:write          Write access to create, update, or delete Pins
  pins:write_secret   Write access to create, update, or delete secret Pins

  user_accounts:read  Read access to user accounts

For more information, see:
  https://developers.pinterest.com/docs/api/v5/#tag/Scopes`);
}
