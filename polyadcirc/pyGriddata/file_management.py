# Copyright (C) 2013 Lindley Graham

"""
This module handles the setting up of landuse classfication folders, bash
scripts, and the cleaning of these folders after :program:`Griddata_v1.32.F90`
has been run in each of the folders.
"""

import glob, os
import shutil as sh

def copy(src, dst):
    """ 
    If file !exists then copy src into dest

    :param string src: source file name
    :param string dst: destination file name

    """
    #if os.path.exists(dst+'/'+src) == False:
    sh.copy(src, dst)

def mkdir(path):
    """ 
    If path !exists then :meth:`os.makedirs`

    :param string path: path of directory to create

    """
    if not os.path.exists(path):
        os.makedirs(path)

def rename13(dirs=None, basis_dir=None):
    """
    Renames all ``*.13`` files in ``dirs`` to ``fort.13``

    :param list dirs: list of directory names

    """
    files = []
    if dirs is None and basis_dir is None:
        files = glob.glob(os.path.join('landuse_*', '*.13'))
    elif dirs is None and basis_dir:
        files = glob.glob(os.path.join(basis_dir, 'landuse_*', '*.13'))
    else:
        for d in dirs:
            files.append(glob.glob(os.path.join(basis_dir, d)+'/*.13')[0])
    for f in files:
        os.rename(f, os.path.join(os.path.dirname(f), 'fort.13'))

def remove(files):
    """
    Remover one or more files or directories
    
    :param string files: Path of files or directories to remove

    Created on Wed Jan 15 02:44:47 2014

    @author: pkjain

    """
    if isinstance(files, str): #is files a stringing
        files = [files]
    for f in files:
        if os.path.isdir(f):
            sh.rmtree(f)
        elif os.path.isfile(f):
            os.remove(f)

def symlink(src, dst, overwrite=1):
    """
    Creates a symbolic link pointing to src named dst. Overwrites existing
    links by default.

    :param string src: source
    :param string dst: destination
    :param binary overwrite: 0 - do not overwrite, 1 - overwrite links, 2 - 
        overwrite files and links, 3 - overwrite directories, files and links

    """
    if not os.path.lexists(dst):
        os.symlink(src, dst)
    elif overwrite > 0 and os.path.islink(dst):
        os.remove(dst)
        print "removing old link"
        os.symlink(src, dst)
    elif overwrite > 1 and os.path.isfile(dst):
        remove(dst)
        print "removing old file"
        os.symlink(src, dst)
    elif overwrite > 2 and os.path.isdir(dst):
        remove(dst)
        print "removing old directory"
        os.symlink(src, dst)
