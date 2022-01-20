import tables
import numpy as np
from tables import *
from time import time
import matplotlib.pyplot as plt
from tables.description import Float32Col
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig
from rta_dq_pipe.datasource.filesystem.FileHandler import FileHandler

class GFTable(IsDescription):
    x = Float32Col()
    y = Float32Col()

class GfHandler(FileHandler):
    """
    This class opens HDF5 file DL1(waveforms) and writes DL2(eventlist)
    """

    def __init__(self, readingString=""):
        self.readingString = readingString
        self.logger = PipeLoggerConfig().getLogger(__name__)

    def read(self, filename):

        start = time()

        t = tables.open_file(filename)

        data = t.get_node(self.readingString)

        self.logger.debug(f"Reading the HDF5 file {(filename)} took {round(time()-start, 5)} sec")

        return [data, t]

    
    def write(self, filename, data):

        start = time()
        
        h5file = tables.open_file(filename, "w", title="dl2")

        group = h5file.create_group("/", 'dl2', 'dl2 eventlist')
        """
        atom = tables.Float32Atom()

        shape = np.shape(data)

        filters = tables.Filters(complevel=5, complib='zlib')

        events = h5file.create_carray(group, f'eventlist', atom, shape, f"{filename}", filters=filters)
        events[:] = data[:]
        """

        table = h5file.create_table(group, 'eventlist', GFTable, "eventlist")
        gfData = table.row

        for i in range(len(data)):
            gfData["x"] = data[i][0]
            gfData["y"] = data[i][1]
            gfData.append()



        table.flush()

        h5file.close()

        fileOk = f"{filename}.ok"

        with open(fileOk, "w") as fok:
            fok.write("")

        self.logger.debug(f" Wrote {filename} and '.ok' file. Took {round(time()-start,5)} sec")

    def convertToNumpyArray(self, data):
        
        raise NotImplementedError("PLEASE implement me!!")

"""
if __name__ == "__main__":

    gfHandler = GfHandler()

    data = gfHandler.read("/data01/rt/rta-dq/rta-dq-pipe/rta_dq_pipe/testing/unit_tests/test_data/gamma_flash_waveform.bin")
    print(data)

"""

