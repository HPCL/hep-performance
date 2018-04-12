'''
Brian Gravelle, Boyana Norris

Useful functions for processing mictest data in the python notebooks 
This will evolve into a real library
'''




############################################################################################

#                                                    Imports

############################################################################################


import os
from os import listdir
from os.path import isfile, join

import sys

try:
    import taucmdr
except ImportError:
    sys.path.insert(0, os.path.join(os.environ['__TAUCMDR_HOME__'], 'packages'))
finally:
    from taucmdr.model.project import Project
    from taucmdr.data.tau_trial_data import TauTrialProfileData

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
font = {'weight' : 'bold',
        'size'   : 24
}
matplotlib.rc('font', **font)

import pandas as pd
import math
import numpy as np
import operator
import time
import re
import collections
import seaborn as sns
# for fancy tables
from IPython.core.display import display, HTML, display_html





############################################################################################

#                                   retrieving data from profiles

############################################################################################



#TODO add params so this is a real function
def get_pandas_non_summary():
    '''
    returns a dictionary of pandas
    keys are the metrics that each panda has data for
    vals are the pandas that have the data organized however they organzed it
    DEPRECATED - may not work
    '''
    num_trials = Project.selected().experiment().num_trials
    trials = Project.selected().experiment().trials(xrange(0, num_trials))
    trial_data = {}
    for i in xrange(0, num_trials):
        trial_data[i] = trials[i].get_data()
        
    start = time.time()
    metric_data = {}

    for trial in xrange(0, num_trials):
        thread_data = []
        for i in xrange(0, len(trial_data[trial])):
            for j in xrange(0, len(trial_data[trial][i])):
                for k in xrange(0, len(trial_data[trial][i][j])):
                    thread_data.append(trial_data[trial][i][j][k].interval_data())
                    metric_data[trial_data[trial][i][j][k].metric] = pd.concat(thread_data)
                    metric_data[trial_data[trial][i][j][k].metric].index.names = ['trial', 'rank', 'context', 'thread', 'region']
        
    end = time.time()
    
    print('Time spent constructing dataframes %s' %(end-start))
    print('\nMetrics included:')
    for m in metric_data.keys():
        print("\t%s"%m)
    
    return metric_data

def load_perf_data(application,experiment,nolibs=False,scaling=False):
    '''
        Return a Pandas dictionary from data in the detault path
        TODO filtering and scaling
    '''
    path = ".tau/" + application + "/" + experiment + "/"
    if not os.path.exists(path):
        sys.exit("Error: invalid data path: %s" % path)

    if scaling:
        metric_dict = get_pandas_scaling(path)
    else:
        metric_dict = get_pandas(path)
    
    if nolibs and not scaling:
        filtered_dict = {}
        for k,v in metric_dict.items():
            if k == 'METADATA': filtered_dict[k] = metric_dict[k]
            else: filtered_dict[k] = filter_libs_out(metric_dict[k])
        return filtered_dict
    else:
        return metric_dict

def get_pandas(path, callpaths=False):
    '''
    returns a dictionary of pandas
        - keys are the metrics that each panda has data for
    params
        - path is the path to the trials (should e directory filled with numbered dirs)
        - 
    vals are the pandas that have the data organized however they organzed it
        - samples are turned into summaries
        - tau cmdr must be installed and .tau with the relevant data must be in this dir
    '''
    if not os.path.exists(path):
        sys.exit("Error: invalid data path: %s" % path)
    metric_data = {}
    
    paths = [path+n+'/' for n in listdir(path) if (not isfile(join(path, n)))]
    num_trials = len(paths)
    #files = [f for f in listdir(path) if not isfile(join(p, f))]
    for p in paths:
        d = [f for f in listdir(p) if (not isfile(join(p, f))) and (not (f == 'MULTI__TIME'))]
        prof_data = TauTrialProfileData.parse(p+'/'+d[0])
        time_data = TauTrialProfileData.parse(p+'/MULTI__TIME')
        prof_data.metadata = time_data.metadata
        metric = prof_data.metric
        metric_data[metric] = prof_data.summarize_samples()

        metric_data[metric].index.names = ['rank', 'context', 'thread', 'region']
        if not callpaths:
            #metric_data[metric]['Total'] = metric_data[metric][metric_data[metric].index.get_level_values('region').str.match('[SUMMARY] .TAU application')]
            metric_data[metric] = metric_data[metric][~metric_data[metric].index.get_level_values('region').str.contains(".TAU application")]
            
        metric_data['METADATA'] = prof_data.metadata
    return metric_data

