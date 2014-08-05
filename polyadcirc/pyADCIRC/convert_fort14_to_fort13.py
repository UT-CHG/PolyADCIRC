# Lindley Graham 03/25/2013
"""
A set of methods for converting a fort.14 formatted file to a fort.13 formatted file
"""

import re, os, glob
import numpy as np
from polysim.pyADCIRC.fort13_management import write_manningsn, read_manningsn

class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self):
        super(Error, self).__init__()

class InputError(Error):
    """
    Exception raised for errors in the input.
    """

    def __init__(self, expr, msg):
        """
        :param expr: input expression in which the error occurred
        :param msg: explanation of the error

        """
        self.expr = expr
        self.msg = msg
        super(InputError, self).__init__()

def convert(source, keep_flags = 0, target = 'fort.13'):
    """ Reads in a ``fort5...14`` file and produces a ``fort5...13 file``. By
    default all remaining flagged nodes are removed. If the user desires to
    keep the flagged nodes, keep_flags should be set to 1.
    
    :param string source: the ``fort5...14`` file name, this is used to
        determine the nodal manningsn values 
    :param string target: the ``fort.13`` files, this is used to determine 
        the default manningsn value and relevant header information
    :param int keep_flags:
        0. ``_noflags`` -- creates a ``fort.13`` formatted file and removes
           remaining flags for Griddata
        1. ``_flags`` -- creates a ``fort.13`` formatted file with remainings flags
           for Griddata intact
        2. _fillins -- creates a ``fort.13`` formatted file and fills in remiaing
           flags from Griddata with data from source if data is present
        3. _color -- creates a ``fort.13`` formatted file and color codes the data
           based on wheter or not is is a default value or not

    """
    output_name = source[:-3]
    if keep_flags == 0:
        output_name += '_noflags.13'
    elif keep_flags == 1:
        output_name += '_flags.13'
    elif keep_flags == 2:
        output_name += '_fillins.13'
    elif keep_flags == 3:
        output_name += '_color.13'
    else:
        print keep_flags
        msg = 'Not a valid keep_flags value.\n'
        msg += '0: creates fort.13 formatted file and removes remaining flags'
        msg += 'for Griddata\n'
        msg += '1: creates fort.13 formatted file with remaining'
        msg += 'flags for Griddata intact\n'
        msg += '2: creates fort.13 formatted file and fills in remaning flags'
        msg += 'from Griddata  with data from source if data is present\n'
        msg += '3: creates fort.13 formatted file and color codes the data '
        msg += 'based on whether or not it is a default value or not\n'
        raise InputError('keep_flags', msg)

    temp_name = source[:-3]+'_body.13'

    # read in nodal manningsn values
    # if keep_flags then copy header from fort.13 (replacing number of
    # non-default values with total number of node in subheader) and read/write
    # all nodes to body
    step = 1
    flag = 0
    attribute_name_present = 0

    with open(source, 'r') as fid_read514, open(output_name, 
            'w') as fid_write, open(target, 'r') as fid_read:
        fid_read514.readline()
        while flag == 0:
            # read in and write out default nodal value(s)
            if attribute_name_present == 0:
                line = fid_read.readline()
                fid_write.write(line)
                tline_indice = re.match(r"mannings_n_at_sea_floor",
                                        line.strip()) 
                if tline_indice != None:
                    attribute_name_present = 1
                    fid_write.write(fid_read.readline())
                    fid_write.write(fid_read.readline())
                    fid_write.write(fid_read.readline())
           # read in total number of nodes and write partial header
            if attribute_name_present == 1:
                line = fid_read.readline()
                fid_write.write(line)
                tline_indice = re.match(r"mannings_n_at_sea_floor",
                                        line.strip())
                if tline_indice != None:
                    # read the original number of non-default values in
                    # the fort.13
                    attr_num = np.fromstring(fid_read.readline(), dtype = int,
                                             sep = ' ')
                    attribute_name_present = 2
                    tmp = np.fromstring(fid_read514.readline(), dtype = int,
                                        sep = ' ')
                    node_num = tmp[1]
                    read_target_nodes = 0

                    if keep_flags == 1:
                        # write out the number of non-default nodes
                        fid_write.write('{:d}\n'.format(node_num))
                    elif keep_flags == 2:
                        # read in and write out the non-default values while
                        # keeping track of missing values
                        missing_val = 0
                        for i in xrange(node_num): # pylint: disable=W0612
                            a = read_manningsn(fid_read514)
                            b = read_manningsn(fid_read)
                            read_target_nodes += 1
                            # add a simple loop to keep in check
                            # with fid_read514
                            while read_target_nodes < attr_num and b[0]<a[0]:
                                b = read_manningsn(fid_read)
                                read_target_nodes += 1
                            if a[3] > 0:
                                write_manningsn(fid_write, a[0], a[4])
                            elif b and b[1] <= 0.022 and b[1] >= 0.012:
                                write_manningsn(fid_write, a[0], b[1])
                            else:
                                missing_val += 1
                        msg =  'Total number of missing values: '
                        print msg + str(missing_val)
                        # write out number of non-default valued nods
                        node_num = step-1
                        fid_write.write('{:d}\n'.format(node_num))
                    elif keep_flags == 0 or keep_flags == 3:
                        # readin the and write out the enon-default values to
                        # fid_body while keeping track of the number of
                        # non-default values
                        with open(temp_name, 'w') as fid_body:
                            for i in xrange(node_num):
                                a = read_manningsn(fid_read514)
                                if a[3] >= 0:
                                    if keep_flags == 0:
                                        write_manningsn(fid_body, a[0], a[3])
                                    elif keep_flags == 3:
                                        write_manningsn(fid_body, a[0], .19)
                                    step += 1
                            # write out number of non-default valued nodes
                            node_num = step-1
                            fid_write.write('{:d}\n'.format(node_num))
            if attribute_name_present == 2:
                if keep_flags == 1:
                    # read in and write out non-default values
                    for i in node_num:
                        a = read_manningsn(fid_read514)
                        write_manningsn(fid_write, a[0], a[3])
                elif keep_flags == 0 or keep_flags == 3 or keep_flags == 2:
                    # append fid_body to fid_write
                    with open(temp_name) as fid_body:
                        for line in fid_body:
                            fid_write.write(line)
                    # now we are still at the end of fid_write
                if keep_flags != 2:
                    # read untilnext nodal attribute
                    for i in xrange(attr_num):
                        fid_read.readline()
                flag = 1
        # finished writing modified portions of fort.13
        # write out remainder of fid_read to fid_write
        for line in fid_read:
            fid_write.write(line)
    # files are now all closed and correctly named
    os.remove(temp_name)

def convert_go(grid, folder_name = None, keep_flags = 0):
    """ See :meth:`~polysim.pyADCIRC.convert_fort14_to_fort13.convert` where
    source is the final ``*.14`` file produced by the bash script associated
    with grid in folder_name

    :param grid: :class:`gridInfo` object
    :param string folder_name: folder containing the ``fort5...14 file``
    :param int keep_flags:
        0. ``_noflags`` -- creates a ``fort.13`` formatted file and removes
           remaining flags for Griddata
        1. ``_flags`` -- creates a ``fort.13`` formatted file with remainings flags
           for Griddata intact
        2. _fillins -- creates a ``fort.13`` formatted file and fills in remiaing
           flags from Griddata with data from source if data is present
        3. _color -- creates a ``fort.13`` formatted file and color codes the data
           based on wheter or not is is a default value or not

    """
    if folder_name == None:
        folder_name = os.getcwd()

    fort_14_files = glob.glob(folder_name+'/'+grid.file_name[:-3]+'5*.14')
    fort_14_files.sort()
    fort_14_files.reverse()
    source = fort_14_files[0]

    convert(source, keep_flags)
