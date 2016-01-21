# Copyright (C) 2013 Lindley Graham

"""
This module :mod:`~polyadcirc.pyADCIRC.fort13_management` handles the
reading/writing of ``fort.13`` formatted files.
"""

import numpy as np
import os

def write_manningsn(fid, node, value):
    """
    Write out a formated node value line to fid

    :type fid: :class:`file`
    :param fid: the file object to be written to
    :type node: int
    :param node: the node number
    :type value: float
    :param value: the nodal value
    :rtype: string
    :return: formatted string for a line in a ``fort.13`` formatted file

    """
    return fid.write('{:<8d} {:17.15g}\n'.format(int(node), value))

def read_manningsn(fid):
    """
    Reads in a node value line from fid

    
    :type fid: :class:`file`
    :param fid: the file object to be read from we might want to re write this
        as the fromstring method returns an array :rtype: :class:`numpy.ndarray`
    :return: Returns an array([node, value])

    """
    return np.fromstring(fid.readline(), sep=' ')

def read_nodal_attr(data, path=None, file_name='fort.13', nums=None):
    """
    Load in nodal attributes from a ``*.13`` file (only does Manning's n for
    now) and return a dictonary (like a MATLAB struct) with these attributes).

    :type data: :class:`polyadcirc.run_framework.domain`
    :param data: the :class:`polyadcirc.run_framework.domain` to which the
        nodal attribute information will be added :type path: string or None
    :param path: the directory containing the ``fort.13`` to be read in
    :type file_name: string
    :param file_name: the name of the ``fort.13`` formatted file
    :param list nums: list of nodes to read

    :rtype: dict
    :return: dictionary of Manning's *n* values

    """
    # Determine how many non-default nodes exist
    # Read in nodal values (Manning's n) from fort.13
    if path == None:
        path = os.getcwd()
    full_file_name = os.path.join(path, file_name)

    
    flag = 0
    attribute_name_present = 0

    manningsn_values = dict()
    
    with open(full_file_name, 'r') as f:
        while flag == 0:
            # read in the default nodal attribute
            if attribute_name_present == 0:
                line = f.readline()
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 1
                    f.readline()
                    data.manningsn_default = float(f.readline().strip())
                    # set default nodal value
                    # THIS PART MIGHT NEED TO BE ALTERED
                    #for node in data.node.values():
                    #    node.manningsn = data.manningsn_default
            # read in the number of non-default valued nodes
            if attribute_name_present == 1:
                line = f.readline()
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 2
                    data.manningsn_num = int(f.readline().strip())
            # read in the non-default nodal values
            if attribute_name_present == 2:
                for i in xrange(data.manningsn_num):
                    a = read_manningsn(f)
                    if (nums == None) or (int(a[0]) in nums):
                        if data.node.has_key(int(a[0])):
                            data.node[int(a[0])].manningsn = a[1]
                        manningsn_values[int(a[0])] = a[1]
                flag = 1
    return manningsn_values

def read_default(data, path=None, file_name='fort.13'):
    """
    Read in default manningsn from a ``*.13`` file and update data accordingly

    :type data: :class:`polyadcirc.run_framework.domain`
    :param data: object in which to store default value
    :type path: string or None
    :param path: directory containing ``file_name``
    :param string file_name: file name
    :rtype: :class:`polyadcirc.run_framework.domain`
    :return: a reference to the :class:`polyadcirc.run_framework.domain` object
        containing the default value

    """
    if path == None:
        path = os.getcwd()
    full_file_name = os.path.join(path, file_name)
    
    flag = 0
    attribute_name_present = 0

    with open(full_file_name, 'r') as f:
        while flag == 0:
            # read in the default nodal attribute
            if attribute_name_present == 0:
                line = f.readline()
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 1
                    f.readline()
                    f.readline()
                    data.manningsn_default = float(f.readline().strip())
                    flag = 1 
    return data.manningsn_default