def get_pandas_scaling(path, callpaths=False):
    '''
    returns a dictionary of dictionaries of pandas
    The first layer of keys is the number of threads
    The second layer keys are the metrics that each panda has data for
    vals are the pandas that have the data organized however they organzed it
        - samples are turned into summaries
        - tau cmdr must be installed and .tau with the relevant data must be in this dir
    '''
    
    metric_data = {}
    
    # generate list of paths to read in
    paths = [path+n+'/' for n in listdir(path) if (not isfile(join(path, n)))]
    num_trials = len(paths)
    if num_trials <= 0:
        print "ERROR reading trials"

    # gather data for path lists
    # puts it in metric data
    #    starts as dict (thread count) of dict (metrics) of list (individual trials)
    for p in paths:
        d = [f for f in listdir(p) if (not isfile(join(p, f))) and (not (f == 'MULTI__TIME'))]

        try:
            trial_dir = p+'/'+d[0]
        except:
            # if the dir is empty that trial ffailed for some reason so skip
            # TODO make this more precise (the metric is just a guess based on the previous one)
            print "Possible missing metric: \nnthread = %d \nmetric = %s" % (num_threads, metric)
            continue
            # print p # some trials don't have data use this to figure out which
            # missing data caused by errors in experiment scripts or crashes

        prof_data = TauTrialProfileData.parse(trial_dir)
        metric = prof_data.metric

        prof_list = [f for f in listdir(trial_dir)]
        num_threads = len(prof_list)

        if num_threads not in metric_data.keys():
            metric_data[num_threads] = {}

        if metric not in metric_data[num_threads].keys():
            metric_data[num_threads][metric] = []

        metric_data[num_threads][metric].append(prof_data.summarize_samples())
        metric_data[num_threads][metric][-1].index.names = ['rank', 'context', 'thread', 'region']
        if not callpaths:
            # this line magically gets rid of the .TAU samples that otherwise unhelpfully dominate the data
            metric_data[num_threads][metric][-1] = metric_data[num_threads][metric][-1][~metric_data[num_threads][metric][-1].index.get_level_values('region').str.contains(".TAU application")]

        try:
            time_data = TauTrialProfileData.parse(p+'/MULTI__TIME')
            prof_data.metadata = time_data.metadata
            metric_data[num_threads]['METADATA'] = prof_data.metadata
        except:
            # TODO make this more precise (the metric is just a guess based on the previous one)
            print "Possible missing metric: \nnthread = %d \nmetric = %s" % (num_threads, metric)

    # average metric data
    #   turns dict of dict of list into dict of dict of panda (average of listed trials)
    for kt in metric_data:
        for km in metric_data[kt]:
            if not (km == 'METADATA'):
                ntrials = len(metric_data[kt][km])
                temp = metric_data[kt][km][0].copy()
                temp.index = temp.index.droplevel()
                metric_sum = temp.unstack()
                for i in range(1, ntrials):
                    temp = metric_data[kt][km][i].copy()
                    temp.index = temp.index.droplevel()
                    metric_sum = metric_sum + temp.unstack()
                metric_data[kt][km] = (metric_sum / ntrials).stack()

    return metric_data

def remove_erroneous_threads(metric_data, thread_list):
    '''
    some trial are intended to run with n threads but m != n threads are recorded
    this function allows the user to easily remove trials that don't conform
    
    - metric_data is the dictionary output from get_pandas_scaling()
    - thread_list is the list of thread counts requested
        - any thread counts not in thread list will be excluded
        - this may not be entirely accurate if an erroneous count is equal to a real count
    - returns new dictionary
    '''

    filtered_data = {}
    for k in metric_data:
        if k in thread_list:
            filtered_data[k] = metric_data[k]

    return filtered_data


def combine_metrics(metric_dict,inc_exc='Inclusive'):
    if inc_exc == 'Inclusive': todrop = 'Exclusive'
    else: todrop = 'Inclusive'
    alldata = metric_dict['PAPI_TOT_CYC'].copy().drop(['Calls','Subcalls',todrop,'ProfileCalls'], axis=1)
    alldata['PAPI_TOT_CYC'] = alldata[inc_exc]
    alldata.drop([inc_exc],axis=1,inplace=True)

    for x in metric_dict.keys():
        if x in ['PAPI_TOT_CYC','METADATA']: continue
        alldata[x] = metric_dict[x][inc_exc]
    return alldata
                  

############################################################################################

#                                   Printing and plotting data

############################################################################################

def print_metadata(data):
    
    for key in data['METADATA']:
        print('{:50} {}'.format(key,data['METADATA'][key] ))


def print_available_metrics(data, scaling=False):
    if not scaling:
        for key in data:
            if not key == 'METADATA':
                print(key)
    else:
        for key in data[data.keys()[0]]:
            if not key == 'METADATA':
                print(key)

def set_chart_font_size(fntsize):
    font = {'size'   : fntsize}; matplotlib.rc('font', **font)

def bar_chart(dfs,x='region',y='Inclusive',size=(15,7)):
    fig, ax = plt.subplots(figsize=size)
    dfs.plot(ax = ax, kind='bar')
    return fig

def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)
    
def highlight(df, fmt="{:.2%}", ht=0.5, hcolor='yellow'):
    return df.style.format(fmt).apply(lambda x: ["background: %s" % hcolor if v >= ht else "" for v in x], axis = 1)

def highlight_higher(x):
    return ["background: yellow" if v > 0.8 else "" for v in x]

