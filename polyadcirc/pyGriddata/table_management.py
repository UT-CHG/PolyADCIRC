# Copyright (C) 2013 Lindley Graham

"""
This modules controls the management and creation of ``*.table`` files
"""

import glob, os, re
from polyadcirc.pyADCIRC.basic import pickleable

if __name__ == "__main__":
    pass

def create_table_single_value(class_num, landuse_table, manningsn_value,
                              folder_name=None):
    """ 
    Create a ``*.table`` in ``folder_name`` where the landuse classification
    numbered class_num is assigned a value of ``manningsn_value`` and all other
    landuse classifications are assigned a manningsn_value of 0

    :param int class_num: land classification number
    :type landuse_table: :class:`tableInfo`
    :param landuse_table: table to base the single value table off of
    :param float manningsn_value: Manningn's *n* value for ``class_num``
    :param string folder_name: folder to create the table in

    """
    new_values = landuse_table.land_classes.copy()
    for k in new_values.iterkeys():
        new_values[k] = 0
    new_values[class_num] = manningsn_value
    new_table = tableInfo(landuse_table.file_name, new_values)
    create_table(new_table, folder_name)

def create_table(landuse_table, folder_name=None):
    """ 
    Create ``table_name.table`` in ``folder_name`` where the landuse
    classification numbered ``landuse_table.keys()`` is assigned a
    ``manningsn_value`` of ``landuse_table['key']``
    
    :type landuse_table: :class:`tableInfo`
    :param landuse_table: table to create
    :param string folder_name: folder to create the table in

    """
    print 'Creating landuse_table file '+landuse_table.file_name+'...'
    if folder_name is None:
        folder_name = ''
    with open(os.path.join(folder_name, landuse_table.file_name), 'w') as f:
        next_str = ' {0:3}    ! '.format(landuse_table.get_num_landclasses())
        next_str += 'Total number of Class\n'
        f.write(next_str)
        for k, v in landuse_table.land_classes.iteritems():
            f.write('{0:3}    {1!r} :description\n'.format(k, v))
        f.write('The class has default value(=-9999) will be skiped in mapping')

def read_table(table_file_name, folder_name=None):
    """ 
    Read in ``table_file_name`` in ``folder_name`` 
   
    :param string table_file_name: local file name of table
    :param string folder_name: folder to read the table from
    
    :rtype: :class:`tableInfo`
    :returns: an object with all of the information in that table
    
    """ 
    print 'Reading landuse_table file '+table_file_name+'...'
    if folder_name is None:
        folder_name = os.getcwd()
    landuse_classes = {}
    with open(os.path.join(folder_name, table_file_name), 'r') as f:
        for line in f:
            m = re.match(r" +(\d+) +(\d+.\d+) +:(.*)", line)
            if m != None:
                landuse_classes[int(m.group(1))] = float(m.group(2))
    new_table = tableInfo(table_file_name, landuse_classes)
    return new_table

def read_tables(folder_name=None):
    """ 
    Read in all ``*.table`` files in folder_name and return a list of tableInfo
    objects
    
    :param string folder_name: folder to read the table(s) from

    :rtype: list of :class:`tableInfo`
    :returns: list of objects with all of the information in that table

    """
    if folder_name is None:
        folder_name = os.getcwd()
    list_of_tables = []
    list_of_table_names = glob.glob(os.path.join(folder_name, '*.table'))
    for x in list_of_table_names:
        x = x[len(folder_name)+1:]
        list_of_tables.append(read_table(x, folder_name))
    return list_of_tables

def create_gap_list_from_folder(table, folder_name):
    """
    Create a list() of :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
    objects from the files in folder.

    :param string folder_name: folder containing gap formatted files
    :rtype: list
    :returns: list of :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
        objects
    """
    gap_files = glob.glob(os.path.join(folder_name, '*.asc'))
    return create_gap_list(table, gap_files)
   
