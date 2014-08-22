"""
This module handles the setting up of landuse classfication folders, bash
scripts, and the cleaning of these folders after :program:`Griddata_v1.32.F90`
has been run in each of the folders.
"""

import glob, os
import shutil as sh
import polyadcirc.pyADCIRC.fort14_management as f14

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
    If path !exists then mkdir

    :param string path: path of directory to create

    """
    if os.path.exists(path) == False:
        os.mkdir(path)

def rename13(dirs = None, basis_dir=None):
    """
    Renames all ``*.13`` files in ``dirs`` to ``fort.13``

    :param list() dirs: list of directory names

    """
    files = []
    if dirs == None and basis_dir == None:
        files = glob.glob('landuse_*/*.13')
    elif dirs == None and basis_dir:
        files = glob.glob(basis_dir+'/landuse_*/*.13')
    else:
        for d in dirs:
            files.append(glob.glob(d+'/*.13')[0])
    for f in files:
        os.rename(f, f.split('/')[0]+'/fort.13')

def remove(files):
    """
    Remover one or more files or directories
    
    :param string files: Path of files or directories to remove

    Created on Wed Jan 15 02:44:47 2014

    @author: pkjain

    """
    if isinstance(files,str): #is files a string
        files = [files]
    if not isinstance(files,list):
        "Error"
    for file in files:
        if os.path.isdir(file):
            sh.rmtree(file)
        elif os.path.isfile(file):
            os.remove(file)
