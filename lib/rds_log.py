import time
import feedback
import os
import errno
from botocore.exceptions import ClientError
from datetime import datetime

def list_available_log_files(rds_client, instance_identifier):
    """ Returns a list of available logfiles for a given instance    
    :param rds_client: 
    :param instance_identifier: 
    :return: 
    """
    feedback.output( 'Looking for available instance logs...' )
    list = rds_client.describe_db_log_files( DBInstanceIdentifier=instance_identifier )['DescribeDBLogFiles']
    feedback.output( 'Total found: {}'.format( len(list) ))
    feedback.output( '' )
    return list


def download_full_file(rds_client, file_name, rds_config):
    """ Iterates RDS marker and downloads a given log file full writing to disk
    :param rds_client: 
    :param file_name: 
    :param rds_config: 
    :return: marker
    """
    feedback.debug('Marker download 1: {}'.format(rds_config['marker']))
    additional_data_pending = True
    #marker = rds_config['marker'] # Initial marker
    full_file_name = get_full_file_name(rds_config['rds_logs_path'], rds_config['rds_instance_identifier'], file_name )

    feedback.output( 'Downloading file to {}'.format( full_file_name ) )

    if rds_config['marker'] == '0':
        file = open(full_file_name, 'w') # erases existing file since marker is at begining ('0')
    else:
        file = open(full_file_name, 'a')

    # Download file portion
    while additional_data_pending:
        try:
            response = rds_client.download_db_log_file_portion(
                DBInstanceIdentifier=rds_config['rds_instance_identifier'],
                LogFileName='error/' + file_name,
                Marker=rds_config['marker'],
                NumberOfLines=rds_config['rds_number_of_lines']
            )
            feedback.debug( 'Response.Marker: [{}]'.format(response['Marker']) )
            feedback.debug( 'Response.AdditionalDataPending: [{}]'.format(response['AdditionalDataPending']) )
            rds_config['marker'] = response['Marker']
            additional_data_pending = response['AdditionalDataPending']

            feedback.debug('Marker download 2: {}'.format(rds_config['marker']))
            # Debug
            #feedback.output( 'Marker: {}'.format(rds_config['marker']) )

            # Writes data into local logfile
            file.write(response['LogFileData'])

        except ClientError as e:
            feedback.output( 'ClientError: {}'.format( e ) )

            # If error is about Rate Exceeded, wait a while and continue
            if e.response['Error']['Code'] == 'Throttling' and e.response['Error']['Message'] == 'Rate exceeded':
                feedback.output( 'Waiting and continuing...' )
                time.sleep(3)
                continue

            else:
                feedback.output( 'Response: {}'.format( e.response ) )
                raise
        except Exception as e:
            feedback.output( 'Generic error: {}'.format(e) )
            raise

    file.close()
    feedback.debug('Marker download 3: {}'.format(rds_config['marker']))
    return rds_config['marker']


def get_full_file_name(path, instance_identifier, file_name):
    """ Build full file path creating directories if doesnt exists
    :param path: 
    :param instance_identifier: 
    :param file_name: 
    :return: Full File Name
    """
    full_path = path + '/' + instance_identifier
    try:
        os.makedirs(full_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    return full_path + '/' + file_name + '.log'


def get_date_from_log_name( log_name ):
    date_array = log_name.split('/')[1].split('.')[-1].split('-')
    date_array.pop()
    date_str = '-'.join(date_array)
    return datetime.strptime(date_str, '%Y-%m-%d')
