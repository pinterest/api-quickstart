from enum import Enum


# Enumerate the valid OAuth scopes.
# For details, see: https://developers.pinterest.com/docs/getting-started/scopes/
class Scope(Enum):
    READ_ADS = "ads:read"
    READ_BOARDS = "boards:read"
    WRITE_BOARDS = "boards:write"
    READ_PINS = "pins:read"
    WRITE_PINS = "pins:write"
    READ_USERS = "user_accounts:read"
    READ_SECRET_BOARDS = "boards:read_secret"
    WRITE_SECRET_BOARDS = "boards:write_secret"
    READ_SECRET_PINS = "pins:read_secret"
    WRITE_SECRET_PINS = "pins:write_secret"
    READ_ADVERTISERS = "ads:read"


def lookup_scope(key):
    if key == "help":
        print_scopes()
        exit(0)
    try:
        return Scope[key.upper()]
    except KeyError:
        # key did not work. try looking up by value.
        value = key.lower()  # case independent
        for scope in Scope:
            if value == scope.value:
                return scope

        print("Invalid scope:", key)
        print_scopes()
        exit(1)


def print_scopes():
    print(
        """\
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
  https://developers.pinterest.com/docs/getting-started/scopes/"""
    )
