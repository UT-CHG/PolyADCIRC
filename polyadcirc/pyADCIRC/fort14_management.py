# Copyright (C) 2013 Lindley Graham

"""
This module, :mod:`~polyadcirc.pyADCIRC.fort14_management` handles the
reading/writing of ``fort.14`` formatted files.
"""

import numpy as np
import glob, os
import polyadcirc.pyADCIRC.flag_fort14 as flag_fort14
import polyadcirc.pyADCIRC.basic as basic

def clean(grid_object, folder_name=None):
    """
    Removes all except for the most recent ``*.14`` files in ``folder_name`` or 
    the current working direcory

    :param grid_object: :class:`~polyadcirc.pyGriddata.gridObject.gridInfo`
    :param string folder_name: folder to clean
    :rtype: list
    :return: list of ``fort.14`` files in ``folder_name``

    """
    if folder_name == None:
        folder_name = ''
        print 'Removing extra *.14 files in current directory...'
    else:
        print 'Removing extra *.14 files in '+folder_name+'...'
    fort_14_files = glob.glob(os.path.join(folder_name,\
                    '*'+grid_object.file_name[:-3]+'*.14'))
    fort_14_files.sort()
    fort_14_files.reverse()
    for fid in fort_14_files[1:]:
        os.remove(fid)
    return fort_14_files

def flag(grid_file_name="fort.14", avg_scheme=2):
    """ 
    Modifiy ``grid_file_name`` so that all of the nodes are flagged
    appropriately for Griddata program and save to ``flagged_grid_file_name``.
 
    :param string grid_file_name: name of ``fort.14`` formatted file
    :param int avg_scheme: averaging scheme flag

    See :meth:`~polyadcirc.pyADCIRC.flag_fort14.flag_fort14`
    """
    flag_fort14.flag_fort14(grid_file_name, avg_scheme)

def flag_go(grid, avg_scheme=2):
    """ Given a gridInfo object create a flagged version of the
    ``grid.file_name[8:]`` and save to ``grid.file_name``

    :param grid: :class:`gridInfo`
    :param int avg_scheme: averaging scheme flag

    See :meth:`~polyadcirc.pyADCIRC.flag_fort14.flag_fort14`
    
    :rtype: string
    :returns: flagged file name

    """
    return flag_fort14.flag_fort14_go(grid, avg_scheme)

def is_flagged(grid):
    """
    :param grid: :class:`gridInfo`
    :rtype: bool
    :returns: true if flagged_grid_file_name exists and false if it doesn't
        exist

    """
    if glob.glob(grid.file_name):
        return True
    else:
        return False

def read_spatial_grid(data, path=None, make_domain_map=False):
    """ 
    Reads in a ``fort.14`` file in ``path`` and updates data

    :type data: :class:`polyadcirc.run_framework.domain`
    :param data: python object to save the ``fort.14`` data to
    :type path: string or None
    :param path: path to the``fort.14`` fortmatted file
    :type make_domain_map: bool
    :param make_domain_map: flag for whether or not to make a node to element
                            map
    :returns: reference to data

    """
    if path == None:
        path = os.getcwd()

    file_name = os.path.join(path, 'fort.14')

    with open(file_name, 'r') as f:
        f.readline()
        # Read in total number of nodes (OUT of fort.14 instead of fort.16 as
        # in serial case)
        a = np.fromstring(f.readline(), dtype=int, sep=' ')
        data.node_num = a[1]
        data.element_num = a[0]
        data.make_domain_map = make_domain_map
        
        # Now read in the nodal coordinates
        for i in xrange(data.node_num): # pylint: disable=W0612
            a = np.fromstring(f.readline(), sep=' ')
            data.node[int(a[0])] = basic.node(a[1], a[2], a[3])
        
        # Node read in the element to node map
        for i in xrange(data.element_num):
            a = np.fromstring(f.readline(), dtype=int,
                              sep=' ')
            data.element[a[0]] = a[2:]

    # This needs only to be done once then, make_domain_map flag will be set to
    # true, this also only needs to be done if we're dealing with subdomains
    if data.make_domain_map:
        data.make_node_to_element_map()            
        data.make_domain_map = False
        print 'Domain map construction complete'
    return data

def read_spatial_grid_header(data, path=None):
    """ 
    Reads in the the number of nodes and elements from the ``fort.14`` file in
    ``path`` and updates data

    :type data: :class:`polyadcirc.run_framework.domain`
    :param data: python object to save the ``fort.14`` data to
    :type path: string or None
    :param path: path to the``fort.14`` fortmatted file
    :returns: reference to data

    """
    if path == None:
        path = os.getcwd()

    file_name = os.path.join(path, 'fort.14')

    with open(file_name, 'r') as f:
        f.readline()
        # Read in total number of nodes (OUT of fort.14 instead of fort.16 as
        # in serial case)
        a = np.fromstring(f.readline(), dtype=int, sep=' ')
        data.node_num = a[1]
        data.element_num = a[0]
        
    return data

def update(data, bathymetry=None, path=None, file_name='fort.14'):
    """
    Write out bathymetry in data to ``fort.14`` formated file, by updating
    path/file_name accordingly

    :type data: :class:`polyadcirc.run_framework.domain`
    :param data: python object to save the ``fort.14`` data to
    :type bathymetry: array or None
    :param bathymetry: if None then use the bathymetry in ``data``
    :type path: string or None
    :param path: path to the``fort.14`` fortmatted file
    :param string  file_name: file name

    """
    if path == None:
        path = os.getcwd()

    file_name = os.path.join(path, file_name)
    tmp = os.path.join(path, 'temp.14')

    # this currrently uses the present fort.14 as a template for formatting
    # purposes
    if bathymetry == None:
        bathymetry = data.array_bathymetry()
    
    # pylint: disable=C0103
    with open(file_name, 'r') as f, open(tmp, 'w') as fw:
        fw.write(f.readline())
        fw.write(f.readline())
        for i, v in data.node.iteritems():
            # pylint: disable=C0103
            fw.write('{:<7d} {:9.8E} {:9.8E} {:7.2f}\n'.format(i, v.x, v.y,
                                                               bathymetry[i-1]))
            f.readline()
        for line in f:
            fw.write(line)
    os.rename(tmp, file_name)






