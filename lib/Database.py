from pymongo import MongoClient

class Database:

    db_config = None
    conn = None
    db = None

    def __init__(self, db_config):
        self.db_config = db_config
        self.connect()

    def connect(self):
        connString = 'mongodb://{}:{}'.format(self.db_config['host'], self.db_config['port'])
        self.conn = MongoClient(connString)
        self.db = self.conn[self.db_config['database']]


    def save_log( self, log_file ):
        result = self.db.logs.insert_one(log_file)
        return result.inserted_id


    def get_log( self, log_file_name ):
        log = self.db.logs.find_one({"LogFileName": log_file_name})

        return log


    def update_log(self, rds_log, last_marker, last_size ):
        log = self.db.logs.update_one({'LogFileName': rds_log['LogFileName']},
                                      {
                                          '$set': {
                                              'last_marker': last_marker,
                                              'Size': rds_log['Size'],
                                              'file_size': last_size
                                          }
                                       }, upsert=False)
        return log



