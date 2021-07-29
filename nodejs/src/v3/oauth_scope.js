import Enum from 'enum';

// Enumerate the valid OAuth scopes.
// For details, see: https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes
export const Scope = new Enum({
  // granular scopes
  READ_DOMAINS: 'read_domains',
  READ_BOARDS: 'read_boards',
  WRITE_BOARDS: 'write_boards',
  READ_PINS: 'read_pins',
  WRITE_PINS: 'write_pins',
  READ_USERS: 'read_users',
  WRITE_USERS: 'write_users',
  READ_SECRET_BOARDS: 'read_secret_boards',
  READ_SECRET_PINS: 'read_secret_pins',
  READ_USER_FOLLOWERS: 'read_user_followers',
  WRITE_USER_FOLLOWEES: 'write_user_followees',
  READ_ADVERTISERS: 'read_advertisers',
  WRITE_ADVERTISERS: 'write_advertisers',
  READ_CAMPAIGNS: 'read_campaigns',
  WRITE_CAMPAIGNS: 'write_campaigns',
  READ_MERCHANTS: 'read_merchants',
  WRITE_MERCHANTS: 'write_merchants',
  READ_PIN_PROMOTIONS: 'read_pin_promotions',
  WRITE_PIN_PROMOTIONS: 'write_pin_promotions',

  // composite scopes
  READ_ORGANIC: 'read_organic',
  WRITE_ORGANIC: 'write_organic',
  MANAGE_ORGANIC: 'manage_organic',
  READ_SECRET: 'read_secret',
  READ_ADS: 'read_ads',
  WRITE_ADS: 'write_ads',
  MANAGE_MERCHANTS: 'manage_merchants'
});
