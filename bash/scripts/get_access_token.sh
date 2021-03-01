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
: ${HTTPS_KEY_FILE:=localhost-key.pem}
: ${HTTPS_CERT_FILE:=localhost.pem}
: ${PINTEREST_API_URI:=https://api.pinterest.com}
: ${PINTEREST_OAUTH_URI:=https://www.pinterest.com}
: ${REDIRECT_LANDING_URI:=https://developers.pinterest.com/manage/${PINTEREST_APP_ID}}
REDIRECT_URI="https://localhost:${REDIRECT_PORT}/"

# Note that the application id and secrect have no defaults,
# because it is best practice not to store credentials in code.
B64AUTH=$(echo -n "${PINTEREST_APP_ID}:${PINTEREST_APP_SECRET}" | base64)

# Get the authorization code by starting a browser session and handling the redirect.
echo 'getting auth_code'

# This call opens the browser with the oauth information in the URI.
# The open call is backgrounded, because there is a race condition between starting
# the browser and starting the web server to handle the response. It is unlikely that
# the human user will click the button in the browser before the web server starts.
# This race condition can be avoided by storing the access token in a temporary file,
# reversing the order of the browser and web server, and backgrounding the web server.
# The extra complexity doesn't seem worthwhile for this simple script.
open "${PINTEREST_OAUTH_URI}/oauth/?consumer_id=${PINTEREST_APP_ID}&redirect_uri=${REDIRECT_URI}&response_type=code" &

# 1. Use openssl to run the web browser to handle the redirect from the oauth call.
# 2. Wait for the response.
# 3. Redirect using a HTTP 301 response to the landing URI.
REDIRECT_SESSION=$(openssl s_server -accept ${REDIRECT_PORT} -cert ${HTTPS_CERT_FILE} -key ${HTTPS_KEY_FILE} 2>&1 <<EOF
HTTP/1.1 301 Moved Permanently
Location: ${REDIRECT_LANDING_URI}

Q
EOF
)

# Cut the authorization code from the output of the web server, which includes
# the redirect URI with the authorization code.
AUTH_CODE=$(echo "${REDIRECT_SESSION}" | grep GET | cut -d ' ' -f 2 | cut -d '=' -f 2)

# Exchange the authorization code for the access token.
echo 'exchanging auth_code for access_token'

# Construct the data for the PUT via curl.
PUT_DATA="{\"code\": \"${AUTH_CODE}\", \"redirect_uri\": \"${REDIRECT_URI}\", \"grant_type\": \"authorization_code\"}"

# Execute the curl PUT command to exchange the authorization code for the access token.
# 1. Use basic authorization (constructed above) with the application id and secret.
# 2. Note that it is necessary to specify JSON as the content type.
OAUTH_RESPONSE=$(curl --silent -X PUT --header "Authorization:Basic ${B64AUTH}" --header 'Content-Type: application/json' --data "${PUT_DATA}" "${PINTEREST_API_URI}/v3/oauth/access_token/")

# Parse the JSON returned by the exchange call and retrieve the access token.
ACCESS_TOKEN=$(echo "$OAUTH_RESPONSE" | jq -r '.["access_token"]')

# Demonstrate how to use the access token to get information about the associated user.
echo 'getting user data using the access token'
USER_RESPONSE=$(curl --silent -X GET --header "Authorization:Bearer ${ACCESS_TOKEN}" "${PINTEREST_API_URI}/v3/users/me/")

# Parse the JSON response and print the data associated with the user.
echo ${USER_RESPONSE} | jq '.["data"]'
