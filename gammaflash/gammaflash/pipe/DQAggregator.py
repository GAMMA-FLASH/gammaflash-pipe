from pathlib import Path
from time import time
from datetime import datetime
from rta_dq_lib.api.DQLib import DQLib


from rta_dq_pipe.pipe.DQPipeline import DQPipeline
from rta_dq_pipe.datasource.DataSource import DataSource
from rta_dq_pipe.output.OutputHandler import OutputHandler
from rta_dq_lib.api.DQPipeline import DQPipeline as DQChain
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig

import numpy as np

class AggregationPool:

    def __init__(self, inputDirs):
        """
        mapping:
            "/mnt/StorageLinux/output_loc/line_1/camera" : 0,
            "/mnt/StorageLinux/output_loc/line_2/camera" : 1,
            "/mnt/StorageLinux/output_loc/line_3/camera" : 2,
            "/mnt/StorageLinux/output_loc/line_4/camera" : 3,            
        
        pool:
            np.array([ <data>, <data>, <data>, <data> ])
        """
        self.mapping = { Path(inputDir) : idx for idx, inputDir in enumerate(inputDirs) }
        self.pool = np.empty(shape=(len(inputDirs)), dtype=object) # [ <data> , <data> , <data> , <data> ]
        self.logger = PipeLoggerConfig().getLogger(__name__)

    def getIndex(self, pathObj):
        return self.mapping[pathObj]


    def insert(self, filePath, data):

        fp = Path(filePath)

        apidx = self.getIndex(fp.parent)

        """
        if apidx in self.removedKeys:
            self.logger.warning(f"Key {apidx} has been removed from the aggration pools")
            return
        """

        self.pool[apidx] = data

        self.logger.debug(f"File {fp} inserted in the aggregation pool at index {apidx}")

    def getData(self):

        return self.pool[self.pool != np.array(None)]




class DQAggregator(DQPipeline):
    
    def __init__(self, dqPipeId, dataSource, dqChain, outputHandler, obsId, runId):
        super().__init__(dqPipeId, dataSource, dqChain, outputHandler, obsId, runId)

        self.MAXPOOLS = 3
        index = self.aggregationPoolIndex(obsId, runId)
        self.aggregationPools = {
            index : AggregationPool(self.dataSource.getWatchDirs())
        }
        self.removedKeys = []
        
        self.logger = PipeLoggerConfig().getLogger(__name__)

        logOutputFolder = PipeLoggerConfig().getLogOutDir().joinpath("timestamps")
        logOutputFolder.mkdir(parents=True, exist_ok=True)

        benchmarkLog = logOutputFolder.joinpath(f"benchmark_dqaggregator_{self.dqPipeId}.log")

        self.benchmarkFile = open(str(benchmarkLog), "w")
        header = "pipeid starttime readtime timeproc endtime starttimeUTC readtimeUTC timeprocUTC endtimeUTC filename \n"
        self.benchmarkFile.write(header)

        self.dqChain = DQChain(self.dqChainId, obsId, debug_lvl=0, compute_pipe_performance=True)


    def __del__(self):
        try:
            self.benchmarkFile.close()
        except:
            pass

    def aggregationPoolIndex(self, obsId, runId):
        """
        Dictionary indexes are obsId_runid
        """
        if obsId is not None and runId is not None:
            return f"obsId_{str(obsId)}_runId_{str(runId)}"
        elif obsId is not None and runId is None:
            return f"obsId_{str(obsId)}"
        elif obsId is None and runId is not None:
            return f"runId_{str(runId)}"
        
    def getAggregationPool(self, obsId, runId):
        index = self.aggregationPoolIndex(obsId, runId)
        
        if index not in self.aggregationPools:
            self.logger.debug(f"New aggregation pool for index: {index}")
            self.aggregationPools[index] = AggregationPool(self.dataSource.getWatchDirs())

        return self.aggregationPools[index]

    def aggregate(self):

        dataToAggregate = self.getAggregationPool(self.obsId, self.runId).getData()

        nFiles = len(dataToAggregate)
        if nFiles == 0:
            self.logger.warning("The aggregation pool is empty")
            return None

        self.logger.debug(f"Aggregating {nFiles} files")

        joined = DQLib.join_activity_products(dataToAggregate)

        activity_output = self.dqChain.process(joined, self.getRunId())
        
        return activity_output

    """
    def removeOldKeysFromAggregationPools(self):
        if len(self.aggregationPools) > self.MAXPOOLS:
            key, val = self.aggregationPools.pop()
            self.removedKeys.append(key)
    """

    def start(self):
        
        self.dataSource.startWatch()

        file_gen = self.dataSource.waitForFile()

        for filePath in file_gen:
                        
            # /mnt/StorageLinux/output_loc/line_1/camera/dl1_1.h5
            if filePath is not None:        

                self.logger.debug(f"New file extracted from the queue: {filePath}. Queue lenght: {self.dataSource.files.qsize()}")

                start = time()

                # extracting obsId and runId from the filename
                obsId, runId = self.readIdsFromFilepath(Path(filePath).name)

                if not obsId and not runId:
                    self.logger.critical(f"The filename {filePath} does not contain nor obsId nor runId")
                    raise ValueError(f"The filename {filePath} does not contain nor obsId nor runId")

        
                self.updateIds(obsId, runId)

                self.getAggregationPool(self.obsId, self.runId).insert(filePath, self.dataSource.readDataFromFile(str(filePath)))

                read_time = time()

                dqChainOutput = self.aggregate()

                time_proc = time()
    
                self.outputHandler.save(dqChainOutput)

                end = time()

                self.logbenchmarking(self.benchmarkFile, start, read_time, time_proc, end, filePath)

                self.countProcessed += 1
                
                self.logger.debug(f"Cumulative number of processed files: {self.countProcessed}")
                
                # self.removeOldKeysFromAggregationPools()

            if self.interrupted:
                self.logger.info(f"Terminating the data processing..")
                file_gen.close()
                self.benchmarkFile.close()


    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True
