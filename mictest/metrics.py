'''
functions to add derived metrics to the dictionaries of metrics

please use the examples to add more

Existing list of prewritten metrics:
add_IPC(metrics)                - Instructions per Cycle
add_CPI(metrics)                - Cycles per instruction
add_VIPC(metrics)               - vector instructions per cycle
add_VIPI(metrics)               - vector instructions per instruction (i.e. fraction of total)
add_L1_missrate(metrics)        - miss rate for L1 cache
add_DERIVED_BRANCH_MR(metrics)  - fraction of miss predicted branches 

add_DERIVED_RATIO_FETCH_STL_TOT_CYC(metrics)

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

def add_VIPC(metrics):
    '''
    add vector instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    CYC = 'PAPI_TOT_CYC'
    VEC = 'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(VEC)) ):
        print "ERROR adding VecEfficiency to metric dictionary"
        return False
    
    vec = metrics[VEC].copy()
    cyc = metrics[CYC].copy()
    vec.index = vec.index.droplevel()
    cyc.index = cyc.index.droplevel()

    uvec = vec.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_VIPC'] = (uvec / ucyc).stack()

    return True

def add_VIPI(metrics):
    '''
    add vector instructions per ins to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    VEC = 'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD'
    

    if(not (metrics.has_key(INS) and metrics.has_key(VEC)) ):
        print "ERROR adding VecEfficiency to metric dictionary"
        return False
    
    vec = metrics[VEC].copy()
    ins = metrics[INS].copy()
    vec.index = vec.index.droplevel()
    ins.index = ins.index.droplevel()

    uvec = vec.unstack()
    uins = ins.unstack()

    metrics['DERIVED_VIPI'] = (uvec / uins).stack()

    return True

def add_StallPercent(metrics):
    '''
    add vector instructions per ins to the metrics dictionary
    returns true if successful
    '''
    CYC = 'PAPI_TOT_CYC'
    STL = 'PAPI_RES_STL'
    

    if(not (metrics.has_key(STL) and metrics.has_key(CYC)) ):
        print "ERROR adding StallPercent to metric dictionary"
        return False
    
    cyc = metrics[CYC].copy()
    stl = metrics[STL].copy()
    cyc.index = cyc.index.droplevel()
    stl.index = stl.index.droplevel()

    ucyc = cyc.unstack()
    ustl = stl.unstack()

    metrics['DERIVED_STALL_PERCENT'] = (ustl / ucyc).stack()

    return True

def add_DERIVED_SP_VOPO(metrics):
    if (not metrics.has_key('PAPI_SP_OPS')):
        print 'ERROR adding DERIVED_SP_VOPO to metric dictionary'
        return False
    a0 = metrics['PAPI_SP_OPS'].copy()
    a0.index = a0.index.droplevel()
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_NATIVE_FP_ARITH:128B_PACKED_SINGLE')):
        print 'ERROR adding DERIVED_SP_VOPO to metric dictionary'
        return False
    a1 = metrics['PAPI_NATIVE_FP_ARITH:128B_PACKED_SINGLE'].copy()
    a1.index = a1.index.droplevel()
    u1 = a1.unstack()
    if (not metrics.has_key('PAPI_NATIVE_FP_ARITH:256B_PACKED_SINGLE')):
        print 'ERROR adding DERIVED_SP_VOPO to metric dictionary'
        return False
    a2 = metrics['PAPI_NATIVE_FP_ARITH:256B_PACKED_SINGLE'].copy()
    a2.index = a2.index.droplevel()
    u2 = a2.unstack()
    metrics['DERIVED_SP_VOPO'] = ((u1 + u2) / (u0 )).stack()

    return True


def add_L1_missrate(metrics, lst=True):
    '''
    add Instructions per cycle to the metrics dictionary
    lst is if it should use lst ins instead of L1
    returns true if successful
    '''
    if lst:
        LST = 'PAPI_LST_INS' # total load store
    else:
        LST = 'PAPI_L1_TCA' # total load store
        
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

def add_L2_missrate(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    L2A = 'PAPI_L2_TCA' # total load store
    L2M = 'PAPI_L2_TCM'  # L1 misses
    
    if(not (metrics.has_key(L2A) and metrics.has_key(L2M)) ):
        print "ERROR adding L2 MR to metric dictionary"
        return False
        
    access = metrics[L2A].copy()
    misses = metrics[L2M].copy()
    access.index = access.index.droplevel()
    misses.index = misses.index.droplevel()    
        
    
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L2_MISSRATE'] = (umisses / uaccess).stack()
        
        
    return True


def add_L3_missrate(metrics, llc=False):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''

    if llc:
        L3A = 'PAPI_NATIVE_LLC_REFERENCES' # total load store
        L3M = 'PAPI_NATIVE_LLC_MISSES'  # L1 misses
    else:
        L3A = 'PAPI_L3_TCA' # total load store
        L3M = 'PAPI_L3_TCM'  # L1 misses
    
    if(not (metrics.has_key(L3A) and metrics.has_key(L3M)) ):
        print "ERROR adding L3 MR to metric dictionary"
        return False
        
    access = metrics[L3A].copy()
    misses = metrics[L3M].copy()
    access.index = access.index.droplevel()
    misses.index = misses.index.droplevel()    
        
    
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L3_MISSRATE'] = (umisses / uaccess).stack()
        
        
    return True

def add_DERIVED_BRANCH_MR(metrics):
    if (not metrics.has_key('PAPI_BR_MSP')):
        print 'ERROR adding DERIVED_BRANCH_MR to metric dictionary'
        return False
    a0 = metrics['PAPI_BR_MSP'].copy()
    a0.index = a0.index.droplevel()
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_BR_CN')):
        print 'ERROR adding DERIVED_BRANCH_MR to metric dictionary'
        return False
    a1 = metrics['PAPI_BR_CN'].copy()
    a1.index = a1.index.droplevel()
    u1 = a1.unstack()
    metrics['DERIVED_BRANCH_MR'] = (u0 / u1).stack()

    return True



def add_DERIVED_RATIO_FETCH_STL_TOT_CYC(metrics):
    if (not metrics.has_key('PAPI_NATIVE_FETCH_STALL')):
        print 'ERROR adding DERIVED_RATIO_FETCH_STL_TOT_CYC to metric dictionary'
        return False
    a0 = metrics['PAPI_NATIVE_FETCH_STALL'].copy()
    a0.index = a0.index.droplevel()
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_TOT_CYC')):
        print 'ERROR adding DERIVED_RATIO_FETCH_STL_TOT_CYC to metric dictionary'
        return False
    a1 = metrics['PAPI_TOT_CYC'].copy()
    a1.index = a1.index.droplevel()
    u1 = a1.unstack()
    metrics['DERIVED_RATIO_FETCH_STL_TOT_CYC'] = (u0 / u1).stack()

    return True



def add_metric_to_scaling_data(data, metric_func, other=None):
    '''
    data is data with scaling information
    metric_func is a function pointer to one of the metric functions in this file
    '''
    results = {}
    for kthread in data:
        if other is None:
            results[kthread] = metric_func(data[kthread])
        else:
            results[kthread] = metric_func(data[kthread], other)

    for kthread in results:
        if not results[kthread]:
            print "ERROR adding metric to thread count: " + str(kthread)


############################################################################################

#                                   Statistics and plotting

############################################################################################



def plot_metric(dfs, metric, function='', inc_exc='Inclusive', percent=False):
    # inc_exc is either Inclusive or Exclusive
    metricdf = dfs[metric]
    if function:
        metricdf_fun = metricdf.loc[metricdf.index.get_level_values('region').str.contains(function)].copy()
    else:
        metricdf_fun = metricdf.copy()
    metricdf_fun['Thread Number'] = metricdf_fun.index.get_level_values('thread')
    if percent:
        metricdf_fun.style.format({inc_exc: '{:,.2%}'.format})
    g = sns.barplot(x='Thread Number', y=inc_exc, data=metricdf_fun)
    return metricdf_fun, g

def compute_correlations(metrics_dict, inc_exc='Inclusive',highlight_threshold=0.5):
    # Compute and display pair-wise metrics correlations, highlighting the 
    # values greater than highlight_threshold.
    alldata = combine_metrics(metrics_dict,'Inclusive')
    correlations = alldata.corr()
    cm = sns.light_palette("yellow", as_cmap=True)
    correlations = correlations.style.format("{:.2%}").background_gradient(cmap=cm)
        #.apply(lambda x: ["background: yellow" if v > 0.5 else "" for v in x], axis = 1)
    return correlations





############################################################################################

#                                   functions for generating metrics

############################################################################################

def gen_metric(met_list, name):
    func = "def add_" + name + "(metrics):\n"

    for m in range(len(met_list)):

        func += "\tif (not metrics.has_key('" + met_list[m] + "')):\n"
        func += "\t\tprint 'ERROR adding " + name + " to metric dictionary'\n"
        func += "\t\treturn False"

        func += "\ta" + str(m) + " = metrics['" + met_list[m] + "'].copy()\n"
        func += "\ta" + str(m) + ".index = a" + str(m) + ".index.droplevel()\n"
        func += "\tu" + str(m) + " = a" + str(m) + ".unstack()\n"
    

    func += "\tmetrics[" + name + "] = " + "\"PLEASE IMPLEMENT THIS PART\"\n\n"
    func += "\treturn True\n\n\n"
        
    
    return func


def gen_metric_complete(met_list, operation, name):
    func = "def add_" + name + "(metrics):\n"

    for m in range(len(met_list)):

        func += "\tif (not metrics.has_key('" + met_list[m] + "')):\n"
        func += "\t\tprint 'ERROR adding " + name + " to metric dictionary'\n"
        func += "\t\treturn False\n"

        func += "\ta" + str(m) + " = metrics['" + met_list[m] + "'].copy()\n"
        func += "\ta" + str(m) + ".index = a" + str(m) + ".index.droplevel()\n"
        func += "\tu" + str(m) + " = a" + str(m) + ".unstack()\n"
    
        operation.replace(met_list[m], "u" + str(m))

    func += "\tmetrics['" + name + "'] = " + operation + "\n\n"
    func += "\treturn True\n\n\n"
        
    
    return func

