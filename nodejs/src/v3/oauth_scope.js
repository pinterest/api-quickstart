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

export function print_scopes() {
  console.log(`\
Valid OAuth 2.0 scopes for Pinterest API version v3:
  read_domains         Get your website's most clicked Pins, see top saved Pins, etc.
  read_boards          See all your boards (including secret and group boards)
  write_boards         Create new boards and change board settings
  read_pins            See all public Pins and comments
  write_pins           Create new Pins
  read_users           See public data about a user (including boards, following, profile)
  write_users          Change a user's following information
  read_secret_boards   See secret boards
  read_secret_pins     See secret pins
  read_user_followers  Access a user's follows and followers
  write_user_followees Follow things for a user

  read_advertisers     See a user's advertising profile and settings
  write_advertisers    Create and manage a user's advertising profile
  read_campaigns       See data on ad campaigns, including spend, budget and performance
  write_campaigns      Create and manage ad campaigns
  read_merchants       See a user's Catalog (shopping feed)
  write_merchants      Manage a user's Catalog (shopping feed)
  read_pin_promotions  See ads and ad creatives
  write_pin_promotions Create and manage ads and ad creatives

  Composite scopes...
  read_organic         See all of a user's public data.
  write_organic        Create new Pins and boards, update public data
  manage_organic       See, update, and add to public data
  read_secret          See secret boards and secret Pins
  read_ads             See data on ad campaigns, including spend, budget and performance
  write_ads            Manage ad campaigns and see data including spend, budget and performance
  manage_merchants     See and manage a user's Catalog (shopping feed)

For more information, see:
 https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes`);
}
