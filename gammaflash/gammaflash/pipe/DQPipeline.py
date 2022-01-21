import os
import signal
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime

from rta_dq_pipe.datasource.DataSource import DataSource
from rta_dq_pipe.output.OutputHandler import OutputHandler
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig


class DQPipeline(ABC):
       
    def __init__(self, dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId):
        self.dqPipeId = dqPipeId
        self.dataSource = dataSource
        self.dqChainId = dqChainId
        self.outputHandler = outputHandler
        self.signal = signal.signal(signal.SIGTERM, self.signal_handler)
        self.interrupted = False
        self.countProcessed = 0
        self.obsId = obsId
        self.runId = runId
        self.logger = PipeLoggerConfig().getLogger(__name__)

    # Definition of the signal handler. All it does is flip the 'interrupted' variable
    def signal_handler(self, signum, frame):

        self.logger.info(f'SIGTERM signal received! pid={os.getpid()} frame={frame}')

        if signum != 15:
            self.logger.info(f"[DQPipeline] Signal {signum} is not supported! frame={frame}")
            return

        self.dataSource.stopWatch()
        self.interrupted = True

    def readIdsFromFilepath(self, filename):
        
        obsId = None
        runId = None

        tmp_filepath = str(Path(filename).name)

        obsIdFound = "obsId" in tmp_filepath
        runIdFound = "runId" in tmp_filepath

        split = tmp_filepath.split("_")

        if obsIdFound and runIdFound:
            obsId = split[1]
            runId = split[3]

        elif not obsIdFound and runIdFound:
            runId = split[1]

        elif obsIdFound and not runIdFound:
            obsId = split[1] 

        return obsId, runId

    def readRunIdFromFilepathGF(self, filename):
        runId = None
        tmp_filepath = str(Path(filename).name)
        runIdFound = "runId" in tmp_filepath
        split = tmp_filepath.split("_")

        if runIdFound:
            runId = split[2]
        
        return runId


    def updateIds(self, obsId, runId):
        self.runId = runId
        self.obsId = obsId
        self.outputHandler.update(obsId=obsId, runId=runId)

    def setRunId(self, runId):
        self.runId = runId
        self.outputHandler.update(runId=runId)

    def getRunId(self):
        return self.runId
    
    def getObsId(self):
        return self.obsId

    
    def logbenchmarking(self, benchmarkfile, start, read_time, timeproc, end, filepath, queuedFiles=""):
        benchmarkfile.write(f"{self.dqPipeId} {start} {read_time} {timeproc} {end} {datetime.fromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%S.%f')} {datetime.fromtimestamp(read_time).strftime('%Y-%m-%dT%H:%M:%S.%f')} {datetime.fromtimestamp(timeproc).strftime('%Y-%m-%dT%H:%M:%S.%f')} {datetime.fromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%S.%f')} {filepath} {queuedFiles}\n")
        benchmarkfile.flush()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

