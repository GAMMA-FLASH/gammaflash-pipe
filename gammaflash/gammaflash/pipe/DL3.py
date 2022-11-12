from time import time
from datetime import datetime, timezone
from pathlib import Path
import glob
import pandas as pd
import json 
import numpy as np
import matplotlib.pyplot as plt

class DL3():
    
    @staticmethod
    def process_spectrum(filename, id, bins=400000, binsize=200):

        print(filename)
        df = pd.read_hdf(filename, "dl2/eventlist")
        df['tstart'] = pd.to_datetime(df['tstart'], unit="s")
        tstarts = df["tstart"].astype(str).to_list()

        binning = np.arange(binsize,bins+(binsize*2),binsize)

        y_hist, bin = np.histogram(df["integral1"], bins=binning)
        bin = 0.5 * (bin[:-1] + bin[1:])

        result_json = json.dumps({"title" : f"Spectrum_{id}", "xlabel" : "Bins", "ylabel": "Counts", 
            "x": bin.tolist(), "y": y_hist.tolist(),
            "tstart":tstarts[0],
            "tend": tstarts[-1]
            })
        insert_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        query = f"INSERT INTO gammaflash_test.gui_spectra (insert_time, `type`, `data`, tstart, tend) VALUES('{insert_time}', 'spectrum_{id}', '{result_json}', '{tstarts[0]}', '{tstarts[-1]}');"

        return query

    @staticmethod
    def get_light_curve(filename, id, freq="10S"):
        
        df = pd.read_hdf(filename, "dl2/eventlist")

        df['tstart'] = pd.to_datetime(df['tstart'], unit="s")
        tstarts = df["tstart"].astype(str).to_list()
        df_grouped = df.groupby(pd.Grouper(key = 'tstart', freq=freq))["tstart"].count().reset_index(name='counts')
        df_grouped["y_err"] = df_grouped["counts"]**(1/2)
        

        result_json = json.dumps({"title" : f"Light_curve_{id}", "xlabel" : "Time (UTC)", "ylabel": "Counts", "mode": "bar", 
            "x": df_grouped["tstart"].astype(str).to_list(),
            "y": df_grouped["counts"].tolist(),
            "y_err": df_grouped["y_err"].tolist(),
            "tstart":tstarts[0],
            "tend": tstarts[-1]
            })

        insert_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        query = f"INSERT INTO gammaflash_test.gui_lc (insert_time, `type`, `data`, tstart, tend) VALUES('{insert_time}', 'lc_{id}', '{result_json}', '{tstarts[0]}', '{tstarts[-1]}');"
        
        return query


if __name__ == "__main__":

    directory = "/data/archive/test_dqpipe_output/DL/DL2/rpg1/*.h5"

    for file in glob.glob(directory):


        start = time()
        
        spectrum_data = DL3.process_spectrum(file, "rpg1")
        lc_data = DL3.get_light_curve(file, "rpg1")
        print(spectrum_data)
        print(lc_data)
        time_proc = time()

        print(f"File processing took: {round(time_proc-start,5)}")
        