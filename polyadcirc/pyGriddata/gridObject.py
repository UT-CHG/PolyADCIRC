"""
This module contains the class definition for
:class:`~polyadcirc.mesh_mapping.gridInfo`.
"""

import os, stat
from polyadcirc.pyADCIRC.basic import pickleable
import polyadcirc.pyADCIRC.convert_fort14_to_fort13 as c13

class gridInfo(pickleable):
    """
    This class contains references to the ``fort.14``, ``*.asc``, and
    ``*.table`` files specific to a particular grid.
    """
    def __init__(self, file_name, gap_data_list):
        """ 
        Initalizes a gridInfo object with the information
        necessary for a ``*.14`` file with name ``file_name``, where
        ``gap_data_list`` is a list of
        :class:``~polyadcirc.mesh_mapping.table_management.gapInfo` objects 
        """
        self.file_name = file_name #: Name of grid file, ``*.14``
        self.gap_data_files = gap_data_list 
        """ list() of :class:`~polsim.table_management.gapInfo` objects """
        self.__landclasses = [] 
        self.__unique_tables = {} 
        for gap in self.gap_data_files:
            #: dict() of unique ``*.table`` files used
            self.__unique_tables[gap.table.file_name] = gap.table
        for k, v in self.__unique_tables.iteritems():
            for x in v.get_landclasses():
            #: list of landclasses used by this grid
                self.__landclasses.append((x, k))
        super(gridInfo, self).__init__()

    def __str__(self):
        """ 
        :rtype: string
        :returns: Return string that matches header and following relevants lines of
            ``*.in`` file
        """
        string_rep = self.__iter_string(self)
        return string_rep

    def __iter_string(self, i = 0, folder_name = ''):
        """ 
        Return string that matches header and following relevant lines of
        ``*.in`` file assuming :program:`Griddata_v1.32.F90` has been run ``i``
        times

        :param int i: number of times :program:`Griddata_v1.32.F90` has been
            run
        :param string folder_name: name of the folder where input files for
            this run of :program:`Griddata_v1.32.F90` are located
        :rtype: string
        :returns: Return string that matches header and following relevants lines of
            ``*.in`` file

        """
        string_rep = ''
        string_rep += "FOR BEST RESULTS, PLEASE KEEP COMMENTS OUT OF"
        string_rep += " THE FIRST 80 CHARACTERS ON EACH LINE.\n"
        string_rep += "123456789012345678901234567890123456789012345"
        string_rep += "67890123456789012345678901234567890\n"
        string_rep += "{0:80}! Database type: Lattice (1), ".format('1')
        string_rep += "Unstructured (2), Smoothing (3)\n"
        string_rep += "{0:80}! Select mode: Bathy. LIDAR (1), ".format('5')
        string_rep += "Bathy. GAP (2), "
        string_rep += " Bathy. USCR (3), Bathy. ETOPO (4), Mannings n GAP (5)\n"
        string_rep += "{0:80}! Map the data to: ".format('1')
        string_rep += "1-value-per-node (1), "
        string_rep += "12-values-per-node (2)\n"
        iter_name = folder_name+'/'
        iter_name += self.file_name[:-3]+i*'5'+self.file_name[-3:]
        string_rep += "{0:80}! Name of grid file.\n".format(iter_name)
        return string_rep

    def create_griddata_input_files(self, folder_name = None):
        """ 
        Creates a series of ``*.in`` files named in order to be run
        by :program:`./Griddata_parallel -I griddata_##.in`

        :param string folder_name: folder for which to create input files

        """
        if folder_name == None:
            folder_name = os.getcwd()
            for i, x in enumerate(self.gap_data_files):
                file_name = folder_name+'/griddata_'+str(i)+'.in'
                with open(file_name,'w') as f:
                    f.write(self.__iter_string(i))
                    f.write(str(x))
        else:
            for i, x in enumerate(self.gap_data_files):
                file_name = folder_name+'/griddata_'+str(i)+'.in'
                with open(file_name,'w') as f:
                    f.write(self.__iter_string(i, folder_name))
                    f.write(x.local_str(folder_name))

    def create_bash_script(self, folder_name = None):
        """
        Creates bash script called grid_file.sh to run Griddata in order on all
        the ``*.in`` file associated with this grid

        :param string folder_name: folder for which to create bash scripts

        """
        file_name = ''
        if folder_name == None:
            folder_name = os.getcwd()
            script_name = 'grid_all_'+self.file_name[:-2]+'sh'
        else:
            file_name += folder_name +'/'
            script_name = 'grid_all_'+folder_name+'_'+self.file_name[:-2]+'sh'
        with open(script_name,'w') as f:
            f.write('#!/bin/bash\n')
            f.write('# This script runs Griddata on several input files\n')
            for i in xrange(len(self.gap_data_files)):
                input_name = file_name + 'griddata_'+str(i)+'.in' 
                f.write('./Griddata_parallel.out -I '+input_name+'\n')
            #f.write('\n\n')
        curr_stat = os.stat(script_name)
        os.chmod(script_name, curr_stat.st_mode | stat.S_IXUSR)
        return script_name

    def get_dict_of_unique_tables(self):
        """
        :rtype: :class:`dict`
        :returns: a dict of all the unqiue ``*.table`` files required by
            ``grid_all_*.sh`` where unique_tables.keys() = ``table_file_name``,
            and unique_tables.values() = 
            :class:`~polyadcirc.mesh_mapping.table_management.tableInfo` object
        """
        return self.__unique_tables
        
    def get_landclasses(self):
        """
        :rtype: :class:`list`
        :returns: landclasses[i] = (class_num, table_file_name)
        """
        return self.__landclasses
            
    def setup_tables_single_value(self, class_num, manningsn_value,
                                  folder_name = None):
        """ 
        Creates a ``*.table`` in ``folder_name`` for ``t_name``.
        The land classification with ``t_class_number`` in ``t_name`` is 
        assigned a value of ``manningsn_value`` and all other landuse
        classifications are assigned a ``manningsn_value`` of 0

        :param int class_num: land classification number
        :param float manningsn_value: Manning's *n* value
        :param string folder_name: name of the folder to create table in

        """
        t_name = self.__landclasses[class_num][1]
        t_class_number = self.__landclasses[class_num][0]
        u_table = self.__unique_tables[t_name]
        u_table.create_table_single_value(t_class_number,  manningsn_value,
                                          folder_name)

    def setup_tables(self, folder_name = None):
        """
        Creates a ``*.table`` in ``folder_name`` for each unqiue ``*.table`` 
        file required by ``grid_all_*.sh``

        :param string folder_name: name of the folder to create table in
        
        """
        for x in self.__unique_tables.itervalues():
            x.create_table(folder_name)

    def convert(self, folder_name = None, keep_flags = 0):
        """ 
        
        :meth:`~polyadcirc.pyADCIRC.convert_fort14_to_fort13.convert` where ``source`` is
        the final ``*.14`` file produced by the bash script associated with
        ``self`` in ``folder_name``

        :param string folder_name: name of the folder containing the ``*.14``
            to be converted
        
        See :meth:`~polyadcirc.pyADCIRC.convert_fort14_to_fort13.convert`
        """
        if folder_name == None:
            folder_name = os.getcwd()
        c13.convert_go(self, folder_name, keep_flags)