def select_metric_from_scaling(scale_data, metric):
    '''
    returns a single level dictionary with just the requested metric
    dictionary keys are the thread counts
    '''
    metric_data = {}
    for kt in scale_data:
        try:
            metric_data[kt] = scale_data[kt][metric]
        except:
            print "ERROR getting %s for thread %d" % (metric, kt)

    return metric_data

def scaling_plot(data, inclusive=True):
    '''
    data is a single metric scaling dictionary
    '''
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby(['thread','region'])[which].sum().reset_index().groupby(['thread']).var()
    if plot: bar_chart(temp)
    if sort: return temp.sort_values(by=which,ascending=False)
    else: return temp



############################################################################################

#                                   Hotspots and related filtering functions

############################################################################################




def filter_libs_out(dfs):
    dfs_filtered = dfs.groupby(level='region').filter(lambda x: not (x.name == '.TAU application') and ('tbb' not in x.name) and ('syscall' not in x.name)  and ('std::' not in x.name))
    return dfs_filtered

def largest_stddev(dfs,n):
    return dfs['Exclusive'].groupby(level=region).std(ddof=0).dropna().sort_values(ascending=False, axis=0)[:n]

def largest_correlation(dfs,n):
    unstacked_dfs = dfs.unstack(region)
    return unstacked_dfs.loc[:,'Exclusive'].corrwith(unstacked_dfs.loc[:,('Inclusive','.TAU application')]).sort_values(ascending=False, axis=0)[:n]

def largest_exclusive(dfs,n):
    return dfs['Exclusive'].groupby(level='region').max().nlargest(n)

def largest_inclusive(dfs,n):
    return dfs['Inclusive'].groupby(level='region').max().nlargest(n)

def means(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby('region')[which].sum().reset_index().groupby('region').mean()
    if sort: temp = temp.sort_values(by=which,ascending=False)
    if plot: bar_chart(temp)
    return temp

def thread_stddev(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby(['thread','region'])[which].sum().reset_index().groupby(['thread']).std()
    if plot: bar_chart(temp)
    if sort: return temp.sort_values(by=which,ascending=False)
    else: return temp

def thread_variance(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby(['thread','region'])[which].sum().reset_index().groupby(['thread']).var()
    if plot: bar_chart(temp)
    if sort: return temp.sort_values(by=which,ascending=False)

def hotspots(dfs, n, flag):
    if flag == 0:
        largest = largest_exclusive(dfs,n)
    elif flag == 1:
        largest = largest_inclusive(dfs,n)
    elif flag == 2:
        largest = largest_stddev(dfs,n)
    elif flag == 3:
        largest = largest_correlation(dfs,n)
    else:
        print('Invalid flag')
    y = ['exclusive time', 'inclusive time', 'standard deviation', 'correlation to total runtime']
    print('Hotspot Analysis Summary')
    print('='*80)
    print('The code regions with largest %s are: ' %y[flag])
    for i in xrange(0,n):
        try:
            print('%s: %s (%s)' %(i+1, largest.index[i], largest[i]))
        except:
            break

def get_hotspots(metric,n=10):
    print('selected metric: %s\n' %metric)
    hotspots(expr_intervals[metric], n, 1)
    
    print('='*80)
    
    filtered_dfs = filter_libs_out(expr_intervals[metric])
    hotspots(filtered_dfs, n, 1)


############################################################################################

#                                   Stuff that was supposed to print prety tables

############################################################################################

# UTILITIES (NOT WORKING)
# TODO make this work

# using something like head() in panda will probably be better
# or to_html()
# This is where useful functions go. Currently includes:

# table printing

# from IPython.core.display import display, HTML, display_html

# def parse_region(region):
#     _location_re = re.compile(r'\{(.*)\} {(\d+),(\d+)}-{(\d+),(\d+)}')
#     func = region.split('=>')[-1]
#     loc = re.search(r'\[(.*)\]', func)
#     if loc:
#         location = loc.group(1)
#         match = _location_re.match(location)
#         if match:
#             return match.group(1)
#     if '[SAMPLE]' in func:
#         loc = re.search(r'\[\{(.*)\} \{(\d+)\}\]', func)
#         if loc:
#             return loc.group(1)

# def add_link(multiindex):
#     link = parse_region(multiindex[4])
#     if link:
#         return (multiindex[0],multiindex[1],multiindex[2],multiindex[3],'<a href="{0}">{1}</a>'.format((link), multiindex[4]))
#     else:
#         return multiindex

    
# def print_table(intervals):
#     '''
#     intervals is a panda with a metric's data
#     '''
#     expr_intervals_link = intervals.copy()
#     expr_intervals_link.index = expr_intervals_link.index.map(lambda x: add_link(x))
#     HTML(expr_intervals_link.to_html(escape=False))

    
# metric='PAPI_TOT_CYC'
# print_table(expr_intervals[metric])
# expr_intervals_link = expr_intervals[metric].copy()
# expr_intervals_link.index = expr_intervals_link.index.map(lambda x: add_link(x))
# HTML(expr_intervals_link.to_html(escape=False))
