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

Requirements
------------
Available MongoDB instance to store downloaded logs informations.
It's easy start using docker:
```sh
docker run -d --name mongo_rds -p 27017:27017 mongo
```

Installing
----------

Download available log files:
```sh
# Defines if debug output will be printed to console
$ export DEBUG_ENABLED=True

# Defines if all available logs will be downloaded or only newer files (1 day)
$ export DOWNLOAD_ONLY_NEWER=True

# AWS credentials
$ export AWS_ACCESS_KEY_ID=secret_key
$ export AWS_SECRET_ACCESS_KEY=access_key
$ export AWS_DEFAULT_REGION=sa-east-1

# RDS instance identifier
$ export RDS_INSTANCE_IDENTIFIER=rds-instance-name
$ export RDS_LOG_PATH=/path/to/store/logs

# MongoDB host to store downloaded files info
$ export MONGODB_HOST=localhost
$ export MONGODB_PORT=27017
$ export MONGODB_DATABASE=rds_logs

# Start script
$ python download_rds_logs.py
```