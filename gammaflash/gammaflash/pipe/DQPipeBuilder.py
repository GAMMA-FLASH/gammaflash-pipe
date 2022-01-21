import os
import logging
from pathlib import Path
from gammaflash.output.OutputToHdf5 import OutputToHdf5
from rta_dq_pipe.utils.XmlReader import XmlReader
from rta_dq_lib.api.DQLib import DQLib
from rta_dq_pipe.pipe.DQAnalysisAcada import DQAnalysisAcada
from rta_dq_pipe.pipe.DQAggregator import DQAggregator
from rta_dq_pipe.datasource.database.MySqlHandler import MySqlHandler
from rta_dq_pipe.datasource.database.RedisHandler import RedisHandler
from rta_dq_pipe.datasource.filesystem.FileSystemDS import FileSystemDS
from rta_dq_pipe.datasource.filesystem.FitsHandler import FitsHandler
from rta_dq_pipe.datasource.filesystem.Hdf5HandlerAcada import Hdf5HandlerAcada
from rta_dq_pipe.datasource.filesystem.PickleHandler import PickleHandler

from rta_dq_pipe.output.OutputToMySql import OutputToMySql
from rta_dq_pipe.output.OutputToPickle import OutputToPickle
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig

from gammaflash.datasource.filesystem.Hdf5HandlerGammaflash import Hdf5HandlerGammaflash
from gammaflash.pipe.DQGammaFlash import DQGammaFlash
from gammaflash.datasource.filesystem.GfHandler import GfHandler

class DQPipeBuilder:

    @staticmethod
    def configLogging(loggingConfig):
        
        logLevel = getattr(logging, loggingConfig["level"])
        logOutDir = loggingConfig["dir"]

        loggerConfig = PipeLoggerConfig()
        loggerConfig.setLogger(logOutDir, logLevel)
        logger = loggerConfig.getLogger(__name__)
        
        logger.info(f'Print from logger pid={os.getpid()}')


    @staticmethod
    def createDirectories(pipelineConf):
        dirs = pipelineConf["input_data"]["input_dirs"].split(":")
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        dirs = pipelineConf["output_data"]["output_loc"].split(":")
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)


    @staticmethod
    def buildDQPipeline(confFilePath, pipelineId, obsId, runId):

        xmlReader = XmlReader(confFilePath)
        
        DQPipeBuilder.configLogging(xmlReader.getLoggingConfig())

        logger = logging.getLogger(__name__)
        logger.info(f'Building new pipeline {pipelineId}')

        pipelineConf = xmlReader.getPipeline(pipelineId)

        DQPipeBuilder.createDirectories(pipelineConf)

        if pipelineConf["input_data"]["type"] == "h5":
            handler = Hdf5HandlerAcada(
                pipelineConf["input_data"]["reading_string"], joinReadingString=pipelineConf["input_data"]["join_with"], joinKeys=pipelineConf["input_data"]["join_keys"])
            
        elif pipelineConf["input_data"]["type"] == "pickle":
            handler = PickleHandler()
        
        elif pipelineConf["input_data"]["type"] == "fits":
            handler = FitsHandler()

        elif pipelineConf["input_data"]["type"] == "gfh5":
            handler = GfHandler(pipelineConf["input_data"]["reading_string"])

        if pipelineConf["input_data"]["type"] in ["h5", "pickle", "fits", "gfh5"]:
            dataSource = FileSystemDS(
                handler,  pipelineConf["input_data"]["input_dirs"])
        
        elif pipelineConf["input_data"]["type"] == "mysql": 
            conf = xmlReader.getDBCredentials("mysql")
            dataSource = MySqlHandler(conf)
        
        elif pipelineConf["input_data"]["type"] == "redis":
            conf = xmlReader.getDBCredentials("redis")
            dataSource = RedisHandler(conf)
    
        if pipelineConf["output_data"]["type"] == "pickle":
            output = OutputToPickle(pipelineConf["output_data"]["output_loc"], pipelineConf["output_data"]["overwrite"], obsId, runId, pipelineConf["output_data"]["suffix"])

        elif pipelineConf["output_data"]["type"] == "mysql":
            conf = xmlReader.getDBCredentials("mysql")
            output = OutputToMySql(pipelineConf["output_data"]["output_loc"], obsId, runId, conf)
        
        elif pipelineConf["output_data"]["type"] == "gfh5":
            output = OutputToHdf5(pipelineConf["output_data"]["output_loc"], pipelineConf["output_data"]["overwrite"], obsId, runId, pipelineConf["output_data"]["suffix"])


        if pipelineConf["type"] == "dq_analysis":
            return DQAnalysisAcada(pipelineConf["id"], dataSource, pipelineConf["dqchain_id"], pipelineConf["nthreads"], output, obsId, runId, pipelineConf["input_data"]["filter_column"], pipelineConf["input_data"]["filter_value"])
        
        elif pipelineConf["type"] == "dq_aggregator":
            return DQAggregator(pipelineConf["id"], dataSource, pipelineConf["dqchain_id"], output, obsId, runId)

        elif pipelineConf["type"] == "reco_gammaflash":
            return DQGammaFlash(pipelineConf["id"], dataSource, pipelineConf["dqchain_id"], output, obsId, runId)

"""if __name__=="__main__":
    import os 
    os.environ["DQLIBCONF"] = "/home/antonio/Desktop/repos/rta-dq/rta-dq-pipe/rta_dq_pipe/testing/test_conf/test_dqpipeline/dqlib_conf"
    dqpipe = DQPipeBuilder.buildDQPipeline("/home/antonio/Desktop/repos/rta-dq/rta-dq-pipe/rta_dq_pipe/testing/test_conf/test_dqpipebuilder/test_dqpipebuilder_dq_analysis_hdf5_in_pickle_out_single_dir.xml", "line_1_camera")
"""
