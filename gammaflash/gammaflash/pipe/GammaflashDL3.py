import json 
import glob
import numpy as np
import pandas as pd
from time import time
from pathlib import Path
import matplotlib.pyplot as plt
from gammaflash.pipe.DL3 import DL3
from datetime import datetime, timezone
#from gammaflash.pipe.eventlist_v4 import Eventlist
#from gammaflash.pipe.DQPipeline import DQPipeline


class GammaflashDL3(DQPipeline):

    def __init__(self, dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId):
        super().__init__(dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId)
        self.results = []
        self.rpId = dqPipeId.split("-")[0]

    
    def start(self):
        self.dataSource.startWatch()

        file_gen = self.dataSource.waitForFile()

        for filePath in file_gen:

            if filePath is not None:    
                
                start = time()

                self.logger.debug(f"New file extracted from the queue: {filePath}. Queue lenght: {self.dataSource.files.qsize()}")
                self.logger.debug(f"Launching DL3 processing tool")

                query_sp = DL3.process_spectrum(filepath)
                outputHandler.mysqlHandler.write(query_sp)


                query_lc = DL3.get_light_curve(filepath)
                outputHandler.mysqlHandler.write(query_lc)

    
    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True