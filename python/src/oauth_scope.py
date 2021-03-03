from enum import Enum

# Enumerate the valid OAuth scopes.
# For details, see: https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes
class Scope(Enum):
    # granular scopes
    READ_DOMAINS = 'read_domains'
    READ_BOARDS = 'read_boards'
    WRITE_BOARDS = 'write_boards'
    READ_PINS = 'read_pins'
    WRITE_PINS = 'write_pins'
    READ_USERS = 'read_users'
    WRITE_USERS = 'write_users'
    READ_SECRET_BOARDS = 'READ_SECRET_BOARDS'
    READ_SECRET_PINS = 'READ_SECRET_PINS'
    READ_USER_FOLLOWERS = 'READ_USER_FOLLOWERS'
    WRITE_USER_FOLLOWEES = 'WRITE_USER_FOLLOWEES'
    READ_ADVERTISERS = 'read_advertisers'
    WRITE_ADVERTISERS = 'WRITE_ADVERTISERS'
    READ_CAMPAIGNS = 'READ_CAMPAIGNS'
    WRITE_CAMPAIGNS = 'WRITE_CAMPAIGNS'
    READ_MERCHANTS = 'READ_MERCHANTS'
    WRITE_MERCHANTS = 'WRITE_MERCHANTS'
    READ_PIN_PROMOTIONS = 'READ_PIN_PROMOTIONS'
    WRITE_PIN_PROMOTIONS = 'WRITE_PIN_PROMOTIONS'

    # composite scopes
    READ_ORGANIC = 'READ_ORGANIC'
    WRITE_ORGANIC = 'WRITE_ORGANIC'
    MANAGE_ORGANIC = 'MANAGE_ORGANIC'
    READ_SECRET = 'READ_SECRET'
    READ_ADS = 'READ_ADS'
    WRITE_ADS = 'WRITE_ADS'
    MANAGE_MERCHANTS = 'MANAGE_MERCHANTS'
