from time import time
from pathlib import Path

from gammaflash.pipe.eventlist_v3 import Eventlist
from gammaflash.pipe.DQPipeline import DQPipeline


class GammaflashDL2(DQPipeline):

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
                self.logger.debug(f"Launching DL2 processing tool")

                outputdir = str(self.outputHandler.outputLoc)

                eventlist = Eventlist()

                temperatures_path = Path("/data/gammaflash_repos/gammaflash-gui-dash/gui/weather_station/weather_station_temp.txt")

                if temperatures_path.exists:
                    temperatures = eventlist.process_temps_file(temperatures_path)
                else:
                    temperatures = []

                eventlist.process_file(filePath, temperatures, outputdir)
    
    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True