def read_node_num(path=None, file_name='fort.13'):
    """
    Read in the number of nodes in the mesh from a ``*.13`` file

    :type path: string or None
    :param path: directory containing ``file_name``
    :param string file_name: file name
    :rtype: int 
    :return: number of nodes in the mesh 

    """
    if path == None:
        path = os.getcwd()
    full_file_name = os.path.join(path, file_name)
    
    with open(full_file_name, 'r') as f:
        f.readline()
        node_num = int(f.readline().strip())
    return node_num 

def read_nodal_attr_dict(path=None, file_name='fort.13'):
    """
    Load in nodal attributes from a ``*.13 file`` (only does Manning's n for
    now) and return a dictonary (like a ``MATLAB`` struct) with these
    attributes).

    :type path: string or None
    :param path: the directory containing the ``fort.13`` to be read in
    :type file_name: string
    :param file_name: the name of the ``fort.13`` formatted file
    :rtype: dict
    :return: dictionary of Manning's *n* 

    """
    # Determine how many non-default nodes exist
    # Read in nodal values (Manning's n) from fort.13
    if path == None:
        path = os.getcwd()
    full_file_name = os.path.join(path, file_name)
    
    flag = 0
    attribute_name_present = 0

    manningsn_values = dict()
    
    with open(full_file_name, 'r') as f:
        while flag == 0:
            # read in the default nodal attribute
            if attribute_name_present == 0:
                line = f.readline()
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 1
            # read in the number of non-default valued nodes
            if attribute_name_present == 1:
                line = f.readline()
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 2
                    manningsn_num = int(f.readline().strip())
            # read in the non-default nodal values
            if attribute_name_present == 2:
                for i in xrange(manningsn_num):
                    a = read_manningsn(f)
                    manningsn_values[int(a[0])] = a[1]
                flag = 1
    return manningsn_values

def update_mann(data, path=None, default=None, file_name='fort.13'):
    """
    Write out ``fort.13`` to path with the attributes contained in Data.  
    
    :type data: :class:`numpy.ndarray` or :class:`dict`
    :param data: containing the nodal attribute information
    :type path: string or None
    :param path: the directory to which the fort.13 file will be written
    :type default: None or float
    :param default: default value
    :type file_name: string
    :param file_name: the name of the ``fort.13`` formatted file
    
    """
    if path == None:
        path = os.getcwd()
    
    tmp_name = os.path.join(path, 'temp.13')
    file_name = os.path.join(path, file_name)

    # this currently uses the present fort.13 file as a template for formatting
    # purposes

    flag = 0
    attribute_name_present = 0
    
    with open(file_name, 'r') as fid_read, open(tmp_name, 'w') as fid_write:
        while flag == 0:
            # read in and write out default nodal value(s)
            if attribute_name_present == 0:
                line = fid_read.readline()
                fid_write.write(line)
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 1
                    fid_write.write(fid_read.readline())
                    fid_write.write(fid_read.readline())
                    if default:
                        fid_read.readline()
                        # write out the default nodal value
                        fid_write.write('{:f}\n'.format(default))
                    else:
                        fid_write.write(fid_read.readline())
            # read in and write out the number of non-default valued nodes
            if attribute_name_present == 1:
                line = fid_read.readline()
                fid_write.write(line)
                if line.find('mannings_n_at_sea_floor') >= 0:
                    attribute_name_present = 2
                    org_non_default = int(fid_read.readline().strip())
                    fid_write.write('{:d}\n'.format(len(data)))
            # read in and write out the non-default nodal values
            if attribute_name_present == 2:
                for i in xrange(org_non_default):
                    fid_read.readline()
                if type(data) == np.ndarray or type(data) == np.array:
                    for k, v in enumerate(data):
                        write_manningsn(fid_write, k+1, v)
                else:
                    for k, v in sorted(data.iteritems()):
                        write_manningsn(fid_write, k, v)
                flag = 1
        # write out remainder of fid_read to fid_write
        for line in fid_read:
            fid_write.write(line)
    # rename files
    os.rename(tmp_name, file_name)



