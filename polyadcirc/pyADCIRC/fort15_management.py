# Lindley Graham 4/8/2013
"""
fort15_management handles the reading/writing of ``fort.15`` formatted files
"""

import numpy as np
import os, re, math
import polyadcirc.pyADCIRC.basic as basic

filetype = {'fort61':(True, 1), 'fort62':(True, 2), 'fort63':(False, 1),
            'tinun63':(False, 1), 'maxele63':(False, 1), 
            'maxvel63':(False, 1), 'nodeflag63':(False, 1),
            'rising63':(False, 1), 'elemaxdry63':(False, 1),
            'fort64':(False, 2), 'fort71':(True, 1), 'fort72':(True, 2),
            'fort73':(False, 1), 'fort74':(False, 2)}

def read_recording_data(data, path=None):
    """
    Reads in ``fort.15`` and stores the following in data as a
    :class:`~polyadcirc.pyADCIRC.basic.time` object
    (``DT``, ``STATIM``, ``RNDAY``, ``DRAMP``)

    Calulcates and stores:
        
        * recording[key] = (meas_locs, total_obs, irtype)
        * stations[key] = list() of locations

    :type data: :class:`~polyadcirc.run_framework.domain`
    :param data: object to store reference to
        :class:`~polyadcirc.pyADCIRC.basic.time` 
    :type path: string or None
    :param path: directory containing ``fort.15`` file 
    :return: reference to ``data.recording`` and ``data.stations``
    :rtype: :class:`~polyadcirc.pyADCIRC.basic.time`

    """
    if path == None:
        path = os.getcwd()

    file_name = path+'/fort.15'
        
    data.stations = {}
    data.recording = {}

    with open(file_name, 'r+') as fid:
        line = fid.readline()
        while line != '':
            if line.find('DT') >= 0:
                line = line.partition('!')
                dt = float(line[0].strip()) # pylint: disable=C0103
            elif line.find('IHOT') >= 0:
                line = line.partition('!')
                ihot = int(line[0].strip())
                data.ihot = ihot
            elif line.find('STATIM') >= 0:
                line = line.partition('!')
                statim = float(line[0].strip())
            elif line.find('RNDAY') >= 0:
                line = line.partition('!')
                rnday = float(line[0].strip())
            elif line.find('DRAMP') >= 0:
                line = line.partition('!')
                dramp = np.fromstring(line[0].strip(), sep=' ')#float(line[0].strip())
                data.time = basic.time(dt, statim, rnday, dramp) 
            elif line.find('H0') >= 0:
                line = line.partition('!')[0]
                line = np.fromstring(line, sep=' ')
                data.h0 = np.fromstring(line[0])[0]
            elif line.find('UNIT  61') >= 0:
                line = line.partition('!')
                _read_record(fid, 'fort61', line, data)
            elif line.find('UNIT  62') >= 0:
                line = line.partition('!')
                _read_record(fid, 'fort62', line, data)
            elif line.find('NOUTC') >= 0:
                line = line.partition('!')
                #_read_record(fid, 'fort91', line, dt, data)
            elif line.find('UNIT  71/72') >= 0:
                line = line.partition('!')
                _read_record7(fid, 'fort71', 'fort72', line, data)
            elif line.find('NOUTGE') >= 0:
                line = line.partition('!')
                _read_record(fid, 'fort63', line, data)
            elif line.find('UNIT  64') >= 0:
                line = line.partition('!')
                _read_record(fid, 'fort64', line, data)
            elif line.find('NOUTGC') >= 0:
                line = line.partition('!')
                #_read_record(fid, 'fort93', line, dt, data)
            elif line.find('UNIT  73/74') >= 0:
                line = line.partition('!')
                _read_record7(fid, 'fort73', 'fort74', line, data)
            line = fid.readline()
    return data.time

def _read_record(fid, key, line, data):
    """
    Saves metadata to ``data.stations[key]`` and ``data.recording[key]`` that
    is used to preallocate arrays for data recording

    :param fid: :class:``file`` object
    :param string key: ADCIRC Output File Type sans ``.``
    :param line: array of parameters read from ``fort.15`` file
    :type line: :class:``np.array``
    :param data: object to store mesh specific data
    :type data: :class:``~polyadcirc.run_framework.domain``
    :rtype: string
    :returns: station type description

    """
    nout, touts, toutf, nspool = np.fromstring(line[0].strip(), sep=' ')
    touts = max(touts, data.time.statim)
    toutf = min(toutf, data.time.rnday+data.time.statim)
    #print key, nout, touts, toutf, nspool
    description = None
    if nout != 0 and nspool != 0:
        total_obs = int((toutf - touts) * 24 * 60 * 60 / data.time.dt/ nspool)
    else:
        total_obs = 0    
    if filetype[key][0]:
        line = fid.readline().partition('!')
        meas_locs = int(line[0].strip())
        description = line[-1]
        stations = []
        for i in xrange(meas_locs):
            line = fid.readline()
            line = line.partition('!')
            line = re.findall(r"[-*\d\.\d]+", line[0].strip())
            stations.append(basic.location(float(line[0]),
                                           float(line[-1])))
        data.stations[key] = stations
    else:
        meas_locs = data.node_num
    data.recording[key] = (meas_locs, total_obs, filetype[key][1]) 
    return description