def create_gap_list(table, gap_files):
    """
    Create a list() of :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
    objects from a list of files.

    :param list gap_files: file names of gap formatted files
    :rtype: list
    :returns: list of :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
        objects
    """
    gap_list = []
    for f in gap_files:
        meta_filename = glob.glob(os.path.join(f.rpartition('/')[0], '*.txt'))
        with open(meta_filename[0], 'r') as meta_info:
            for line in meta_info:
                m = re.match(r"UTM map zone", line)
                if m != None:
                    UTM_zone = line.split()[-1]
                    break
        gap_list.append(gapInfo(f, table, 1, UTM_zone))
    return gap_list


class gapInfo(pickleable):
    """
    This object stores information specific to a GAP dataset, methods for
    creating it's portion of the ``*.in`` file, and methods for creating the
    table(s) needed for this GAP dataset.
    """
    def __init__(self, file_name, table, horizontal_sys=None, UTM_zone=None):
        """ 
        Initalizes a gapInfo object with the information necessary for a
        ``*.asc``,``*.asc.binary`` file with name ``file_name``
        """
        self.file_name = file_name #: Name of GAP/NLCD data file, ``*.asc``
        self.horizontal_sys = horizontal_sys 
        """ Horizontal system: (1) GRS80, (2) NAD83/WGS84, (3) WGS72"""
        self.UTM_zone = UTM_zone #: UTM Zone number of GAP/NLCD data.
        self.table = table #: :class:`tableInfo` object
        super(gapInfo, self).__init__()

    def __str__(self):
        """ 
        :rtype: string
        :returns: text that matches relevant lines of ``*.in`` file 
        """
        string_rep = ''
        string_rep += "{0:80}! Name of GAP/NLCD data file.\n".format(\
                self.file_name)
        string_rep += "{0:80}!".format(self.table.file_name)
        string_rep += " Name of classified value table.\n"
        convert = 'N'
        if glob.glob(self.file_name+'.binary') == []:
            convert = 'Y'
        elif glob.glob(self.file_name+'.binary') == []:
            convert = 'Y'
        string_rep += "{0:80}!".format(convert)
        string_rep += " Convert to ASCII GAP/NLCD data to "
        string_rep += "binary(required)? (Y/N)\n"
        if self.horizontal_sys != None:
            string_rep += "{0:80}!".format('Y')
            string_rep += " Convert grid to UTM coordinates(grid"
            string_rep += " required to be in UTM coordinates)? (Y/N)\n"
            string_rep += "{0:80}!".format(str(self.horizontal_sys))
            string_rep += " Select horizontal system: GRS80(1),"
            string_rep += " NAD83/WGS84 (2), WGS72 (3)\n"
            string_rep += "{0:80}! ".format(str(self.UTM_zone))
            string_rep += "UTM Zone number of GAP/NLCD data.\n\n"
        else:
            string_rep += "{0:80}!".format('N')
            string_rep += " Convert grid to UTM coordinates(grid"
            string_rep += " required to be in UTM coordinates)? (Y/N)\n\n"
        return string_rep

    def local_str(self, basis_dir, folder_name=None):
        """ 
        
        :param string basis_dir: the folder containing the ``*.asc`` files and
            the directory folder_name
        :param string folder_name: name of folder to create ``*.in`` for
    
        :rtype: string
        :returns: text that matches relevant lines of ``*.in`` file and uses
            basis_dir for ``*.asc`` files 
        
        """
        string_rep = ''
        string_rep += "{0:80}! Name of GAP/NLCD data file.\n".format(\
                self.file_name)
        if folder_name:
            table_name = os.path.join(folder_name, self.table.file_name)
        else:
            table_name = self.table.file_name
        string_rep += "{0:80}!".format(table_name)
        string_rep += " Name of classified value table.\n"
        convert = 'N'
        if glob.glob(os.path.join(basis_dir, self.file_name+'.binary')) == []:
            convert = 'Y'
        else:
            convert = 'N'
        string_rep += "{0:80}!".format(convert)
        string_rep += " Convert to ASCII GAP/NLCD data to "
        string_rep += "binary(required)? (Y/N)\n"
        if self.horizontal_sys != None:
            string_rep += "{0:80}!".format('Y')
            string_rep += " Convert grid to UTM coordinates(grid"
            string_rep += " required to be in UTM coordinates)? (Y/N)\n"
            string_rep += "{0:80}!".format(str(self.horizontal_sys))
            string_rep += " Select horizontal system: GRS80(1),"
            string_rep += " NAD83/WGS84 (2), WGS72 (3)\n"
            string_rep += "{0:80}! ".format(str(self.UTM_zone))
            string_rep += "UTM Zone number of GAP/NLCD data.\n\n"
        else:
            string_rep += "{0:80}!".format('N')
            string_rep += " Convert grid to UTM coordinates(grid"
            string_rep += " required to be in UTM coordinates)? (Y/N)\n\n"
        return string_rep

    def create_table_single_value(self, class_num, manningsn_value,
                                  folder_name=None):
        """ 
        Create a ``*.table`` in ``folder_name`` where the landuse classification
        numbered class_num is assigned a value of ``manningsn_value`` and all
        other landuse classifications are assigned a ``manningsn_value`` of 0.

        :param int class_num: land classification number
        :param float manningsn_value: Manningn's *n* value for `class_num`
        :param string folder_name: folder to create the table in

        """
        create_table_single_value(class_num, self.table, manningsn_value,
                                  folder_name)

    def create_table(self, folder_name=None):
        """ 
        Create ``self.table_name.table`` in`` folder_name`` where the landuse
        classification numbered ``landuse_table.keys()`` is assigned a
        ``manningsn_value`` of ``landuse_table['key']``.
        
        :param string folder_name: folder to create the table in

        """ 
        create_table(self.table, folder_name)

    def read_table(self, folder_name=None):
        """ 
        Read in ``self.table.file_name`` in ``folder_name`` 
       
        :param string folder_name: folder to read the table from
        :rtype: :class:`tableInfo`
        :returns: an object with all of the information in that table
        
        """ 
        return read_table(self.table.file_name, folder_name)

