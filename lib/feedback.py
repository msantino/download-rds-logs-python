debug_enabled = False

def output( msg ):
    print msg

def debug( msg ):
    if debug_enabled:
        output( msg )

def start( rds_config ):
    output( '= = = = = = = = = = = = = = = = = = = = = = = = = = = = ' )
    output( '= = = = = = = Starting Download RDS Script  = = = = = = ' )
    output( '= = = = = = = = = = = = = = = = = = = = = = = = = = = = ' )
    output( 'Instance Identifier: {}'.format(rds_config['rds_instance_identifier']))
    output( 'Download logs to: {}'.format(rds_config['rds_logs_path']))
    output( '' )