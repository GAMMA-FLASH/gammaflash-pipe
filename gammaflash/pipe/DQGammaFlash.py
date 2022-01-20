import numpy as np
from time import time
from scipy.signal import find_peaks
from lmfit.models import PolynomialModel
from rta_dq_pipe.pipe.DQPipeline import DQPipeline

class DQGammaFlash(DQPipeline):
    
    def __init__(self, dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId):
        super().__init__(dqPipeId, dataSource, dqChainId, outputHandler, obsId, runId)
        self.results = []
        self.algorithm = dqPipeId

    def opt_fit(self, data):
        left = 0.997
        right = 1.003
        x = data[0]
        y = data[1]

        xmax = x[np.argmax(y)]

    
        xstart = np.where(x >= xmax*left)[0][0]
        xstop  = np.where(x >= xmax*right)[0][0]
        yr = y[xstart:xstop]
        xr = x[xstart:xstop]

        mod = PolynomialModel(degree=3)
    
        params = mod.guess(yr, x=xr)

        out = mod.fit(yr, params, x=xr)
    
        xfine = np.arange(xr[0],xr[-1],0.001)
        yfine = mod.eval(x=xfine, params=params) 
        yfine2 = mod.eval(x=xfine, params=out.params)
        yfinemax = np.max(yfine)

        return yfinemax

    def start(self):
        self.dataSource.startWatch()

        file_gen = self.dataSource.waitForFile()

        for filePath in file_gen:

            if filePath is not None:    
                
                start = time()

                self.logger.debug(f"New file extracted from the queue: {filePath}. Queue lenght: {self.dataSource.files.qsize()}")

                runId = self.readRunIdFromFilepathGF(filePath)

                self.setRunId(runId=runId)

                #try:
                f = self.dataSource.readDataFromFile(filePath)
                group = f[0]
                t = f[1]
                #except:
                #    self.logger.warning(f"Error cannot read {filePath}")
                #    continue
                
                for data in group:
                    """
                    We have n waveform to process, shape for each waveform is (16384, 2)
                    column 0 is x and column 1 is y
                    """
                    #for name in data._v_attrs._f_list("user"):
                    #    self.logger.debug(f"name: {name}, value: {data._v_attrs[name]}")
                    
                    if self.algorithm == "reco_gammaflash_max":
                        index = np.argmax(data[:,1])
                        self.results.append([data[:,0][index], data[:,1][index]])
                        
                    
                    elif self.algorithm == "reco_gammaflash_scipy":
                        peaks, results_scipy = find_peaks(data[:,1], height=40, distance=150)
                        values = data[peaks, 1]
                        temp_res = np.dstack(([peaks], [values]))[0]
                        self.results.extend(temp_res.tolist())
                    
                    elif self.algorithm == "reco_gammaflash_opt_fit":
                        value = self.opt_fit(data)
                        self.results.append(value)
            
                self.outputHandler.save(self.results)
                t.close()
                self.results = []

                end = time()

                self.countProcessed += 1

                self.dataSource.removeDataFile(filePath)

                self.logger.debug(f"Cumulative number of processed files: {self.countProcessed}, took {end - start} s")

            if self.interrupted:
                self.logger.info(f"Terminating the data processing..")
                file_gen.close()

    def stop(self):
        self.dataSource.stopWatch()
        self.interrupted = True

                


