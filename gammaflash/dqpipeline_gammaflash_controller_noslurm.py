import signal
import argparse
import os,sys,json,datetime,time
from multiprocessing import Process
from defusedxml.ElementTree import parse
from rta_dq_pipe.utils.XmlReader import XmlReader
from rta_dq_pipe.pipe.DQPipeBuilder import DQPipeBuilder


class DQPipeController:

    @staticmethod
    def buildAndStart(pipeID, confFilePath, obsid, runid):
        print(f"BuildAndStart pid={os.getpid()}")
        dqPipeline = DQPipeBuilder.buildDQPipeline(confFilePath, pipeID, obsid, runid)
        dqPipeline.start()


    def start(self, xmlFile, obsid, runid):

        pids = []

        print("[DQPipeController] start")

        processes = []

        xmlReader = XmlReader(xmlFile)

        pipelines = xmlReader.readPipelines()

       
        for pipeline in pipelines:

            pipeID = pipelines[pipeline]['id']

            p = Process(target=DQPipeController.buildAndStart, args=(pipeID, xmlFile, obsid, runid))

            processes.append(p)

        for p in processes:
            p.start()
            pids.append(p.pid)

        with open("pids.txt", "w") as f:
            f.write(str(pids))

        for p in processes:
            p.join()

    def update(self,command_file,obsid,runid):

        print("TBI")
         

    def stop(self):

        with open("pids.txt", "r") as f:
            pids = f.read()
            listpids = list(pids.strip('][').split(', '))

        for p in listpids:
            os.kill(int(p), signal.SIGTERM)


if __name__ == "__main__":
    """
        python dqpipeline_controller.py --mode start --xmlfile /data01/homes/cta/DQ-containers/tmp_download/rta-dq/rta-dq/rta-dq-pipe/rta_dq_pipe/testing/test_conf/test_benchmark/test_benchmark_4lines_1thread.xml --obsid 1 --runid 2 --jobfile 4line_1thread.ll
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, help='The command to start, stop or update the slurm job', choices=["start", "update", "stop"], required=True)
    parser.add_argument('--xmlfile', type=str, help='The location of the xml input file', required=True)
    parser.add_argument('--obsid', type=str, help='The observation ID', required=True)
    parser.add_argument('--runid', type=str, help='The run ID', required=True)
    args = parser.parse_args()
 
    dqPipeController = DQPipeController()

    if(args.mode=="start"):

        dqPipeController.start(args.xmlfile, args.obsid, args.runid)


    if(args.mode=="update"):

        dqPipeController.update(args.obsid, args.runid)

    if (args.mode == "stop"):
        dqPipeController.stop()
