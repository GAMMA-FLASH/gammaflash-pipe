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
    def process_spectrum(filename, id, bins=10000, binsize=10):
        df = pd.read_csv(filename, sep="\t")
        df['tstart'] = pd.to_datetime(df['tstart'], unit="s")
        tstarts = df["tstart"].astype(str).to_list()

        binning = np.arange(0,bins+binsize,binsize)

        y_hist, bin = np.histogram(df["integral1"], bins=binning)

        result_json = json.dumps({"title" : "titolo", "xlabel" : "xlabel", "ylabel": "ylabel", 
            "x": bin.tolist(), "y": y_hist.tolist(),
            "tstart":tstarts[0],
            "tend": tstarts[-1]
            })
        insert_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        query = f"INSERT INTO gammaflash_test.gui_spectra (insert_time, `type`, `data`, tstart, tend) VALUES('{insert_time}', 'spectrum_{id}', '{result_json}', '{tstarts[0]}', '{tstarts[-1]}');"

        return query

    @staticmethod
    def get_light_curve(filename, id, freq="10S"):
        
        df = pd.read_csv(filename, sep="\t")

        df['tstart'] = pd.to_datetime(df['tstart'], unit="s")
        tstarts = df["tstart"].astype(str).to_list()
        df_grouped = df.groupby(pd.Grouper(key = 'tstart', freq=freq))["tstart"].count().reset_index(name='counts')
        df_grouped["y_err"] = df_grouped["counts"]**(1/2)
        

        result_json = json.dumps({"title" : "titolo", "xlabel" : "xlabel", "ylabel": "ylabel", "mode": "bar", 
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

    directory = "/home/antonio/Desktop/DL2/*.txt"

    y_hist = np.zeros(1000)

    for file in glob.glob(directory):
        spectrum_data = DL3.process_spectrum(file)
        lc_data = DL3.get_light_curve(file)
        print(spectrum_data)
        print(lc_data)
        exit()