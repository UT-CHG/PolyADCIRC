# Copyright (C) 2013 Lindley Graham

"""
This module is for the manipulation and creation of ``fort.19`` and
``fort.20`` files.
"""

import numpy as np
import os, math

def write_fort19(etiminc, esbin, file_name=None):
    """
    Write out a ``fort.19`` formatted file to ``file_name``

    neta = total number of elevation specified boundary nodes

    :type etiminc: :class:`numpy.array` of shape (neta,) 
    :param etimic: time increment (secs) between consecutive sets of
                    elevation specified bounadry condition values
    :type esbin: :class:`numpy.array` of shape (k, neta)
    :param esbin: elevation at specfied elevation nodes k

    .. seealso:: `ADCIRC <http://adcirc.org/home/documentation/users-manual-v50/input-file-descriptions/non-periodic-elevation-boundary-condition-file-fort-19/>`_ 
                Non-periodic Elevation Boundary Condition File
    """
    if file_name == None:
        file_name = os.path.join(os.getcwd(), 'fort.19')

    esbin = esbin.ravel()
    
    with open(file_name, 'w') as fid:
        fid.write(str(etiminc)+"      ")
        fid.write('! ETIMINC time increment (secs) \n')
        for k in esbin:
            fid.write('{:17.15f}\n'.format(k))

def sin_wave(t_start, t_finish, amplitude, nnodes, time, periods=.5, 
             shift=0, timinc=None):
    """
    Creates data for a sine wave for forcing over the simulation ``time``
    evert ``timinc``.
    
    :param float t_start: starting time of sine shaped wave in days
    :param float t_finish: ending time of the sine shaped wave in days
    :param float amplitude: amplitude of the sine shaped wave
    :param int nnodes: number of nodes for this BC
    :param time: container for information from the ``fort.15``
    :type time: :class:`~polyadcirc.pyADCIRC.basic.time`
    :param float periods: number of periods to include in the wave
    :param float shift: number of periods to shift the wave  
    :param int timinc: time increment (secs) between consecutive sets of data

    :rtype: tuple of (:class:`numpy.ndarray`, :class:`numpy.ndarray`, int)
    :returns: (times, values at times, timinc)

    """
    if timinc == None:
        timinc = time.dt * 450.0
    times = np.arange(time.statim*60*60*24.0, time.rnday*60*60*24.0+timinc,
                      float(timinc))
    t_start = 60*60*24.0*t_start
    t_finish = 60*60*24.0*t_finish
    freq = periods/(t_finish - t_start)
    
    def wave(t):
        """
        Internal method for defining a sine wave at time t
        """
        if t_start <= t <= t_finish:
            tt = t_finish-t
            return amplitude* math.sin(2*math.pi*(freq*tt + shift))
        else:
            return 0

    values = map(wave, times)
    nvalues = np.tile(values, (nnodes, 1))

    return (times, nvalues.transpose(), timinc)

def step_wave(t_start, t_finish, amplitude, nnodes, time, timinc=None):
    """
    Creates data for a square wave for forcing over the simulation ``time``
    evert ``timinc``.

    :param float t_start: starting time of sine shaped wave in days
    :param float t_finish: ending time of the step shaped wave in days
    :param float amplitude: amplitude of the step shaped wave
    :param int nnodes: number of nodes for this BC
    :param time: container for information from the ``fort.15``
    :type time: :class:`~polyadcirc.pyADCIRC.basic.time`
    :param int timinc: time increment (secs) between consecutive sets of data

    :rtype: tuple of (:class:`numpy.ndarray`, :class:`numpy.ndarray`, int)
    :returns: (times, values at times, timinc)

    """
    if timinc == None:
        timinc = time.dt * 450.0
    times = np.arange(time.statim*60*60*24.0, time.rnday*60*60*24.0+timinc,
                      float(timinc))
    t_start = 60*60*24.0*t_start
    t_finish = 60*60*24.0*t_finish
  
    def wave(t):
        """
        Internal method for defining a step function at time t
        """
        if t_start <= t <= t_finish:
            return amplitude
        else:
            return 0

    values = map(wave, times)
    nvalues = np.tile(values, (nnodes, 1))

    return (times, nvalues.transpose(), timinc)

def write_fort20(ftiminc, qnin, file_name=None):
    """
    Write out a ``fort.20`` formatted file to ``file_name``

    nflbn = total number of normal flow specified boundary nodes

    :type ftiminc: :class:`numpy.array` of shape (nflbn,) 
    :param ftiminc: time increment (secs) between consecutive sets of
                    normal flow specified bounadry condition values
    :type qnin: :class:`numpy.array` of shape (k, nflbn)
    :param qnin: normal flow/unit width at specified nomarl flow node k

    .. seealso:: `ADCIRC <http://adcirc.org/home/documentation/users-manual-v50/input-file-descriptions/non-periodic-normal-flow-boundary-condition-file-fort-20/>`_ 
                Non-periodic Normal Flow Boundary Condition File
    """
    if file_name == None:
        file_name = os.path.join(os.getcwd(), 'fort.20')
    qnin = qnin.ravel() 
    with open(file_name, 'w') as fid:
        fid.write(str(ftiminc)+"      ")
        fid.write('! FTIMINC time increment (secs) \n')
        for k in qnin:
            fid.write('{:17.15f}\n'.format(k))

