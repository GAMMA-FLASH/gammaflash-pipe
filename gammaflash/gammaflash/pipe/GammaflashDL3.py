import json 
import glob
import numpy as np
import pandas as pd
from time import time
from pathlib import Path
import matplotlib.pyplot as plt
from gammaflash.pipe.DL3 import DL3
from datetime import datetime, timezone
from gammaflash.pipe.DQPipeline import DQPipeline


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

                

                #cleaning filename for testing
                filepath_pathlib = Path(filePath)
                filename_replace_ext = filepath_pathlib.with_suffix('.txt')

                self.logger.debug(f"New file extracted from the queue: {filename_replace_ext}. Queue lenght: {self.dataSource.files.qsize()}")
                self.logger.debug(f"Launching DL3 processing tool")



                query_sp = DL3.process_spectrum(filename_replace_ext, id=self.rpId)
                self.outputHandler.mysqlHandler.write(query_sp)


                query_lc = DL3.get_light_curve(filename_replace_ext, id=self.rpId)
                self.outputHandler.mysqlHandler.write(query_lc)

    
    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True