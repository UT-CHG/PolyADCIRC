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
        self.d
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

    def prep_all(grid, flag = 1, basis_dir = None):
        """
        Assumes that all the necessary input files are in ``path``. Given a
        :class:`~polyadcirc.pyGriddata.gridInfo` object this function generates a
        ``landuse_##`` folder for every land classification number containing a
        ``fort.13`` file specific to that land classification number.

        :param grid: :class:`~polyim.pyGriddata.gridInfo`
        :param string path: THIS MUST BE CWD (``'.'``) or ``None``

        .. todo:: Update so that landuse folders can be prepped n at a time and so
            that this could be run on a HPC system
        
        """
        if basis_dir == None:
            basis_dir = os.getcwd()

        # check to see if Griddata is here
        if len(glob.glob(path+'/Griddata_*.out')) == 0:
            # check to see if Griddata is compiled and in pyGriddata (or somewhere?)
            for p in sys.path:
                if re.search("PolyADCIRC", p):
                    locations = glob.glob(p+'/*Griddata_*.out')
                    locations.append(glob.glob(p+'/polyadcirc/pyGriddata/Griddata_*.out'))
                    compiled_prog = locations[0]
                    break
            # put Griddata here
            if compiled_prog:
                fm.copy(compiled_prog, path)
            else:
                print "Compile a copy of Griddata_v1.32.F90 and put it in the"
                print "PolyADCIRC folder on your Python Path."
                print "Name it Griddata_parallel.out."

        f14.flag_go(grid, flag)
        first_landuse_folder_name = basis_dir+'/landuse_00'
        first_script = fm.setup_landuse_folder(0, grid,
            folder_name = first_landuse_folder_name)
        # run grid_all_data in this folder 
        subprocess.call(['./'+first_script], cwd = basis_dir)
        # set up remaining land-use classifications
        script_list = fm.setup_landuse_folders(grid, False, basis_dir)

        for s in script_list:
            subprocess.call(['./'+s], cwd = basis_dir)

        # TODO: find out where these will be now that things are moving around
        binaries = glob.glob('*.asc.binary')
        for f in binaries:
            os.remove(f)

        # now clean out unecessary files and convert *.14 to *.13 when appropriate
        fm.cleanup_landuse_folders(grid, basis_dir)
        fm.convert(grid, basis_dir)
        fm.rename13(basis_dir=basis_dir)

    def prep_test(grid, path = None):
        """
        Assumes :meth:`~polyadcirc.pyGriddata.prep_mesh.prep_all` has been run
        first. Prepares a fort.13 file for testing purposes.

        :param grid: :class:`~polyim.pyGriddata.gridInfo`
        :param string path: THIS MUST BE CWD (``'.'``) or ``None``

        """
        if path == None:
            path = os.getcwd()

        subprocess.call(['./'+fm.setup_folder(grid, 'test')], cwd = path)
        grid.convert('test')
        #fm.cleanup_landuse_folder('test')
        fm.rename13(['test'])

    def compare(basis_dir = None, default = 0.012):
        """
        Create a set of diagnostic plots in basis_dir/figs

        :param string basis_dir: directory containing the test folder and landuse
            folders
        :param float default: default Manning's *n*
        """
        if basis_dir == None:
            basis_dir = os.getcwd()
        tables = tm.read_tables(basis_dir+'/test')
        domain = dom.domain(basis_dir)
        domain.read_spatial_grid()
        fm.mkdir(basis_dir+'/figs')
        old_files = glob.glob(basis_dir+'/figs/*.png')
        for fid in old_files:
            os.remove(fid)
        domain.get_Triangulation(path = basis_dir)
        original = f13.read_nodal_attr_dict(basis_dir+'/test')
        original = tmm.dict_to_array(original, default, domain.node_num)
        weights = np.array(tables[0].land_classes.values())
        lim = (np.min(weights), np.max(weights))
        bv_dict = tmm.get_basis_vectors(basis_dir)
        combo = tmm.combine_basis_vectors(weights, bv_dict, default, domain.node_num)
        bv_array = tmm.get_basis_vec_array(basis_dir, domain.node_num)
        plt.basis_functions(domain, bv_array, path = basis_dir)
        plt.field(domain, original, 'original', clim = lim,  path = basis_dir)
        plt.field(domain, combo, 'reconstruction', clim = lim, path = basis_dir)
        plt.field(domain, original-combo, 'difference', path = basis_dir)
        combo_array = tmm.combine_bv_array(weights, bv_array)
        plt.field(domain, combo_array, 'combo_array',  clim = lim, path = basis_dir)
        plt.field(domain, original-combo_array, 'diff_ori_array', path = basis_dir)
        plt.field(domain, combo-combo_array, 'diff_com_array', path = basis_dir)
        combo_bv = tmm.combine_basis_vectors(np.ones(weights.shape),
                bv_dict,default, domain.node_num)
        plt.field(domain, combo_bv, 'combo_bv', path = basis_dir)