def _read_record7(fid, key1, key2, line, data):
    """
    Saves metadata to ``data.stations[key]`` and ``data.recording[key]`` that
    is used to preallocate arrays for data recording for ``fort.7#`` type
    ADCIRC output files

    :param fid: :class:``file`` object
    :param string key1: ADCIRC Output File Type sans ``.``
    :param string key2: ADCIRC Output File Type sans ``.``
    :param line: array of parameters read from ``fort.15`` file
    :type line: :class:``np.array``
    :param data: object to store mesh specific data
    :type data: :class:``~polyadcirc.run_framework.domain``
    :rtype: string
    :returns: station type description

    """
    nout, touts, toutf, nspool = np.fromstring(line[0].strip(), sep=' ')
    touts = max(touts, data.time.statim)
    toutf = min(toutf, data.time.rnday+data.time.statim)
    description = None
    if nout != 0 and nspool != 0:
        total_obs = int((toutf - touts) * 24.0 * 60 * 60 / data.time.dt/ nspool)
    else:
        total_obs = 0    
    if filetype[key1][0]:
        line = fid.readline().partition('!')
        meas_locs = int(line[0].strip())
        stations = []
        description = line[-1]
        for i in xrange(meas_locs):
            line = fid.readline()
            line = line.partition('!')
            line = re.findall(r"[-*\d\.\d]+", line[0].strip())
            stations.append(basic.location(float(line[0]),
                                           float(line[-1])))
        data.stations[key1] = stations
        data.stations[key2] = stations
    else:
        meas_locs = data.node_num
    data.recording[key1] = (meas_locs, total_obs, filetype[key1][1])
    data.recording[key2] = (meas_locs, total_obs, filetype[key2][1])
    return description

def subdomain(fulldomain_path, subdomain_path):
    """
    Create a modifed ``fort.15`` for the subdomain at ``subdomain_path``.
    
        * Reduce RNDAY by 0.05%
        * Set NBFR to 0
        * Remove periodic forcing boundary frequencies
        * Remove recording stations outside of the subdomain grid and update
          the number of stations accordingly

    :param int flag: type of subdomain 0 - ellipse, 1 - circle
    :param string fulldomain_path: fulldomain dir containing ``fort.15`` file
    :param string subdomain_path: subdomain dir containing ``fort.15`` file

    """
    class fdata:
        """ Storage class for station information """
        def __init__(self):
            self.stations = {}
            self.recording = {}
    
    data = fdata()
        
    with open(fulldomain_path+'/fort.15', 
              'r') as fid_read, open(subdomain_path+'/fort.15', 
                                     'w') as fid_write:
        line = fid_read.readline()
        while line != '':
            if line.find('DT') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                dt = float(line[0].strip()) # pylint: disable=C0103
            elif line.find('STATIM') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                statim = float(line[0].strip())
            elif line.find('RNDAY') >= 0:
                line = line.partition('!')
                rnday = float(line[0].strip())*0.95
                fid_write.write(' {:<6.3f} {:>30}{}'.format(rnday, '!',
                                                            line[-1])) 
            elif line.find('DRAMP') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                dramp = np.fromstring(line[0].strip(), sep=' ', dtype=float)
                data.time = basic.time(dt, statim, rnday, dramp) 
            elif line.find('NBFR') >= 0:
                line = line.partition('!')
                fid_write.write(' {:<35d} {}{}'.format(0, '!', line[-1]))
                line = line[0]
                while not line.find('ANGINN') >= 0:
                    line = fid_read.readline()
                fid_write.write(line)
            elif line.find('NFFR') >= 0:
                while not line.find('NOUTE') >= 0:
                    line = fid_read.readline()
                fid_write.write(line)
                line = line.partition('!')
                description = _read_record(fid_read, 'fort61', line, data)
                _write_record(fid_write, 'fort61', description, data)
            elif line.find('UNIT 62') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                description = _read_record(fid_read, 'fort62', line, data)
                _write_record(fid_write, 'fort62', description, data)
            elif line.find('NOUTC') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                #description = _read_record(fid_read, 'fort91', line, dt, data)
                #_write_record(fid_write, 'fort91', description, data)
            elif line.find('UNIT 71/72') >= 0:
                fid_write.write(line)
                line = line.partition('!')
                description = _read_record7(fid_read, 'fort71', 'fort72', line,
                                            data) 
                _write_record(fid_write, 'fort71', description, data)
            else:
                fid_write.write(line)
            line = fid_read.readline()

