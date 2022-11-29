import random

import h5py
import tables
import numpy as np
from tables import IsDescription, StringCol, Int64Col, UInt16Col, Int32Col, Float32Col, Float64Col, UInt8Col, open_file

import zerosuppression as zs

FILENAME = r"C:\Users\Ismam\Desktop\test\2022-07-25.h5"
DETECTOR = "rpg0"
DIRECTORY = r"C:\Users\Ismam\Desktop\test"
THRESHOLD = 20
TFILE = r"C:\Users\Ismam\Desktop\test\weather_station_temp.txt"

zs.CONVERT(FILENAME, DETECTOR, DIRECTORY, THRESHOLD, TFILE)

r"""h5file = open_file(r"C:\Users\Ismam\Desktop\test\test_structure.h5", mode="w", title="Test file")
group = h5file.create_group("/", 'waveform', 'Detector information')

atom = tables.Int16Atom()
shape = (16384, 1)
filters = tables.Filters(complevel=5, complib='zlib')

for i in range(10):
    arraysy = h5file.create_carray(group, f"wf_{str(i).zfill(6)}", atom, shape, f"wf_{i}", filters=filters)
    arraysy._v_attrs.VERSION = "2.0"
    arraysy._v_attrs.start = 1.3123
    arraysy._v_attrs.end = 1.9341

h5file.close()"""