class tableInfo(pickleable):
    """
    This class stores the relation between Manning's *n* values and land class
    numbers.

    """
    def __init__(self, file_name, land_classes):
        """ Initializes a tableInfo object associated with file_name,
        containing all of the information in file_name
        """
        self.file_name = file_name 
        """ Name of classified value table, ``*.table`` """
        self.land_classes = land_classes 
        """ dict of land classification numbers and associated mannings_n
            values """
        super(tableInfo, self).__init__()

    def get_landclasses(self):
        """ 
        :rtype: list
        :returns: list of land_classes (integers)

        """
        return self.land_classes.keys()

    def get_num_landclasses(self):
        """ 
        :rtype int:
        :returns: total number of land_classes """
        return len(self.land_classes)

    def __str__(self):
        """
        :rtype string:
        :returns: file_name and the Python string rep of a dict
        
        """
        string_rep = self.file_name+'\n'
        string_rep += str(self.land_classes)
        return string_rep

    def create_table_single_value(self, class_num, manningsn_value,
                                  folder_name=None):
        """ 
        Create a ``*.table`` in ``folder_name`` where the landuse
        classification numbered class_num is assigned a value of
        ``manningsn_value`` and all other landuse classifications are assigned
        a manningsn_value of 0.

        :param int class_num: land classification number
        :param float manningsn_value: Manningn's *n* value for `class_num`
        :param string folder_name: folder to create the table in

        """
        create_table_single_value(class_num, self, manningsn_value,
                                  folder_name)
    
    def create_table(self, folder_name=None):
        """ 
        Create ``table_name.table`` in`` folder_name`` where the landuse
        classification numbered ``landuse_table.keys()`` is assigned a
        ``manningsn_value`` of ``landuse_table['key']``.
        
        :param string folder_name: folder to create the table in

        """         
        create_table(self, folder_name)

    def read_table(self, folder_name=None):
        """ 
        Read in ``self.file_name`` in ``folder_name`` .
       
        :param string folder_name: folder to read the table from
        :rtype: :class:`tableInfo`
        :returns: an object with all of the information in that table
        
        """ 
        return read_table(self.file_name, folder_name)
