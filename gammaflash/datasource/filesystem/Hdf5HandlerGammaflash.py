import tables
import numpy as np
from time import time
from os.path import basename
from astropy.table import join

from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig
from rta_dq_pipe.datasource.filesystem.FileHandler import FileHandler


class Hdf5HandlerGammaflash(FileHandler):
    """
    This class is a copy of Hdf5HandlerAcada for opening hdf5 files dl2(eventlist), similar to LST1 hdf5
    """

    def __init__(self, readingString, joinReadingString=None, joinKeys=None):

        # dl1:event:telescope:image:LST_LSTCam => ['dl1', 'event', 'telescope', 'image', 'LST_LSTCam']
        self.logger = PipeLoggerConfig().getLogger(__name__)
        # self.nodes = readingString.split(":")
        self.readingString = readingString
        self.joinReadingString = joinReadingString
        self.joinKeys = None
        self.doJoin = False

        if self.joinReadingString and joinKeys:
            
            if ":" in joinKeys: # e.g. 'event_id':'obs_id'
                self.joinKeys = joinKeys.split(":")
            else:
                self.joinKeys = [joinKeys] # e.g. 'event_id'

            self.doJoin = True
    
        if self.joinReadingString and not joinKeys:
            self.logger.critical(f"The 'joinKeys' attribute is necessary if you want to perform a join.")


    def regularJoin(self, data, join_with):
        return np.array(join(data, join_with, keys=self.joinKeys, metadata_conflicts="silent"))
    
    """
    Append join has been deprecated on 20/09/2021
    def appendJoin(self, data, join_with):
        newFieldsDescr = [descrTuple for descrTuple in join_with.dtype.descr if descrTuple[0] not in data.dtype.names]
        newDT = np.dtype(data.dtype.descr + newFieldsDescr)
        newArray = np.empty(data.shape, dtype=newDT)
        # copy existing data into the new table
        for c in data.dtype.names:
            newArray[c] = data[c]
        for fieldDescr in newFieldsDescr:
            newArray[fieldDescr[0]] = join_with[fieldDescr[0]]
        
        return newArray
    """

    def read(self, fileName):
                
        start = time()
        
        t = tables.open_file(fileName)

        data = t.get_node(self.readingString)[:]
        """
        metadata = {}
        for name in data._v_attrs._f_list("user"):
            #print("name: %s, value: %s" % (name, group._v_attrs[name]))
            metadata[name] = data._v_attrs[name]
        """
        if self.joinReadingString:
            join_with = t.get_node(self.joinReadingString)[:]
            # Perform the join
            data = self.regularJoin(data, join_with)
        
        t.close()

        self.logger.debug(f"Reading the HDF5 file {basename(fileName)} took {round(time()-start, 5)} sec")

        return data

    def write(self, filename, data):
        raise NotImplementedError("PLEASE implement me!!")

    def convertToNumpyArray(self, data):
        return np.array(data)