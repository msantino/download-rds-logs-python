# download-rds-logs-python
Python with AWS SDK to download RDS instances.

Requirements
------------

AWS env variables to validate script credentials

Installing
----------

To install this code, clone it under any directory and use the following command:
```sh
$ pip install -r requirements.txt
```

Download available log files:
```sh
# Defines if debug output will be printed to console
$ export DEBUG_ENABLED=True
# Defines if all available logs will be downloaded or only newer files (1 day)
$ export DOWNLOAD_ONLY_NEWER=True
# AWS credentials
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
$ export AWS_DEFAULT_REGION=

$ export RDS_INSTANCE_IDENTIFIER=
$ export RDS_LOG_PATH=
$ export MONGODB_HOST=
$ export MONGODB_PORT=
$ export MONGODB_DATABASE=
$ ruby download_instance_logs.rb
```