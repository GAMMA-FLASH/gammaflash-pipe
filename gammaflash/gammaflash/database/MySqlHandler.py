import numpy as np
import pymysql.cursors
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig
from rta_dq_pipe.datasource.database.DatabaseHandler import DatabaseHandler

class MySqlHandler(DatabaseHandler):

    def __init__(self, conf):
        
        self.logger = PipeLoggerConfig().getLogger(__name__)
        self.conn = pymysql.connect(host=conf["hostname"], user=conf["username"], \
        password=conf["password"], port=int(conf["port"]), \
        cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.conn.cursor()
        self.logger.info(f"mysql connection started")
        

    
    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
            self.logger.info(f"mysql connection closed")
        except:
            pass

    def write(self, query):
        self.cursor.execute(query)
        self.conn.commit()


    def read(self, query):
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        results = np.asarray(results)

        return results


    def convertToNumpyArray(self):
        raise NotImplementedError("PLEASE implement me!!")

    
