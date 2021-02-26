# Python Quickstart

Python code that makes it easy to get started with the Pinterest API.

## Quick Start

1. Follow the directions at the top level of this repo for configuring
your application ID, application secret, and https certificates.

2. Set up your virtualenv.

```
$ python3 -m venv ./venv/api
$ . ./venv/api/bin/activate
$ pip install -r requirements.txt
```

3. Set up the shell environment.

```
$ . ../common/scripts/api_env
```

4. Run the simplest sample script.

```
$ ./scripts/get_access_token.py
```

You should now be able to run any of the use cases in the scripts directory.

In every new shell, you'll need to activate the virtualenv and configure the environment.

```
$ . ./venv/api/bin/activate
$ . ../common/scripts/api_env
```

## PyCharm

If you want to use PyCharm as the IDE for this code, there are two ways
to configure the environment.

1. Set up the environment and run PyCharm at the command line. This is the best way to keep your Pinterest API credentials secure. For example, on MacOS:

   ```
   $ . ../common/scripts/api_env
   $ /Applications/PyCharm\ CE.app/Contents/MacOS/pycharm
   ```

2. Enter the environment variables into the PyCharm environment. Note that PyCharm will store your credentials in its workspace configuration,
which is less secure than keeping the credentials in a file that you control.

   * Print the critical variables.

     ```
     $ . ../common/scripts/api_env
     $ env | grep PINTEREST_APP
     PINTEREST_APP_ID=<number>
     PINTEREST_APP_SECRET=<string>
     $ env | grep HTTPS
     HTTPS_KEY_FILE=<path to key file>
     HTTPS_CERT_FILE=<path to cert file>
     ```

   * Start PyCharm.
   * Select Run/Edit Configurations...
   * Select Templates/Python
   * Enter the four list variables above in the Environment variables.

