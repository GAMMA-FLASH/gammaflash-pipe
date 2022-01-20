import os
import signal
import numpy as np
from time import time
from datetime import datetime
from functools import partial
from rta_dq_lib.api.DQLib import DQLib
from multiprocessing import Queue, Process
from multiprocessing.managers import BaseManager

from rta_dq_pipe.pipe.DQPipeline import DQPipeline
from rta_dq_pipe.datasource.DataSource import DataSource
from rta_dq_pipe.output.OutputHandler import OutputHandler
from rta_dq_lib.api.DQPipeline import DQPipeline as DQChain
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig

class MyManager(BaseManager): pass
class DQChainOutput:
    def __init__(self):
        self.output = None
    def get(self):
        return self.output
    def set(self, obj):
        self.output = obj

MyManager.register('DQChain', DQChain)
MyManager.register('DQChainOutput', DQChainOutput)



class DQAnalysisAcada(DQPipeline):
    
    def __init__(self, dqPipeId, dataSource, dqChainId, nthreads, outputHandler, obsId, runId, filterColumn, filterValue):
        super().__init__(dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId)
        self.logger = PipeLoggerConfig().getLogger(__name__)
        self.nthreads = nthreads

        self.filterColumn = filterColumn # the column name that is used to filter the events
        self.filterValue = filterValue # the value of the column name to filter the events
    

        # vogliamo poter crearne N 
        # devono essere creati dentro il contesto di un Manager        
        if self.nthreads == 0:
            self.dqChain = DQChain(self.dqChainId, obsId, debug_lvl=0, compute_pipe_performance=True)
            self.logger.info(f"The number of multiprocessing.Process is {self.nthreads}. No multiprocessing will be used.")

        elif self.nthreads > 0:    
            self.manager = MyManager() 
            self.manager.start()
            self.dqChains = [self.manager.DQChain(self.dqChainId, obsId, debug_lvl=0, compute_pipe_performance=True) for i in range(self.nthreads)]
            self.logger.info(f"Multiprocessing has been activated, it will use {self.nthreads} multiprocessing.Process objects")
        else:
            self.logger.critical(f"The number of multiprocessing.Process objects cannot be lower than zero!")


        logOutputFolder = PipeLoggerConfig().getLogOutDir().joinpath("timestamps")
        logOutputFolder.mkdir(parents=True, exist_ok=True)

        benchmarkLog = logOutputFolder.joinpath(f"benchmark_dqanalysis_{self.dqPipeId}.log")

        self.benchmarkFile = open(str(benchmarkLog), "w")
        header = "pipeid starttime readtime timeproc endtime starttimeUTC readtimeUTC timeprocUTC endtimeUTC filename \n"
        self.benchmarkFile.write(header)
        
        self.logger.info(f"A new DQAnalysisAcada object has been created. It will use {nthreads} multiprocess.Process objects.")

    def __del__(self):
        try:
            self.benchmarkFile.close()
        except:
            pass

    def processSingleThread(self, data):
        #f = open(f"processo_{0}_{0}_{2500}.txt", "a")
        activityOutput = self.dqChain.process(data, self.getRunId())
        #f.write(f"{-1}, {-1}, {activityOutput.metadata.pipeline_performance.elapsed_time}\n")
        #f.close()

        return activityOutput

    @staticmethod
    def processWrapper(id, output, data, dqChain):
        #start = datetime.utcnow()
        #f = open(f"processo_{id}_{len(l)}_{2500}.txt", "a")
        activityOutput = dqChain.process(data, run_id=0)
        output.set(activityOutput)
        #l[id] = activityOutput
        #end = datetime.utcnow()
        #f.write(f"{start}, {end}, {activityOutput.metadata.pipeline_performance.elapsed_time}\n")
        #f.close()
   

    def processMultiThreads(self, data):

        toBeJoined = None

        outputs = [self.manager.DQChainOutput() for i in range(self.nthreads)]

        procs = []
        for i in range(self.nthreads):
            p = Process(target=DQAnalysisAcada.processWrapper, args=(i, outputs[i], data[i], self.dqChains[i]))
            procs.append(p)

        for p in procs:
            p.start()

        # self.logger.debug(f"Waiting for processes..")
        TIMEOUT = 10
        start_timer = time()
        for p in procs:
            p.join(timeout=TIMEOUT)
            elapsed = time() - start_timer
            if elapsed >= TIMEOUT:
                self.logger.critical(f"A join timeout has been expired for process {p}!")
                raise TimeoutError(f"A join timeout has been expired for process {p}!")

        toBeJoined = [output.get() for output in outputs]
        self.logger.debug(f"Number of activity products = {len(toBeJoined)}")

        joined = DQLib.join_activity_products(toBeJoined, convertToNumpyStructArray = False)

        return joined

    def start(self):
        
        self.dataSource.startWatch()

        file_gen = self.dataSource.waitForFile()

        for filePath in file_gen:

            if filePath is not None:    
                
                start = time()



                self.logger.debug(f"New file extracted from the queue: {filePath}. Queue lenght: {self.dataSource.files.qsize()}")

                # search for obsid e runid within the filename
                obsId, runId = self.readIdsFromFilepath(filePath)

                self.updateIds(obsId, runId)
                
                dqChainOutput = None

                data = self.dataSource.readDataFromFile(filePath)

                if self.filterColumn:
                    #filtering data as requested by xml configuration
                    mask = data[self.filterColumn] == int(self.filterValue)
                    data = data[mask]

                if self.nthreads > 0:
                    data = np.array_split(data, self.nthreads)

                read_time = time()



                if self.nthreads == 0:
                    dqChainOutput = self.processSingleThread(data) # data is a numpy structured array
                else:
                    dqChainOutput = self.processMultiThreads(data) # data is a List of numpy structured array

                time_proc = time()
                
            
            
                self.logger.debug(f"File processing took: {round(time_proc-start,5)}")

                self.outputHandler.save(dqChainOutput)

                end = time()

            
            
                self.logbenchmarking(self.benchmarkFile, start, read_time, time_proc, end, filePath)

                self.countProcessed += 1

                self.logger.debug(f"Cumulative number of processed files: {self.countProcessed}")

            if self.interrupted:
                self.logger.info(f"Terminating the data processing..")
                file_gen.close()
                self.benchmarkFile.close()


    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True


