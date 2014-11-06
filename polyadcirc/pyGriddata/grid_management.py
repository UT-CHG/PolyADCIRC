"""
This module contains the class definition for
:class:`~polyadcirc.mesh_mapping.grid_mamangement`.
"""

import os, stat, glob, sys, re, subprocess
from polyadcirc.pyADCIRC.basic import pickleable
import polyadcirc.pyADCIRC.convert_fort14_to_fort13 as c13
import polyadcirc.pyADCIRC.fort14_management as f14
import polyadcirc.pyADCIRC.fort13_management as f13
import polyadcirc.pyADCIRC.plotADCIRC as plt
import numpy as np
import polyadcirc.pyGriddata.table_management as tm
import polyadcirc.pyGriddata.table_to_mesh_map as tmm
import polyadcirc.pyGriddata.file_management as fm
import polyadcirc.run_framework.domain as dom
from polyadcirc.pyADCIRC.basic import comm

size = comm.Get_size()
rank = comm.Get_rank()

class gridInfo(pickleable):
    """
    This class contains references to the ``fort.14``, ``*.asc``, and
    ``*.table`` files specific to a particular grid.
    """
    def __init__(self, basis_dir, grid_dir, gap_data_list, flag=1,
                 file_name="fort.14", table_folder=None,
                 executable_dir=None):
        """ 
        Initalizes a gridInfo object and sets up a directory with links to the
        necessary input files to run :program:`Griddata_v1.1.32.F90` from
        within that directory.

        To run in parallel use :program:`mpirun` or :program:`ibrun`. If
        :program:`Griddata_v1.32.F90` has been compiled using the ``DGHIGHMEM``
        option make sure to correctly set ``OMP_NUM_THREADS`` to be the number
        of processors per node. Then the number of mpi tasks should be set to
        the number of nodes. 
        
        :param string basis_dir: the path to create the landuse_##
            directories in
        :param string grid_dir: the path where the ``fort.14`` formatted file
            is located, there also needs to be a ``fort.13`` formatted file
            here to use as a template
        :param gap_data_list: a list() of
            :class:`~polyadcirc.pyGriddata.table_management.gapInfo` objects
        :type gap_data_list: list()
        :param int flag: flag to choose which averaging scheme to use ..see::
            :meth:`~polyadcirc.pyADCIRC.flag_fort14.flag_fort14`
        :param string file_name: the name of the ``fort.14`` formatted file in
            ``grid_dir``
        :param string table_folder: The folder containing the ``*.table`` file.
            This is ONLY necessary when running simutaneous copies of the
            :program:`Griddata`.
        :param string executable_dir: path to the directory containing the
            compiled ``Griddata_*.out`` executable 
        
        """
        self.file_name = file_name #: Name of grid file, ``*.14``
        self.grid_dir = grid_dir  #: path for the dir of the grid file
        self.gap_data_files = gap_data_list #: a list of gapInfo objects
        self.basis_dir = basis_dir #: path for the dir to create landuse_ in
        self.table_folder = table_folder #: path for the dir with ``*.table``
        """ list() of :class:`~polyadcirc.table_management.gapInfo` objects """
        self.__landclasses = [] 
        self.__unique_tables = {} 
        for gap in self.gap_data_files:
            #: dict() of unique ``*.table`` files used
            self.__unique_tables[gap.table.file_name] = gap.table
        for k, v in self.__unique_tables.iteritems():
            for x in v.get_landclasses():
            #: list of landclasses used by this grid
                self.__landclasses.append((x, k))
        self.flag = flag #: averaging scheme flag

        if rank == 0:
            # Look for ``fort.14`` formatted file in grid_dir and place a link
            # to it in basis_dir
            fm.symlink(grid_dir+'/'+file_name, basis_dir+'/'+file_name)
            flagged_file_name = f14.flag_go(self, flag)
            self.file_name = os.path.basename(flagged_file_name)

            # check to see if Griddata is here
            if executable_dir == None:
                executable_dir = sys.path
            else:
                executable_dir = [executable_dir]
            if len(glob.glob(self.basis_dir+'/Griddata_*.out')) == 0:
                # check to see if Griddata is compiled and on the python path
                compiled_prog = None
                for p in executable_dir:
                    locations1 = glob.glob(p+"/*Griddata_*.out")
                    locations2 = glob.glob(p+"/polyadcirc/pyGriddata/Griddata_*.out")
                    if locations1:
                        compiled_prog = locations1[0]
                    elif locations2:
                        compiled_prog = locations2[0]
                    else:
                        compiled_prog = None
                    break
                # put link to Griddata here
                if compiled_prog:
                    fm.symlink(compiled_prog,
                               os.path.join(basis_dir,
                                            os.path.basename(compiled_prog)))
                else:
                    print """Compile a copy of Griddata_v1.32.F90 and specify
                    it's location using executable_dir"""
            # Create links to gap files (*.asc) using gap_list of gapInfo
            # objects
            for gap in self.gap_data_files:
                local_file_name = os.path.basename(gap.file_name)
                fm.symlink(gap.file_name, basis_dir+'/'+local_file_name)
                if os.path.exists(gap.file_name+'.binary'):
                    fm.symlink(gap.file_name+'.binary',
                        basis_dir+'/'+local_file_name+'.binary')
                gap.file_name = local_file_name
        self.file_name = comm.bcast(self.file_name, root=0)
        
        super(gridInfo, self).__init__()
 
    def prep_all(self, removeBinaries=False, class_nums=None, condense=True,
            TOL=None):
        """
        Assumes that all the necessary input files are in ``self.basis_dir``.
        This function generates a ``landuse_##`` folder in ``self.basis_dir``
        for every land classification number containing a ``fort.13`` file
        specific to that land classification number.

        .. todo:: Update so that landuse folders can be prepped n at a time and
                  so that this could be run on a HPC system

        Currently, the parallel option preps the first folder and then all the
        remaining folders at once.

        :param binary parallel: Flag whether or not to simultaneously prep
            landuse folders.
        :param binary removeBinarues: Flag whether or not to remove
            ``*.asc.binary`` files when completed.
        :param list class_nums: List of integers indicating which classes to
            prep. This assumes all the ``*.asc.binary`` files are already in
            existence.
        :param boolean condense: Flag whether or not to condense ``fort.13`` to
            only non-zero values within a tolerance.
        :param double TOL: Tolerance below which to consider a Manning's n
            value to be zero if ``condense == True``
        
        """
        if class_nums == None:
            class_nums = range(len(self.__landclasses))
        if rank > class_nums:
            print "There are more MPI TASKS than land classes."
            print "This code only scales to MPI_TASKS = len(land_classes)."
            print "Extra MPI TASKS will not be used."
            return

        # Are there any binary files?
        binaries = glob.glob(self.basis_dir+'/*.asc.binary')
        # If not create them
        if not(binaries) and rank == 0:
            # set up first landuse folder
            first_script = self.setup_landuse_folder(class_nums[0])
            # set up remaining land-use classifications
            script_list = self.setup_landuse_folders(False)
            # run grid_all_data in this folder 
            subprocess.call(['./'+first_script], cwd=self.basis_dir)
            class_nums.remove(0)
        elif rank == 0:
            script_list = self.setup_landuse_folders()
        else:
            script_list = None
            class_nums = None
        class_nums = comm.bcast(class_nums, root=0)
        script_list = comm.bcast(script_list, root=0)
        
        if len(class_nums) != len(script_list):
            temp = [script_list[i] for i in class_nums]
            script_list = temp

        # run remaining bash scripts
        for i in range(0+rank, len(script_list), size):
            # run griddata
            subprocess.call(['./'+script_list[i]], cwd=self.basis_dir)
            # clean up folder
            match_string = r"grid_all_(.*)_"+self.file_name[:-3]+r"\.sh"
            landuse_folder = re.match(match_string, script_list[i]).groups()[0]
            self.cleanup_landuse_folder(os.path.join(self.basis_dir,
                landuse_folder))
            # rename fort.13 file
            fm.rename13([landuse_folder], self.basis_dir) 
            if condense:
                print "Removing values below TOL"
                landuse_folder_path = os.path.join(self.basis_dir,
                        landuse_folder)
                # read fort.13 file
                mann_dict = f13.read_nodal_attr_dict(landuse_folder_path)
                # condense fort.13 file
                condensed_bv = tmm.condense_bv_dict(mann_dict, TOL)
                # write new file
                f13.update_mann(condensed_bv, landuse_folder_path) 
        print "Done"
        # remove unnecessary files
        if removeBinaries and rank == 0:
            binaries = glob.glob(self.basis_dir+'/*.asc.binary')
            for f in binaries:
                os.remove(f)
 
    def prep_test(self, removeBinaries=False):
        """
        Assumes :meth:`~polyadcirc.pyGriddata.prep_mesh.prep_all` has been run
        first. Prepares a fort.13 file for testing purposes.
        
        :param binary removeBinaries: flag wheter or not to remove
            ``*.asc.binary`` files

        """
        subprocess.call(['./'+self.setup_folder('test')], cwd=
                        self.basis_dir)
        self.convert(self.basis_dir+'/'+'test')
        # remove unnecessary files
        if removeBinaries:
            binaries = glob.glob(self.basis_dir+'/*.asc.binary')
            for f in binaries:
                os.remove(f)
        self.cleanup_landuse_folder(self.basis_dir+'/test')
        fm.rename13(['test'], self.basis_dir)  

    def __str__(self):
        """ 
        :rtype: string
        :returns: Return string that matches header and following relevants
            lines of ``*.in`` file
        """
        string_rep = self.__iter_string(self)
        return string_rep

    def __iter_string(self, i=0, folder_name=''):
        """ 
        Return string that matches header and following relevant lines of
        ``*.in`` file assuming :program:`Griddata_v1.32.F90` has been run ``i``
        times

        :param int i: number of times :program:`Griddata_v1.32.F90` has been
            run
        :param string folder_name: name of the folder where input files for
            this run of :program:`Griddata_v1.32.F90` are located
        :rtype: string
        :returns: Return string that matches header and following relevants
            lines of ``*.in`` file

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
        
    def create_griddata_input_files(self, folder_name):
        """ 
        Creates a series of ``*.in`` files named in order to be run
        by :program:`./Griddata_parallel -I griddata_##.in`

        :param string folder_name: folder for which to create input files

        """
        for i, x in enumerate(self.gap_data_files):
            file_name = self.basis_dir+'/'+folder_name+'/griddata_'+str(i)+'.in'
            with open(file_name, 'w') as f:
                f.write(self.__iter_string(i, folder_name))
                f.write(x.local_str(self.basis_dir, folder_name))

    def create_bash_script(self, folder_name):
        """
        Creates bash script called grid_file.sh in ``self.basis_dir`` or
        ``cwd`` if ``folder_name==None`` to run Griddata in order on all the
        ``*.in`` file associated with this grid 

        :param string folder_name: folder for which to create bash scripts

        """
        file_name = folder_name +'/'
        script_name = self.basis_dir+'/grid_all_'+folder_name+'_'
        script_name += self.file_name[:-2]+'sh'
        with open(script_name, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('# This script runs Griddata on several input files\n')
            for i in xrange(len(self.gap_data_files)):
                input_name = file_name + 'griddata_'+str(i)+'.in'
                f.write('./Griddata_parallel.out -I '+input_name+'\n')
            f.write('\n\n')
        curr_stat = os.stat(script_name)
        os.chmod(script_name, curr_stat.st_mode | stat.S_IXUSR)
        return os.path.basename(script_name)
    
    def setup_tables_single_value(self, class_num, manningsn_value,
                                  folder_name):
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
        u_table.create_table_single_value(t_class_number, manningsn_value,
                                          folder_name)

    def setup_tables(self, folder_name):
        """
        Creates a ``*.table`` in ``folder_name`` for each unqiue ``*.table`` 
        file required by ``grid_all_*.sh``

        :param string folder_name: name of the folder to create table in
        
        """
        for x in self.__unique_tables.itervalues():
            x.create_table(folder_name)

    def convert(self, folder_name, keep_flags=0):
        """ 
        
        :meth:`~polyadcirc.pyADCIRC.convert_fort14_to_fort13.convert` where
        ``source`` is the final ``*.14`` file produced by the bash script
        associated with ``self`` in ``folder_name``

        :param string folder_name: name of the folder containing the ``*.14``
            to be converted
        
        See :meth:`~polyadcirc.pyADCIRC.convert_fort14_to_fort13.convert`
        """
        c13.convert_go(self, folder_name, keep_flags)

    def setup_landuse_folder(self, class_num, manningsn_value=1,
                             folder_name=None): 
        """ 
        Set up a single landuse with name landuse_class_num
        
        :param int class_num: land classification number for this folder
        :param int manningsn_value: Manning's *n* value for this land
            classification
        :param string folder_name: folder name relative to ``self.base_dir``
        :rtype: string
        :returns: file name of bash script for this land class

        """
        if folder_name == None:
            folder_name = 'landuse_'+'{:=02d}'.format(class_num)
        print 'Setting up folder -- '+folder_name+'...'
        # create a folder for this land-use classification
        fm.mkdir(self.basis_dir+'/'+folder_name)
        # cp self.file_name folder_name
        fm.copy(self.basis_dir+'/'+self.file_name,
                self.basis_dir+'/'+folder_name)
        # create *.in files
        self.create_griddata_input_files(folder_name)
        # create *.sh files
        script_name = self.create_bash_script(folder_name)
        # create the *.table file needed for grid_all_data
        self.setup_tables_single_value(class_num, manningsn_value,
                                       self.basis_dir+'/'+folder_name)
        return script_name

    def setup_landuse_folders(self, create_all=True):
        """ 
        Set up landuse folders by copying all necessary files to run
        grid_all_data into the landuse folder. One folder is created for each
        landuse classification. 

        If create_all is True then sets up num_landuse folders.
        Else sets up num_landuse-1 folders.

        :param boolean create_all: flag to not skip first folder
        :rtype: list()
        :returns: list of file names of bash scripts for each land class

        """
        
        print 'Setting up a single set of landuse folders...'
        list_of_landuse_classes = self.get_landclasses()
        script_list = []
        if create_all:
            for i in xrange(len(list_of_landuse_classes)):
                script_list.append(self.setup_landuse_folder(i))
        else:
            for i in xrange(1, len(list_of_landuse_classes)):
                script_list.append(self.setup_landuse_folder(i))
        return script_list

    def setup_folder(self, folder_name='temp'):
        """ 
        Set up a single folder with name folder_name 

        :param string folder_name: folder name relative to ``self.base_dir``
        :rtype: string
        :returns: file name of bash script for this land class

        """
        print 'Setting up folder -- '+folder_name+'...'
        # create a folder for this land-use classification
        fm.mkdir(self.basis_dir+'/'+folder_name)
        # cp self.file_name folder_name
        fm.copy(self.basis_dir+'/'+self.file_name,
                self.basis_dir+'/'+folder_name)
        # create *.in files
        self.create_griddata_input_files(folder_name)
        # create *.sh files
        script_name = self.create_bash_script(folder_name)        
        # create the *.table file needed for grid_all_data
        self.setup_tables(self.basis_dir+'/'+folder_name)
        return script_name

    def cleanup_landuse_folder(self, folder_name=None):
        """ 
        
        Removes all files in folder_name(or current directory) except *.table
        and the most recent ``*.14``
        
        :param string folder_name: path to folder to clean up relative to
            ``self.base_dir``

        """
        if folder_name == None:
            folder_name = ''
            print 'Cleaning current directory...'
        else:
            print 'Cleaning '+folder_name+'...'
        file_list = glob.glob(folder_name+'/*')
        fort13_files = glob.glob(folder_name+'/*.13')
        table_files = glob.glob(folder_name+'/*.table')
        f14_files = f14.clean(self, folder_name)
        if f14_files:
            for x in f14_files:
                file_list.remove(x)
        for x in fort13_files:
            file_list.remove(x)
        for x in table_files:
            file_list.remove(x)
        for x in file_list:
            os.remove(x)   
        self.convert(folder_name)

    def cleanup_landuse_folders(self):
        """ 
        Removes all files except ``*.table`` and the most recent ``*.14`` in all
        landuse folders in the current directory

        """
        print 'Cleaning all landuse folders...'
        landuse_folder_names = glob.glob(self.basis_dir+'/landuse_*')
        for x in landuse_folder_names:
            self.cleanup_landuse_folder(x)


def compare(basis_dir=None, default=0.012):
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
    domain.get_Triangulation(path=basis_dir)
    original = f13.read_nodal_attr_dict(basis_dir+'/test')
    original = tmm.dict_to_array(original, default, domain.node_num)
    weights = np.array(tables[0].land_classes.values())
    lim = (np.min(weights), np.max(weights))
    bv_dict = tmm.get_basis_vectors(basis_dir)
    combo = tmm.combine_basis_vectors(weights, bv_dict, default,
                                      domain.node_num) 
    bv_array = tmm.get_basis_vec_array(basis_dir,
                                       domain.node_num)
    plt.basis_functions(domain, bv_array, path=basis_dir)
    plt.field(domain, original, 'original', clim=lim, path=basis_dir)
    plt.field(domain, combo, 'reconstruction', clim=lim, path=basis_dir)
    plt.field(domain, original-combo, 'difference', path=basis_dir)
    combo_array = tmm.combine_bv_array(weights, bv_array)
    plt.field(domain, combo_array, 'combo_array', clim=lim, path=basis_dir)
    plt.field(domain, original-combo_array, 'diff_ori_array', path=basis_dir)
    plt.field(domain, combo-combo_array, 'diff_com_array', path=basis_dir)
    combo_bv = tmm.combine_basis_vectors(np.ones(weights.shape),
                                         bv_dict, default, domain.node_num)
    plt.field(domain, combo_bv, 'combo_bv', path=basis_dir)

