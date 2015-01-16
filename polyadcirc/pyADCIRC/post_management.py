# Lindley Graham
"""
This module controls the automatic writing of ``in.post*`` files
"""

import os, stat

def post_script_sub(path):
    """
    Write out a bash scrip to run :program:`adcpost` with ``in.postsub`` and
    and save it to path

    :param string path: folder to save ``postsub.sh`` to
    
    """
    with open(path+'/postsub.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('./adcpost < in.postsub > post_o.txt\n')
    curr_stat = os.stat(path+'/postsub.sh')
    os.chmod(path+'/postsub.sh', curr_stat.st_mode | stat.S_IXUSR)

def post_script_ALL(path):
    """
    Write out a bash scrip to run :program:`adcpost` with ``in.postALL`` and
    and save it to path

    :param string path: folder to save ``postALL.sh`` to
    
    """
    with open(path+'/postALL.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('./adcpost < in.postALL > post_o.txt\n')
    curr_stat = os.stat(path+'/postALL.sh')
    os.chmod(path+'/postALL.sh', curr_stat.st_mode | stat.S_IXUSR)

def post_script_n(path, n):
    """
    Write out a bash scrip to run :program:`adcpost` with ``in.postn`` and save
    it to path

    :param string path: folder to save ``postn.sh`` to
    
    """
    with open(path+'/post'+str(n)+'.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('./adcpost < in.post'+str(n)+' > post_o.txt\n')
    curr_stat = os.stat(path+'/post'+str(n)+'.sh')
    os.chmod(path+'/post'+str(n)+'.sh', curr_stat.st_mode | stat.S_IXUSR)

def write_sub(path, hotfiles=False):
    """
    Write out a ``in.postsub`` file and save it to path

    :param string path: folder to save ``in.postsub`` to
    :param boolean hotfiles: flag whether or not to post process hot start
        files

    """
    with open(path+'/in.postsub', 'w') as f:
        f.write('post\n')
        f.write('1063\n')
        f.write('1064\n')
        f.write('999\n')
        if hotfiles:
            f.write('y\n')
        else:
            f.write('n\n')
        f.write('quit\n')

def write_n(path, n, hotfiles=False):
    """
    Write out a ``in.postn`` file and save it to path

    :param string path: folder to save ``in.postn`` to
    :param int n: ADCPOST file type code
    :param boolean hotfiles: flag whether or not to post process hot start
        files

    """
    with open(path+'/in.postsub', 'w') as f:
        f.write('post\n')
        f.write(str(n)+'\n')
        f.write('999\n')
        if hotfiles:
            f.write('y\n')
        else:
            f.write('n\n')
        f.write('quit\n')

def write_multi(path, nums, hotfiles=False):
    """
    Write out a ``in.postmulti`` file and save it to path

    :param string path: folder to save ``in.postn`` to
    :param list nums: list of ADCPOST file type codes
    :param boolean hotfiles: flag whether or not to post process hot start
        files

    """
    with open(path+'/in.postmulti', 'w') as f:
        f.write('post\n')
        for n in nums:
            f.write(str(n)+'\n')
        f.write('999\n')
        if hotfiles:
            f.write('y\n')
        else:
            f.write('n\n')
        f.write('quit\n')

def write_ALL(path, hotfiles=False):
    """
    Write out a ``in.postALL` file and save it to path

    :param string path: folder to save ``in.postALL`` to
    :param boolean hotfiles: flag whether or not to post process hot start
        files

    """
    with open(path+'/in.postALL', 'w') as f:
        f.write('post\n')
        f.write('100\n')
        if hotfiles:
            f.write('y\n')
        else:
            f.write('n\n')
        f.write('quit\n')



