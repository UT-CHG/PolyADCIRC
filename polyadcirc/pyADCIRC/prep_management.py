# Copyright (C) 2013 Lindley Graham

"""
This module controls the automatic writing of ``in.prep*`` files
"""

import os, stat

def prep_script_12(path):
    """
    Write out a bash scrip to run :program:`adcprep` with ``in.prep1`` and
    ``in.prep2`` and save it to path

    :param string path: folder to save ``prep12.sh`` to
    
    """
    with open(path+'/prep12.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('./adcprep < in.prep1 > prep_o.txt\n')
        f.write('./adcprep < in.prep2 > prep_o.txt\n')
    curr_stat = os.stat(path+'/prep12.sh')
    os.chmod(path+'/prep12.sh', curr_stat.st_mode | stat.S_IXUSR)

def prep_script_n(path, n):
    """
    Write out a bash scrip to run :program:`adcprep` with ``in.prepn`` and save
    it to path

    :param string path: folder to save ``prepn.sh`` to
    
    """
    with open(path+'/prep'+str(n)+'.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('./adcprep < in.prep'+str(n)+' > prep_o.txt\n')
    curr_stat = os.stat(path+'/prep'+str(n)+'.sh')
    os.chmod(path+'/prep'+str(n)+'.sh', curr_stat.st_mode | stat.S_IXUSR)

def write_1(path, nprocs=12, nfile="fort.14"):
    """
    Write out a ``in.prep1`` file for ``nfile`` and save it to path

    :param string path: folder to save ``in.prep1`` to
    :param int nprocs: number of processors a single :program:`PADCIRC` run
                       will be run on
    :param string nfile: name of ``fort.14`` formatted file

    """
    with open(path+'/in.prep1', 'w') as f:
        f.write(str(nprocs)+'\n')
        f.write('1 \n')
        f.write(nfile)

def write_2(path, nprocs=12): 
    """
    Write out a ``in.prep2`` file for ``nfile`` and save it to path

    :param string path: folder to save ``in.prep2`` to
    :param int nprocs: number of processors a single :program:`PADCIRC` run
                       will be run on

    """
    with open(path+'/in.prep2', 'w') as f:
        f.write(str(nprocs)+'\n')
        f.write('2')

def write_5(path, nprocs=12, nfile="fort.13"):
    """
    Write out a ``in.prep5`` file for ``nfile`` and save it to path

    :param string path: folder to save ``in.prep5`` to
    :param int nprocs: number of processors a single :program:`PADCIRC` run
                       will be run on
    :param string nfile: name of ``fort.13`` formatted file

    """
    with open(path+'/in.prep5', 'w') as f:
        f.write(str(nprocs)+'\n')
        f.write('5 \n')
        f.write(nfile)

def write_n(path, n, nprocs=12, nfile=None):
    """
    Write out a ``in.prepn`` file for ``nfile`` and save it to path

    :param string path: folder to save ``in.prepn`` to
    :param int n: number of the ``in.prepn`` file
    :param int nprocs: number of processors a single :program:`PADCIRC` run
                       will be run on
    :param string nfile: name of ``fort.nn`` formatted file

    """
    with open(path+'/in.prep'+n, 'w') as f:
        f.write(str(nprocs)+'\n')
        f.write(n+' \n')
        if nfile:
            f.write(nfile)


