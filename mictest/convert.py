#!/usr/bin/env python
# A couple of scripts to set the environent and import data from a .tau set of results
from utilities import *
from metrics import *
import numbers, copy, shelve
from multiprocessing import Process

datasets = {
	'talapas_scaling' : ["manual_scaling_TTbar70_talapas_fullnode",
			     "manual_scaling_Large_talapas",
			     "ev_thr_scaling_Large_talapas"],
	'cori_scaling': ["manual_scaling_TTbar35",
			"manual_scaling_TTbar70",
			"manual_scaling_Large",
			"mixed_thr_scaling_Large"]
}

def processDataset(application,experiment):
	path = ".tau/" + application + "/" + experiment + "/"
	# note that this function takes a long time to run, so only rerun if you must
	metric_data = get_pandas_scaling(path, callpaths=True)


	if application == "talapas_scaling":
    		metric_data = remove_erroneous_threads(metric_data,  [1, 8, 16, 32, 48, 56])
	elif application == "cori_scaling":
    		metric_data = remove_erroneous_threads(metric_data,  [1, 4, 8, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 256])

	
	key=application + ":" + experiment 
	d = shelve.open(key+'.shelve')
	d[key] = metric_data
	d.close()

if __name__ == '__main__':
 allprocesses = []
 for application,experiments in datasets.items():
    for experiment in experiments:
      print(application,experiment)
      allprocesses.append(Process(target=processDataset, args=(application,experiment)))

for p in allprocesses:
  p.start()

for p in allprocesses:
  p.join()
