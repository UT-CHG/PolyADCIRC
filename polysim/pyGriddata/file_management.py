"""
This module handles the setting up of landuse classfication folders, bash
scripts, and the cleaning of these folders after :program:`Griddata_v1.32.F90`
has been run in each of the folders.
"""

import glob, os
import shutil as sh
import polysim.pyADCIRC.fort14_management as f14

def setup_landuse_folders(grid_object, create_all=True):
    """ 
    Set up landuse folders by copying all necessary files to run
    grid_all_data into the folder. One folder is created for each
    landuse classification. 

    If create_all is True then sets up num_landuse folders.
    Else sets up num_landuse-1 folders.

    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being mapped
    :param boolean create_all: flag to not skip first folder
    :rtype: list()
    :returns: list of file names of bash scripts for each land class

    """
    
    print 'Setting up a single set of landuse folders...'
    list_of_landuse_classes = grid_object.get_landclasses()
    script_list = []
    if create_all:
        for i in xrange(len(list_of_landuse_classes)):
            script_list.append(setup_landuse_folder(i, grid_object))
    else:
        for i in xrange(1, len(list_of_landuse_classes)):
            script_list.append(setup_landuse_folder(i, grid_object))
    return script_list

def setup_landuse_folders_double(grid_object, create_all=True):
    """ 
    Set up landuse folders by copying all necessary files to run
    grid_all_data into the folder. Two folders are created for each
    landuse classification. 

    If create_all is True then sets up num_landuse*2 folders.
    Else sets up (num_landuse-1)*2 folders.
    
    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being mapped
    :param boolean create_all: flag to not skip first folder
    :rtype: list()
    :returns: list of file names of bash scripts for each land class

    """
    
    print 'Setting up a double set of landuse folders...'
    list_of_landuse_classes = grid_object.get_landclasses()
    script_list = []
    if create_all:
        for i in xrange(len(list_of_landuse_classes)):
            sh_names = setup_landuse_folder_double(i, grid_object)
            for x in sh_names:
                script_list.append(x)
    else:
        setup_landuse_folder(0, grid_object, 0.1,

                'landuse_00_2')
        for i in xrange(1, len(list_of_landuse_classes)):
            sh_names = setup_landuse_folder_double(i, grid_object)
            for x in sh_names:
                script_list.append(x)
    return script_list

def setup_landuse_folder(class_num, grid_object, manningsn_value=1,
        folder_name=None):
    """ 
    Set up a single landuse with name landuse_class_num
    
    :param int class_num: land classification number for this folder
    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being mapped
    :param int manningsn_value: Manning's *n* value for this land
        classification
    :param string folder_name: folder name
    :rtype: string
    :returns: file name of bash script for this land class

    """
    if folder_name == None:
        folder_name = 'landuse_'+'{:=02d}'.format(class_num)
    print 'Setting up folder -- '+folder_name+'...'
    # create a folder for this land-use classification
    mkdir(folder_name)
    # cp grid_object.file_name folder_name
    copy(grid_object.file_name, folder_name)
    # *.asc and *.binary files are only kept in ./ for this project 
    # create *.in files
    grid_object.create_griddata_input_files(folder_name)
    # create *.sh files
    script_name = grid_object.create_bash_script(folder_name)
    # create the *.table file needed for grid_all_data
    grid_object.setup_tables_single_value(class_num, manningsn_value,
            folder_name)
    return script_name

def setup_folder(grid_object, folder_name = 'temp'):
    """ 
    Set up a single folder with name folder_name 

    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being mapped
    :param string folder_name: folder name
    :rtype: string
    :returns: file name of bash script for this land class

    """
    print 'Setting up folder -- '+folder_name+'...'
    # create a folder for this land-use classification
    mkdir(folder_name)
    # cp grid_object.file_name folder_name
    copy(grid_object.file_name, folder_name)
    # *.asc and *.binary files are only kept in ./ for this project 
    # create *.in files
    grid_object.create_griddata_input_files(folder_name)
    # create *.sh files
    script_name = grid_object.create_bash_script(folder_name)
    # create the *.table file needed for grid_all_data
    grid_object.setup_tables(folder_name)
    return script_name

def setup_landuse_folder_double(class_num, grid_object):
    """ 
    Set up two landuse folders with names:
    landuse_class_num_00
    landuse_class_num_01

    :param int class_num: land classification number for this folder
    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being mapped
    :rtype: list() of strings
    :returns: files name of bash scripts for this land class

    """
    script_list = [setup_landuse_folder(class_num, grid_object, 0.1,
        'landuse_'+str(class_num)+'_00')]
    script_list.append(setup_landuse_folder(class_num, grid_object, 1,
        'landuse_'+str(class_num)+'_01'))
    return script_list

def cleanup_landuse_folder(grid_object, folder_name=None):
    """ 
    
    Removes all files in folder_name(or current directory) except *.table
    and the most recent ``*.14``
    
    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being cleaned
    :param string folder_name: path to folder to clean up

    """
    if folder_name == None:
        folder_name = ''
        print 'Cleaning current directory...'
    else:
        print 'Cleaning '+folder_name+'...'
    file_list = glob.glob(folder_name+'/*')
    fort13_files = glob.glob(folder_name+'/*.13')
    table_files = glob.glob(folder_name+'/*.table')
    f14_files = f14.clean(grid_object, folder_name)
    if f14_files:
        for x in f14_files:
            file_list.remove(x)
    for x in fort13_files:
        file_list.remove(x)
    for x in table_files:
        file_list.remove(x)
    for x in file_list:
        os.remove(x)   
    grid_object.convert(folder_name)

def cleanup_landuse_folders(grid_object):
    """ 
    Removes all files except ``*.table`` and the most recent ``*.14`` in all
    landuse folders in the current directory

    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being cleaned

    """
    print 'Cleaning all landuse folders...'
    landuse_folder_names = glob.glob('landuse_*')
    for x in landuse_folder_names:
        cleanup_landuse_folder(grid_object, x)

def clean(grid_object, folder_name = None):
    """ 
    
    Removes all ``*.sh``, ``*.in``, all landuse folders, and all except for the
    most recent ``*.14`` files in the current working directory

    This currently doesn't work correctly for removing directories...

    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which landclasses are being cleaned 
    :param string folder_name: path to folder to clean up

    """
    files = glob.glob('grid_all*'+grid_object.file_name[:-3]+'*')
    files += glob.glob('*.in')
    folders =  glob.glob('landuse_*')
    for x in files:
        os.remove(x)
    for x in folders:
        os.removedirs(x)
    f14.clean(grid_object, folder_name)

def convert(grid_object, keep_flags = 0):
    """ Converts the final ``fort5...5.14`` file to a ``fort.13`` file for
    ``grid_object``

    :type grid_object: :class:`~polysim.mesh_mapping.gridObject.gridInfo`
    :param grid_object: grid for which ``*.14`` files are being converted
    :param int keep_flags: flag for types of conversion

    See :meth:`~polysim.mesh_mapping.gridInfo.convert`

    """
    print 'Converting fort.14 files...'
    landuse_folder_names = glob.glob('landuse_*')
    for x in landuse_folder_names:
        grid_object.convert(x, keep_flags)

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

def rename13(dirs = None):
    """
    Renames all ``*.13`` files in ``dirs`` to ``fort.13``

    :param list() dirs: list of directory names

    """
    files = []
    if dirs == None:
        files = glob.glob('landuse_*/*.13')
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
            shutil.rmtree(file)
        elif os.path.isfile(file):
            os.remove(file)
