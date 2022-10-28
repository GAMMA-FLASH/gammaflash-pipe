from time import time
import gammaflash.pipe.zerosuppression as zerosuppression
from gammaflash.pipe.DQPipeline import DQPipeline


class GammaflashDL1(DQPipeline):
    """
    This class is a wrapper on the zerosuppression tool developed by G. Levi
    """

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
                self.logger.debug(f"Launching DL1 zerosuppression tool")

                threshold = 20
                if self.rpId == "rpg2":
                    threshold = 5

                outfile = zerosuppression.CONVERT(filePath, self.rpId, str(self.outputHandler.outputLoc), Threshold=threshold, TFile="/data/gammaflash_repos/gammaflash-gui-dash/gui/weather_station/weather_station_temp.txt")
                _ = open(f"{outfile}.ok", "w")
    
    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True