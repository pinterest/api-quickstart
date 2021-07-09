#!/usr/bin/env bash

#
# This script uses curl, openssl, and some helper utilities to demonstrate how to
# use OAuth authentication with the Pinterest API.
#
# To see the communications at any stage of this script, use echo to show the
# relevant variable. For example, echo "$REDIRECT_SESSION" to see the complete
# web browser session for the redirect.
#
# Prerequisites: curl, openssl, base64, jq, grep, cut
#

# Get configuration from environment or defaults.
: ${REDIRECT_PORT:=8085}
: ${PINTEREST_API_URI:=https://api.pinterest.com}
: ${PINTEREST_OAUTH_URI:=https://www.pinterest.com}
: ${REDIRECT_LANDING_URI:=https://developers.pinterest.com/manage/${PINTEREST_APP_ID}}
REDIRECT_URI="http://localhost:${REDIRECT_PORT}/"

# Note that the application id and secrect have no defaults,
# because it is best practice not to store credentials in code.
B64AUTH=$(echo -n "${PINTEREST_APP_ID}:${PINTEREST_APP_SECRET}" | base64)

# Get the authorization code by starting a browser session and handling the redirect.
echo 'getting auth_code...'

# Specify the scopes for the user to authorize via OAuth.
# This example requests typical read-only authorization.
# For more information, see: https://developers.pinterest.com/docs/redoc/#section/User-Authorization/OAuth-scopes
SCOPE="user_accounts:read"

# This call opens the browser with the oauth information in the URI.
open "${PINTEREST_OAUTH_URI}/oauth/?consumer_id=${PINTEREST_APP_ID}&redirect_uri=${REDIRECT_URI}&scope=${SCOPE}&response_type=code" &

# 1. Use netcat (nc) to run the web browser to handle the redirect from the oauth call.
# 2. Wait for the response.
# 3. Redirect using a HTTP 301 response to the landing URI.
REDIRECT_SESSION=$(nc -l localhost ${REDIRECT_PORT} 2>&1 <<EOF
HTTP/1.1 301 Moved Permanently
Location: ${REDIRECT_LANDING_URI}

EOF
)

# Cut the authorization code from the output of the web server, which includes
# the redirect URI with the authorization code.
AUTH_CODE=$(echo "${REDIRECT_SESSION}" | grep GET | cut -d ' ' -f 2 | cut -d '=' -f 2)

# Exchange the authorization code for the access token.
echo 'exchanging auth_code for access_token...'

# Execute the curl PUT command to exchange the authorization code for the access token.
# 1. Use basic authorization (constructed above) with the application id and secret.
# 2. Note that it is necessary to send x-www-form-urlencoded data.
OAUTH_RESPONSE=$(curl --silent -X POST --header "Authorization:Basic ${B64AUTH}" --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'grant_type=authorization_code' --data-urlencode "code=${AUTH_CODE}" --data-urlencode "redirect_uri=${REDIRECT_URI}" "${PINTEREST_API_URI}/v5/oauth/token")

RESPONSE_TYPE=$(echo "$OAUTH_RESPONSE" | jq -r '.["response_type"]')
echo response_type: $RESPONSE_TYPE

# Parse the JSON returned by the exchange call and retrieve the access token.
ACCESS_TOKEN=$(echo "$OAUTH_RESPONSE" | jq -r '.["access_token"]')

# The scope returned in the response includes all of the scopes that
# have been approved now or in the past by the user.
SCOPE=$(echo "$OAUTH_RESPONSE" | jq -r '.["scope"]')
echo scope: $SCOPE

# Demonstrate how to use the access token to get information about the associated user.
echo 'getting user data using the access token'
USER_RESPONSE=$(curl --silent -X GET --header "Authorization:Bearer ${ACCESS_TOKEN}" "${PINTEREST_API_URI}/v5/user_account")

# An alternative for the above command is to use the OAuth2 bearer authentication
# that is built into curl. Replace these arguments:
#   --header "Authorization:Bearer ${ACCESS_TOKEN}"
# with these arguments:
#   --oauth2-bearer "${ACCESS_TOKEN}"

# Parse the JSON response and print the data associated with the user.
ACCOUNT_TYPE=$(echo ${USER_RESPONSE} | jq -r '.["account_type"]')
USERNAME=$(echo ${USER_RESPONSE} | jq -r '.["username"]')
PROFILE_IMAGE=$(echo ${USER_RESPONSE} | jq -r '.["profile_image"]')
WEBSITE_URL=$(echo ${USER_RESPONSE} | jq -r '.["website_url"]')
echo '--- User Summary ---'
echo Account Type: $ACCOUNT_TYPE
echo Username: $USERNAME
echo Profile Image: $PROFILE_IMAGE
echo Website URL: $WEBSITE_URL
echo '--------------------'