def trim_locations(flag, subdomain_path, locs):
    """
    Remove locations outside of the subdomain from locs

    :param int flag: type of subdomain 0 - ellipse, 1 - circle
    :param string subdomain_path: subdomain dir containing ``fort.15`` file
    :param list() locs: list of :class:`~polyadcirc.pyADCIRC.basic.location`
        objects
    :rtype: list()
    :returns: list of locations inside the subdomain

    """
    if flag == 0:
        return trim_locations_ellipse(subdomain_path, locs)
    elif flag == 1:
        return trim_locations_circle(subdomain_path, locs)

def trim_locations_circle(subdomain_path, locs):
    """
    Remove locations outside of the circular subdomain from locs

    :param string subdomain_path: subdomain dir containing ``fort.15`` file
    :param list() locs: list of :class:`~polyadcirc.pyADCIRC.basic.location`
        objects
    :rtype: list()
    :returns: list of locations inside the subdomain

    """
    with open(subdomain_path+"/shape.c14", "r") as fid:
        line = fid.readline().split()
        xb = float(line[0])
        yb = float(line[1])
        r = float(fid.readline())
    for loc in locs:
        if (xb-loc.x)**2 + (yb-loc.y)**2 >= r**2:
            locs.remove(loc)    
    return locs

def trim_locations_ellipse(subdomain_path, locs):
    """
    Remove locations outside of the elliptical subdomain from locs

    :param string subdomain_path: subdomain dir containing ``fort.15`` file
    :param list() locs: list of :class:`~polyadcirc.pyADCIRC.basic.location`
        objects 
    :rtype: list()
    :returns: list of locations inside the subdomain

    """
    with open(subdomain_path+"/shape.e14", "r") as fid:
        point1 = fid.readline().split()
        p1 = [float(point1[0]), float(point1[1])]
        point2 = fid.readline().split()
        p2 = [float(point2[0]), float(point2[1])]
        w = float(fid.readline())

    #Xmin = min(p1[0], p2[0])
    #Xmax = max(p1[0], p2[0])
    #Ymin = min(p1[1], p2[1])
    #Ymax = max(p1[1], p2[1])

    #center point
    c = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2]              
    #distance between points
    d = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**(0.5)    
    #theta to positive Xaxis
    theta = math.atan((p1[1] - p2[1])/(p1[0] - p2[0]))      
    sin = math.sin(-theta)
    cos = math.cos(-theta)
    #xaxis will be the axis the points lie on
    xaxis = ((0.5*d)**2 + (0.5*w)**2)**(0.5) 
    yaxis = w/2
    
    for loc in locs:
        #transform Global Coordinates to local coordinates
        X = loc.x - c[0]
        Y = loc.y - c[1]
        x = cos*X - sin*Y
        y = sin*X + cos*Y

        if x**2/xaxis**2 + y**2/yaxis**2 >= 1:
            locs.remove(loc)
    return locs

def _write_record(fid, key, description, data):
    """
    Write out station metadata and locations to fid from
    ``data.stations[key]``. ``nout``, ``touts``, ``toutf``, nspool`` are left
    unchanged from line.
        
    :param fid: :class:``file`` object
    :param string key: ADCIRC Output File Type sans ``.``
    :param line: array of parameters read from ``fort.15`` file
    :type line: :class:``np.array``
    :param data: object to store mesh specific data
    :type data: :class:``~polyadcirc.run_framework.domain`` or similar object

    """
    fid.write(' {:<35} {}{}'.format(len(data.stations[key]), '!',
                                    description))
    for loc in data.stations[key]:
        fid.write('{:9.8E} {:9.8E}\n'.format(loc.x, loc.y))

def set_ihot(ihot, path=None):
    """
    Set the hot start parameter to ``ihot``

    :param int ihot: Hot start paramter, ``fort.##`` file to read hot start
        dtat from

    """
    if path == None:
        path = os.getcwd()

    tmp_name = path +"/temp.15"
    file_name = path +"/fort.15"

    with open(file_name, 'r') as fid_read, open(tmp_name, 'w') as fid_write:
        line = fid_read.readline()
        while line != '':
            if line.find('IHOT') >= 0:
                line = line.partition('!')
                fid_write.write(' {:<35d} {}{}'.format(ihot, '!', line[-1]))
            else:
                fid_write.write(line)
            line = fid_read.readline()
    # rename files
    os.rename(tmp_name, file_name)

def set_write_hot(nhstar, nhsinc, path=None):
    """
    Set the hot start file generation paramters to ``nhstar`` and ``nhsinc``

    :param int nhstar: Type of hot start file to write
    :param int nhsinc: Frequency in timesteps to write data out to the hotstart
        file

    """
    if path == None:
        path = os.getcwd()

    tmp_name = path +"/temp.15"
    file_name = path +"/fort.15"

    with open(file_name, 'r') as fid_read, open(tmp_name, 'w') as fid_write:
        line = fid_read.readline()
        while line != '':
            if line.find('NHSTAR') >= 0:
                line = line.partition('!')
                fid_write.write(' {:<1d} {:<35d} {}{}'.format(nhstar,
                                                              nhsinc, '!', 
                                                              line[-1]))
            else:
                fid_write.write(line)
            line = fid_read.readline()
    # rename files
    os.rename(tmp_name, file_name)

