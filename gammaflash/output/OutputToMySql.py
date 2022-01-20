import pymysql.cursors
import random
import json
from rta_dq_pipe.datasource.database.MySqlHandler import MySqlHandler
from rta_dq_pipe.output.OutputHandler import OutputHandler
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig


class OutputToMySql(OutputHandler):

    def __init__(self, outputLoc, obsId, runId, conf):
        super().__init__(outputLoc, obsId, runId)
        self.mysqlHandler = MySqlHandler(conf)
        self.logger = PipeLoggerConfig().getLogger(__name__)


    
    def save(self, data):

        for d in data.events[0]:
            data.events[0][d] = data.events[0][d].tolist()

        parsed_json = json.dumps(data.events[0])
        

        self.logger.info(f"\n\n\n\n\n\n sono con i dati {json.dumps(data.events[0])} \n\n\n\n\n\n")

        """
        INSERT INTO {self.output}
        (RedpitayaID, Bars)
        VALUES({runId}, {data.events[0]});
        """

        #UPDATE gamma_flash_test.gftable SET Bars='{parsed_json}' WHERE RedpitayaID={runID};
        #query = f"INSERT INTO {self.outputLoc} (RedpitayaID, Bars) VALUES({0}, '{parsed_json}');"
        query = f"UPDATE gammaflash_test.gftable SET Bars='{parsed_json}' WHERE RedpitayaID={self.runId};"
        #print(query)
 
        #self.mysqlHandler

        self.mysqlHandler.write(query)


    
    def update(self, obsId=None, runId=None, dqChainId=None):
        self.obsId = 0 #random.randint(5,1000)
        self.runId = 0 #random.randint(5,1000)
