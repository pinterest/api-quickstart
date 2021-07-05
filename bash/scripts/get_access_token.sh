#!/usr/bin/env bash
#
# OAuth is version specific, so this script just calls the appropriate
# version-specific script, based on the PINTEREST_API_VERSION environment
# variable. More documentation is available in each version-specific script.
#
: ${PINTEREST_API_VERSION:=v3}

SCRIPT_NAME="${BASH_SOURCE[0]}"

# get the location of this script
SCRIPT_DIR=$(cd $(dirname ${SCRIPT_NAME}); pwd)

VERSION_SPECIFIC_SCRIPT="${SCRIPT_DIR}/${PINTEREST_API_VERSION}/get_access_token.sh"
echo running version specific script: ${VERSION_SPECIFIC_SCRIPT}
exec ${VERSION_SPECIFIC_SCRIPT}
