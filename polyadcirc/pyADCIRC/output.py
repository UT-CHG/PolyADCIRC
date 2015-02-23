"""
THis module provides methods for retrieving data from ASCII ADCIRC formatted
timeseries and non-timeseries data files and returning that data as numpy
arrays.
"""

import numpy as np
import polyadcirc.pyADCIRC.fort15_management as f15

def get_data_nts(kk, path, data, nts_data, file_names=["tinun.63"]):
    """
    Retrieves data from a nontimeseries formatted files in path and adds data
    to ``nts_data``

    :param int kk: run number
    :param string path: ``RF_directory_*`` path
    :param data: :class:`~polyadcirc.run_framework.domain`
    :param dict() nts_data: reference to dict() to store data to
    :param list() file_names: list of :program:`ADCIRC` output files to
        retrieve data from

    """
    for fid in file_names:
        key = fid.replace('.', '')
        if key == "timemax63":
            ts_sr, time_obs = get_ts_sr(path, "fort.63", True)  
            i = np.argmax(ts_sr, 1)
            nts_data[key][..., kk] = np.squeeze(time_obs[i])
        else:
            nts_data[key][..., kk] = get_nts_sr(path, data, fid)
    
def get_nts_sr(path, data, file_name):
    """
     Retrieves data from a nontimeseries formatted file in path and adds data
    to ``nts_data``

    :param string path: ``RF_directory_*`` path
    :param data: :class:`~polyadcirc.run_framework.domain`
    :param string file_name: :program:`ADCIRC` output file to retrieve data
        from

    :rtype: :class:`numpy.ndarray`
    :returns: array of dimensions (data.node_num,)
    """

    single_nodal_data = np.zeros((data.node_num,))        
    with open(path+'/'+file_name, 'r') as fid:
        # skip header information
        # skip some header information
        fid.readline()
        fid.readline()
        fid.readline()
        for i in xrange(data.node_num): 
            single_nodal_data[i] = np.fromstring(fid.readline(), sep=' ')[1]
    return single_nodal_data

def get_data_ts(kk, path, ts_data, time_obs, file_names=["fort.61"],
        timesteps=None):
    """
    Retrieves data from a timeseries formatted files in path and adds data
    to ``ts_data``

    :param int kk: run number
    :param string path: ``RF_directory_*`` path
    :param dict() ts_data: reference to dict() to store data to
    :param dict() time_obs: reference to dict() to store time data to
    :param list() file_names: list of :program:`ADCIRC` output files to
    :param int timesteps: number of timesteps to read

    """
    for fid in file_names:
        key = fid.replace('.', '')
        if kk == 0:
            ts_data[key][..., kk], time_obs[key] = get_ts_sr(path, fid, True,
                    timesteps)
        else:
            ts_data[key][..., kk] = get_ts_sr(path, fid, timesteps)[0] 

def get_ts_sr(path, file_name, get_time=False, timesteps=None):
    """
     Retrieves data from a timeseries formatted file in path and adds data
    to ``ts_data``

    :param string path: ``RF_directory_*`` path
    :param string file_name: :program:`ADCIRC` output file to retrieve data
        from
    :param boolean: flag for whether or not to record times of recordings
    :param int timesteps: number of timesteps to read
    :rtype: :class:`numpy.ndarray`
    :returns: array of dimensions (data.node_num,)
    """

    with open(path+'/'+file_name, 'r') as fid:
        # skip some header information
        fid.readline()
        line = fid.readline().strip()#rpartition('File')[0]
        line = np.fromstring(line, sep=' ')
        total_obs = int(line[0])
        if timesteps and timesteps < total_obs:
            total_obs = timesteps
        meas_locs = int(line[1])
        irtype = f15.filetype[file_name.replace('.','')][1]
        single_timeseries_data = np.zeros((meas_locs, total_obs, irtype))
        if get_time:
            time_obs = np.zeros((total_obs,))
        else:
            time_obs = None
        for i in xrange(total_obs):
            if get_time:
                time_obs[i] = np.fromstring(fid.readline(), sep=' ')[0]
            else:
                fid.readline()
            for j in xrange(meas_locs): 
                single_timeseries_data[j, i, ...] = np.fromstring(fid.readline(), 
                                                                  sep=' ')[1:]
    if irtype == 1:
        single_timeseries_data = np.squeeze(single_timeseries_data, axis=2)
    return (single_timeseries_data, time_obs)
