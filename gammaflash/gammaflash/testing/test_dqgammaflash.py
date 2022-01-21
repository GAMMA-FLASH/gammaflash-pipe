import os
import pytest
import pickle
import subprocess
from time import sleep 
from os import listdir
from pathlib import Path
from astropy.table import Table
from os.path import abspath, join
from multiprocessing import Pipe
from multiprocessing import Process
from rta_dq_pipe.utils.XmlReader import XmlReader
from rta_dq_pipe.pipe.DQAnalysis import DQAnalysis
from rta_dq_pipe.testing.TestUtils import TestUtils
from rta_dq_pipe.pipe.DQPipeBuilder import DQPipeBuilder

class TestDqGammaFlash:

    @staticmethod
    def buildAndStart(pipeID, confFilePath):
        print(f"BuildAndStart pid={os.getpid()}")
        dqPipeline = DQPipeBuilder.buildDQPipeline(confFilePath, pipeID, 1, 2)
        dqPipeline.start()


    @pytest.mark.conf_file_for_test("test_dqpipebuilder/test_dqpipebuilder_dq_gammaflash_gfbin_in_pickle_out_single_dir.xml")
    @pytest.mark.dqlib_confdir("dqlib_conf")
    @pytest.mark.test_data_file_path_type("gfh5")
    def test_processing_gfbin_single_dir(self, export_DQLIBCONF, confFilePath, testDataFilePath):

        xmlReader = XmlReader(confFilePath)

        pipelines = xmlReader.getPipelines()
        print(pipelines)

        pipeline = pipelines.popitem()[1]
        output_dir = pipeline["output_data"]["output_loc"]

        dataDir = pipeline["input_data"]["input_dirs"]

        TestUtils.cleanDir(output_dir)

        print(testDataFilePath)

        N_FILES = 4
        obsId1 = 0
        runId1 = 0
        sleepTime1 = 5

        # this thread simulates the data arrival
        _ = TestUtils.startThread(target=TestUtils.copy_test_data_file, args=(testDataFilePath, dataDir, N_FILES, obsId1, runId1, sleepTime1))

        
        COUNT_FILES = (N_FILES * 1)
        parent_conn, child_conn = Pipe()
        t2 = TestUtils.startThread(target=TestUtils.monitorFileOverwritingAndSendSignal, args=(output_dir, os.getpid(), COUNT_FILES, child_conn))

        dqPipeline = DQPipeBuilder.buildDQPipeline(confFilePath, "reco_gammaflash_scipy", obsId1, runId1)

        dqPipeline.start()

        t2.join()

        #asserts


    @pytest.mark.conf_file_for_test("test_full_pipeline/test_fullpipeline_gf_hdf5_in_hdf5_out.xml")
    @pytest.mark.dqlib_confdir("dqlib_conf_gf")
    @pytest.mark.test_data_file_path_type("gfh5")
    def test_processing_gfbin_full_pipeline(self, export_DQLIBCONF, confFilePath, testDataFilePath):

        xmlReader = XmlReader(confFilePath)

        pipelines = xmlReader.getPipelines()
        processes = []
        inputSimulatorThreads = []
        n_analysis_pipe = 0
        print(pipelines)

        N_FILES = 4
        obsId1 = 0
        runId1 = 0
        sleepTime1 = 5

        for pipeID, pipeConf in pipelines.items():

           TestUtils.cleanDir(pipeConf["output_data"]["output_loc"])

           p = Process(target=TestDqGammaFlash.buildAndStart, args=(pipeID, confFilePath))

           if pipeConf["type"] == "reco_gammaflash":
                t = Process(target=TestUtils.copy_test_data_file, args=(testDataFilePath, pipeConf["input_data"]["input_dirs"], N_FILES))
                inputSimulatorThreads.append(t)
                n_analysis_pipe += 1

           processes.append(p)

        for p in processes:
            p.start()

        for p in inputSimulatorThreads:
            p.start()

        for p in processes:
            p.join()
            assert p.is_alive() == False

        print(testDataFilePath)

        """
        COUNT_FILES = (N_FILES * 1)
        parent_conn, child_conn = Pipe()
        t2 = TestUtils.startThread(target=TestUtils.monitorFileOverwritingAndSendSignal, args=(output_dir, os.getpid(), COUNT_FILES, child_conn))

        dqPipeline = DQPipeBuilder.buildDQPipeline(confFilePath, "reco_gammaflash_scipy", obsId1, runId1)



        dqPipeline.start()

        t2.join()
        """
    @pytest.mark.conf_file_for_test("test_full_pipeline/test_fullpipeline_gf_hdf5_in_mysql_out.xml")
    @pytest.mark.dqlib_confdir("dqlib_conf_gf")
    @pytest.mark.test_data_file_path_type("gfh5")
    def test_processing_gfbin_mysql_full_pipeline(self, export_DQLIBCONF, confFilePath, testDataFilePath):

        xmlReader = XmlReader(confFilePath)

        pipelines = xmlReader.getPipelines()
        processes = []
        inputSimulatorThreads = []
        n_analysis_pipe = 0
        print(pipelines)

        N_FILES = 4
        obsId1 = 0
        runId1 = 0
        sleepTime1 = 5

        for pipeID, pipeConf in pipelines.items():

            if pipeConf["output_data"]["type"] != "mysql":

                TestUtils.cleanDir(pipeConf["output_data"]["output_loc"])

            p = Process(target=TestDqGammaFlash.buildAndStart, args=(pipeID, confFilePath))

            if pipeConf["type"] == "reco_gammaflash":
                t = Process(target=TestUtils.copy_test_data_file, args=(testDataFilePath, pipeConf["input_data"]["input_dirs"], N_FILES))
                inputSimulatorThreads.append(t)
                n_analysis_pipe += 1

            processes.append(p)

        for p in processes:
            p.start()

        for p in inputSimulatorThreads:
            p.start()

        for p in processes:
            p.join()
            assert p.is_alive() == False

        print(testDataFilePath)