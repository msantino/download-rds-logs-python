import boto3
import os
from sys import exit
from lib import rds_log
from lib import feedback
from lib.Database import Database
from datetime import datetime, time

# Defines output from feedback.debug()
feedback.debug_enabled = os.getenv('DEBUG_ENABLED', True)
download_only_newer = os.getenv('DOWNLOAD_ONLY_NEWER', True)

# AWS RDS Client
rds_client = boto3.client(
    'rds',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', ''),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', ''),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'sa-east-1')
)

# Local RDS Configs
rds_config = {
    "rds_instance_identifier": os.getenv('RDS_INSTANCE_IDENTIFIER', ''),
    "rds_logs_path": os.getenv('RDS_LOG_PATH', ''),
    "rds_number_of_lines": 1000, # do not increment too much, will truncate lines
    "marker": '0'
}

# Mongodb Config
db_config = {
    "host": os.getenv('MONGODB_HOST', 'localhost'),
    "port": os.getenv('MONGODB_PORT', 27017),
    "database": os.getenv('MONGODB_DATABASE', 'rds_logs'),
}

""" Inicio do Script """
feedback.start( rds_config )

# Database Instance
db = Database(db_config)


log_files = rds_log.list_available_log_files( rds_client, rds_config['rds_instance_identifier'])
for log in log_files:

    # Check date from logfile name. If corresponds to older than 2 days will skip
    file_date = rds_log.get_date_from_log_name( log['LogFileName'] )
    if abs((file_date - datetime.now()).days) > 0 and download_only_newer:
        feedback.debug('Skiping log due to oldest file time [{}]'.format(file_date))
        continue

    if abs((file_date - datetime.now()).seconds) > 3600:
        feedback.debug('Skiping log due to oldest file hour [{}]'.format(file_date))
        continue

    # Reset global marker
    rds_config['marker'] = '0'

    feedback.debug('Marker 1: {}'.format(rds_config['marker']))
    feedback.output( 'Start processing file {}'.format(log['LogFileName']) )
    feedback.debug( 'Size to download (from RDS): {}'.format(log['Size']) )
    feedback.debug( '== DEBUG (RDS_LOG): {}'.format(log) )

    working_file_name =  log['LogFileName'].split('/')[1]
    local_file_name = rds_log.get_full_file_name( rds_config['rds_logs_path'], rds_config['rds_instance_identifier'], working_file_name )
    feedback.debug( 'Local file name: {}'.format(local_file_name) )
    local_file_size = 0 if not os.path.isfile(local_file_name) else os.stat(local_file_name).st_size

    # Check if local file size corresponds to rds file size
    feedback.debug( 'Size of file existing on disk: {}'.format(local_file_size) )
    if local_file_size+102400 >= int(log['Size']):
        feedback.output( 'Skiping file due to complete size on disk.' )
        continue

    # Gets database file info
    db_log = db.get_log(log['LogFileName'])
    feedback.debug( '== DEBUG (RDS_LOG): {}'.format(db_log) )
    if db_log == None:
        db_log = db.save_log(log)
        db_log = db.get_log(log['LogFileName'])
    else:
        # get marker from database if it was already saved (new gambeta)
        rds_config['marker'] = db_log['last_marker'] if db_log.get('last_marker') != None else '0'

    # Check if database file size corresponds to local file already existing (gambeta)
    database_file_size = 0 if db_log.get('file_size') == None else db_log['file_size']
    feedback.debug( 'Size of file existing on database: {}'.format(database_file_size) )
    if database_file_size < local_file_size:
        rds_config['marker'] = '0' # truncate local file and restart downloading it

    # Start single log download
    last_marker = rds_log.download_full_file(rds_client, working_file_name, rds_config)

    # Saves last marker into database
    feedback.output( 'Updating last marker into database' )
    feedback.debug( 'New file size on disk: {}'.format(os.stat(local_file_name).st_size) )
    db.update_log( log, last_marker, os.stat(local_file_name).st_size )
    feedback.output( 'Updated.' )
    feedback.output( 'Finished processing file {}'.format(log['LogFileName']) )

    feedback.output( '' )


