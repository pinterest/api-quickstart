# Bash Quickstart

Shell code that makes it as easy as possible to see how the Pinterest API works.

## Quick Start

1. Netcat (the `nc` command) is used to run a simple web server to receive the OAuth redirect and is available on many operating systems. Check to make sure that it is installed on your development system by running `nc -h`. MacOS has netcat by default. Use your operating system's package manager to install netcat if necessary.

2. Follow the directions in the README at the top level of this repo for configuring your application ID and application secret.

3. From the top of this repo, change your working directory to this directory: `cd bash`

4. Set up the shell environment.

   ```
   $ . ../common/scripts/api_env
   ```

5. Run the sample script.

   ```
   $ ./scripts/get_access_token.sh
   ```
