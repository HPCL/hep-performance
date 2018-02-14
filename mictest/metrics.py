'''
functions to add derived metrics to the dictionaries of metrics

please use the examples to add more
'''


from utilities import *

def add_IPC(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    CYC = 'PAPI_TOT_CYC'
    
    if(not (metrics.has_key(INS) and metrics.has_key(CYC)) ):
        print "ERROR adding IPC to metric dictionary"
        return False
    
    cyc = metrics['PAPI_TOT_CYC'].copy()
    ins = metrics['PAPI_TOT_INS'].copy()
    cyc.index = cyc.index.droplevel()
    ins.index = ins.index.droplevel()    
        
    
    ucyc = cyc.unstack()
    uins = ins.unstack()

    metrics['DERIVED_IPC'] = (uins / ucyc).stack()
        
        
    return True

def add_CPI(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    CYC = 'PAPI_TOT_CYC'
    
    if(not (metrics.has_key(INS) and metrics.has_key(CYC)) ):
        print "ERROR adding CPI to metric dictionary"
        return False
        
    cyc = metrics['PAPI_TOT_CYC'].copy()
    ins = metrics['PAPI_TOT_INS'].copy()
    cyc.index = cyc.index.droplevel()
    ins.index = ins.index.droplevel()    
        
    
    ucyc = cyc.unstack()
    uins = ins.unstack()

    metrics['DERIVED_CPI'] = (ucyc / uins).stack()
        
        
    return True


def add_L1_missrate(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    LST = 'PAPI_LST_INS' # total load store
    L1M = 'PAPI_L1_TCM'  # L1 misses
    
    if(not (metrics.has_key(LST) and metrics.has_key(L1M)) ):
        print "ERROR adding L1 MR to metric dictionary"
        return False
        
    access = metrics[LST].copy()
    misses = metrics[L1M].copy()
    access.index = access.index.droplevel()
    misses.index = misses.index.droplevel()    
        
    
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L1_MISSRATE'] = (umisses / uaccess).stack()
        
        
    return True

def gen_metric(met_list, name):
    func = "def add_" + name + "(metrics):\n"

    for m in range(len(met_list)):

        func += "\tif (not metrics.has_key(" + met_list[m] + ")):\n"
        func += "\t\tprint 'ERROR adding " + name + " to metric dictionary'\n"
        func += "\t\treturn False"

        func += "\ta" + str(m) + " = metrics[" + met_list[m] + "].copy()\n"
        func += "\ta" + str(m) + ".index = a" + str(m) + ".index.droplevel()\n"
        func += "\tu" + str(m) + " = a" + str(m) + ".unstack()\n"
    

    func += "\tmetrics[" + name + "] = " + "\"PLEASE IMPLEMENT THIS PART\"\n\n"
    func += "\treturn True\n\n\n"
        
    
    return func

