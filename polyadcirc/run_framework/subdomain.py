"""
This module contains a set of methods and a class for interacting with NCSU
Subdomain Modeling Python code and associated files. The focus of this module
is the :class:`subdomain`.
"""

import glob, os, sys, subprocess, re, math 
import numpy as np
import polyadcirc.run_framework.domain as dom
import polyadcirc.pyADCIRC.fort15_management as f15
import polyadcirc.pyADCIRC.fort13_management as f13
import polyadcirc.pyADCIRC.output as output
import polyadcirc.run_framework.random_manningsn as rmn
import polyadcirc.pyADCIRC.post_management as post
import polyadcirc.pyGriddata.file_management as fm
import scipy.io as sio
from polyadcirc.pyADCIRC.basic import comm
import py.gensub as gensub 

def loadmat(save_file, base_dir, grid_dir, save_dir, basis_dir):
    """
    Loads data from ``save_file`` into a
    :class:`~polyadcirc.run_framwork.random_manningsn.runSet` object.
    Reconstructs :class:`~polyadcirc.run_framwork.random_manningsn.subdomain`. 

    :param string save_file: local file name
    :param string grid_dir: directory containing ``fort.14``, ``fort.15``, and
        ``fort.22`` 
    :param string save_dir: directory where ``RF_directory_*`` are
        saved, and where fort.13 is located 
    :param string basis_dir: directory where ``landuse_*`` folders are located
    :param string base_dir: directory that contains ADCIRC executables, and
        machine specific ``in.prep#`` files 
    :rtype: tuple of :class:`~polyadcirc.run_framwork.random_manningsn.runSet`
        and :class:`~polyadcirc.run_framwork.random_manningsn.domain` objects
    :returns: (main_run, domain)

    """
    
    # the lines below are only necessary if you need to update what the
    # directories are when swithcing from euclid to your desktop/laptop
    # assumes that the landuse directory and ADCIRC_landuse directory are in
    # the same directory
    domain = subdomain(grid_dir)
    domain.update()
    domain.get_Triangulation()
    #domain.set_station_bathymetry()

    main_run = rmn.runSet(grid_dir, save_dir, basis_dir, base_dir=base_dir)
    main_run.ts_error = {}
    main_run.nts_error = {}
    main_run.time_obs = {}

    # load the data from at *.mat file
    mdat = sio.loadmat(os.path.join(save_dir, save_file))

    for k, v in mdat.iteritems():
        skey = k.split('_')
        if skey[-1] == 'time':
            # check to see if the key is "*_time"
            main_run.time_obs[skey[0]] = v
        elif f15.filetype.has_key(skey[0]):
            if not re.match('fort', skey[0]):
                # check to see if key is nts_data
                main_run.nts_error[skey[0]] = v
            else:
                # check to see if key is ts_data
                main_run.ts_error[skey[0]] = v
        #print k, v
    
    return (main_run, domain)

class subdomain(dom.domain):
    """
    Objects of this class contain all the data needed by :mod:`py.genbcs`,
    :mod:`py.genfull`, and :mod:`py.gensub` for a particular subdomain
    mesh/grid. References to :class:`polyadcirc.run_framework.subdomain` objects
    are also contained in an instantiation of this class.
    """
    def __init__(self, path, node_num=0, element_num=0,
                 node=None, element=None):
        """
        Initialization
        """
        super(subdomain, self).__init__(path, node_num, element_num, node,
                                        element)

        # figure out where the script dir for the ncsu subdomain code is
        for sys_path in sys.path:
            potential_file_list = glob.glob(sys_path+'/py')
            if potential_file_list:
                self.script_dir = potential_file_list[0]
                break

        fm.mkdir(path)

        #: flag for shape of subdomain (0 ellipse, 1 circle)
        self.flag = None

    def set_fulldomain(self, fulldomain):
        """
        Sets the fulldomain of this subdomain to fulldomain and adds this
        subdomain to that fulldomain.

        :type fulldomain: :class:`~polyadcirc.run_framework.fulldomain`
        :param fulldomain: the fulldomain for this subdomain

        """
        self.fulldomain = fulldomain
        self.fulldomain.subdomains.append(self)

    def gensub(self, bound_ele=1, bound_vel=1, bound_wd=1):
        """
        Generate the subdomain input files (``fort.13``, ``fort.14``,
        ``fort.015``, ``py.141``, ``py.140``) and shape file. Creates
        ``fort.15`` based on the ``fort.15`` in
        :class:`polyadcirc.run_framework.fulldomain` to ``self.path``, and
        creates symbolic links to meterological forcing files (``fort.22*``).
        
        :param int bound_ele: a flag determining whether surface elevations of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :param int bound_vel: a flag determining whether velocities of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :param int bound_wd: a flag determining whether wet/dry status of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :rtype: string
        :returns: command line for invoking gensub.py

        """
        with open(self.path+'/gensub.in', 'w') as fid:
            fid.write(str(bound_ele)+'\n')
            fid.write(str(bound_vel)+'\n')
            fid.write(str(bound_wd)+'\n')
        command = 'python '+self.script_dir+'/gensub.py '
        command += self.fulldomain.path+'/fort.14 '+str(self.flag)+' '
        command += 'fort.14 '
        
        if os.path.exists(self.fulldomain.path+'/fort.13'):
            command += self.fulldomain.path+'/fort.13 '
            command += 'fort.13 ' 
        
        command += '< gensub.in'
        subprocess.call(command, shell=True, cwd=self.path)

        #self.update_sub2full_map()
        self.create_fort15()
        self.link_fort22()
        return command

    def link_fort22(self):
        """
        Create symboolic links to ``fort.22*`` meterological files in this
        subdomain folder from the fulldomain folder.
        """
        fort22_files = glob.glob(self.fulldomain.path+'/fort.22*')
        for fid in fort22_files:
            fm.symlink(fid, self.path+'/'+fid.rpartition('/')[-1])

    def genfull(self, noutgs=1, nspoolgs=1):
        """ 
        Generate the full domain control file, ``fort.015``, and save it to
        ``self.fulldomain.path``.

        :param int noutgs: flag controlling whether or not ``fort.06*`` will be
            written out 
        :param int nspoolgs: the number of timesteps at which information is
            written to the new output files ``fort.06*``
        :rtype: string
        :returns: command line for invoking genfull.py
        
        """
        return self.fulldomain.genfull(noutgs, nspoolgs, [self])

    def genbcs(self, forcing_freq=1, dt=None, nspoolgs=1, h0=None, L=False):
        """
        Generate the ``fort.019`` which is the boundary conditions file needed
        for a subdomain run of :program:`ADCIRC`. This requires the presence of
        the output files from a fulldomain run, ``fort.06*``.

        :param int forcing_freq: number of timesteps at which infomration
            is written to a boudnary conditions file (``fort.019``) THIS MUST
            BE A MULTIPLE OF NSPOOLGS
        :param float dt: One timestep in seconds
        :param int nspoolgs: the number of timesteps at which information is
            written to the new output files ``fort.06*``
        :param float h0: minimum water depth for a node to be wet
        :param boolean L: flag whether or not :program:`PADCIRC` was run with
            ``-L`` flag and if local files need to be post-processed into
            global files
        :rtype: string
        :returns: command line for invoking genbcs.py

        """
        if L:
            # create post-processing input file
            post.write_sub(self.fulldomain.path)
            # run ADCPOST
            subprocess.call('./adcpost < in.postsub > post_o.txt', shell=True,
                            cwd=self.fulldomain.path)
        
        self.create_fort15()
        self.link_fort22()
        self.read_recording_data()

        if self.check_fulldomain():
            if h0 == None:
                h0 = self.h0
            if dt == None:
                dt = self.fulldomain.time.dt
            command = "python "+self.script_dir+"/genbcs.py -p "
            command += self.fulldomain.path+'/ '+self.path+'/ '
            command += str(forcing_freq)+' '+str(dt)+' '+str(nspoolgs)
            command += ' '+str(h0)
            print command
            subprocess.call(command, shell=True, cwd=self.path)
            return command
        else:
            print "Output files from the fulldomain run do not exist"
            return "Output files from the fulldomain run do not exist"

    def circle(self, x, y, r):
        """
        Generate a subdomain shape file for a circular subdomain

        :param float x: x coordinate of circle center
        :param float y: y coordinate of circle center
        :param float r: radius of circle
        :rtype: int
        :returns: flag for :meth:`py.gensub`

        """
        with open(self.path+'/shape.c14', 'w') as fid:
            fid.write('{:17.15f} {:17.15f}\n'.format(x, y))
            fid.write(str(r))
        self.flag = 1
        return self.flag

    def ellipse(self, x, y, w):
        """
        Generate a subdomain shape file for an elliptical subdomain
        
        :param list() x: x coordinates of the first and second focal points
        :param list() y: y coordinates of the first and second focal points
        :param float w: width of ellipse
        :rtype: int
        :returns: flag for :meth:`py.gensub`

        """
        with open(self.path+'/shape.e14', 'w') as fid:
            fid.write('{:17.15f} {:17.15f}\n'.format(x[0], y[0]))
            fid.write('{:17.15f} {:17.15f}\n'.format(x[1], y[1]))
            fid.write(str(w))
        self.flag = 0
        return self.flag

    def read_circle(self):
        """
        Read in the parameters used to define the circular subdomain cut out and
        store them as ``self.x``, ``self.y``, and ``self.r``

        :rtype: tuple
        :returns: (x, y, r)

        """
        with open(self.path+"/shape.c14", "r") as fid:
            t = fid.readline().split()
            x = float(t[0])
            y = float(t[1])
            r = float(fid.readline())

        self.x = x
        self.y = y
        self.r = r
        return (x, y, r)

    def read_ellipse(self):
        """
        Read in the parameters used to define the circular subdomain cut out and
        store them as ``self.x``, ``self.y``, and ``self.r``

        :rtype: tuple
        :returns: (x, y, w)

        """

        with open(self.path+"/shape.e14", "r") as fid:
            point1 = fid.readline().split()
            point2 = fid.readline().split()
            x = [float(point1[0]), float(point2[0])]
            y = [float(point1[1]), float(point2[1])]
            w = float(fid.readline())
            self.x = x
            self.y = y
            self.w = w
        return (x, y, w)

    def ellipse_properties(self, x, y, w):
        """
        Given a the (x,y) locations of the foci of the ellipse and the width
        return the center of the ellipse, width, height, and angle relative to
        the x-axis.

        :param double x: x-coordinates of the foci
        :param double y: y-coordinates of the foci
        :param double w: width of the ellipse
        :rtype: tuple of doubles
        :returns: (center_coordinates, width, height, angle_in_rads)

        """
        return ellipse_properties(x, y, w)

    def setup(self, flag=None, bound_ele=1, bound_vel=1, bound_wd=1):
        """
        Generate the subdomain input files (``fort.13``, ``fort.14``,
        ``fort.015``, ``py.141``, ``py.140``) and shape file. Creates
        ``fort.15`` based on the ``fort.15`` in
        :class:`polyadcirc.run_framework.fulldomain` to ``self.path``, and
        creates symbolic links to meterological forcing files (``fort.22*``).
        
        :param int flag: flag determining whether or not the subdomain is an
            ellipse (0) or a circle (1)
        :param int bound_ele: a flag determining whether surface elevations of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :param int bound_vel: a flag determining whether velocities of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :param int bound_wd: a flag determining whether wet/dry status of
            the boundary nodes of a subdomain are enforced using a boundary
            condition file.
        :rtype: string
        :returns: command line for invoking gensub.py

        """
        # Appropriately flag subdomain
        if flag == None and self.flag == None:
            circle = glob.glob(self.path+'/shape.c14')
            if len(circle) > 0:
                self.flag = 1
            ellipse = glob.glob(self.path+'/shape.e14')
            if len(ellipse) > 0:
                self.flag = 0
        elif flag != None:
            self.flag = flag #: flag for :meth:`py.gensub`
        # Get rid of old files
        f_list = ['fort.015', 'fort.13', 'fort.14', 'bv.nodes', 'py.140',
                  'py.141']
        for fid in f_list:
            if os.path.exists(self.path+'/'+fid):
                os.remove(self.path+'/'+fid)
        return self.gensub(bound_ele, bound_vel, bound_wd)
        
    def check_fulldomain(self):
        """
        Check to see if the ``fort.06*`` and ``PE*/fort.065`` files exist

        :rtype: boolean
        :returns: False if the ``fort.06*`` files don't exist
        
        """
        return self.fulldomain.check_fulldomain()

    def check(self):
        """
        Check to make sure the ``fort.019`` file exists

        :rtype: boolean
        :returns: False the ``fort.019`` doesn't exist

        """
        fort019 = glob.glob(self.path+'/fort.019')
        return len(fort019) > 0

    def compare_runSet(self, ts_data, nts_data, ts_names=None, 
                       nts_names=None, save_file=None): 
        """
        Reads in :class:`polyadcirc.random_manningsn.runSet` output from this
        subdomain and from it's fulldomain and compares them.

        NOTE THIS DOES NOT CURRENTLY WORK FOR STATION DATA! ONLY USE FOR GLOBAL
        DATA i.e files that are fort.*3 or fort.*4

        comparision_data = fulldomain_data - subdomain_data
        
        :param list() ts_data: (ts_data_subdomain, ts_data_fulldomain)
        :param list() nts_data: (nts_data_subdomain, nts_data_fulldomain)
        :param list() ts_names: names of ADCIRC timeseries
            output files to be recorded from each run
        :param list() nts_names: names of ADCIRC non timeseries
            output files to be recorded from each run
        :param string save_file: name of file to save comparision matricies to
        :rtype: tuple
        :returns: (ts_error, nts_error)

        """
        
        if save_file == None:
            save_file = self.path+'/compare_s2f_runSet.mat'

        nts_keys = []
        if nts_names == None:
            nts_keys = nts_data[0].keys()
        else:
            for fid in nts_names:
                nts_keys.append(fid.replace('.', ''))

        ts_keys = []
        if ts_names == None:
            ts_keys = ts_data[0].keys()
        else:
            for fid in ts_names:
                ts_keys.append(fid.replace('.', ''))

        # Save matricies to *.mat file for use by MATLAB or Python
        mdict = dict()

        # Pre-allocate arrays for non-timeseries data
        nts_error = {}
        ts_error = {}

        fulldom_nodes = [v-1 for v in self.sub2full_node.values()]

        # Get nts_error
        for key in nts_keys:
            full_data = nts_data[1][key][fulldom_nodes]
            sub_data = nts_data[0][key]
            nts_error[key] = (full_data - sub_data)#/full_data

        # fix dry nodes
        if 'fort63' in ts_keys:
            ts_data[0] = rmn.fix_dry_nodes(ts_data[0], self)
            ts_data[1] = rmn.fix_dry_nodes(ts_data[1], self)

        # fix dry data
        if 'fort61' in ts_keys:
            self.set_station_bathymetry()
            ts_data[0] = rmn.fix_dry_data(ts_data[0], self)
            ts_data[1] = rmn.fix_dry_data(ts_data[1], self)

        # Get ts_data
        for key in ts_keys:
            # Theres a bug wrt stations here either we need a mapping between
            # fulldomain stations and subdomain stations or these stations MUST
            # be the same.
            if key == 'fort61' or key == 'fort62':
                continue
            sub_data = ts_data[0][key]
            total_obs = sub_data.shape[1]
            if self.recording[key][2] == 1:
                full_data = ts_data[1][key][fulldom_nodes, 0:total_obs]
            else:
                full_data = ts_data[1][key][fulldom_nodes, 0:total_obs, :]
            ts_error[key] = (full_data - sub_data)#/full_data

        # Update and save
        # export nontimeseries data
        for k, v in nts_error.iteritems():
            mdict[k] = v
            print k
            b = np.ma.fix_invalid(v, fill_value=0)
            print np.max(abs(b)), np.argmax(abs(b))
        # export timeseries data
        for k, v in ts_error.iteritems():
            mdict[k] = v
            print k
            b = np.ma.fix_invalid(v, fill_value=0)
            print np.max(abs(b)), np.argmax(abs(b))

        sio.savemat(save_file, mdict, do_compression=True)
        return (ts_error, nts_error)
    
    def compare_to_fulldomain(self, ts_names, nts_names, save_file=None,
                              timesteps=None, savefull=True, readmatfull=False,
                              savesub=True, readmatsub=False, fulldict=None):
        """
        Reads in output files from this subdomain and from it's fulldomain and
        compares them.

        NOTE THIS DOES NOT CURRENTLY WORK FOR STATION DATA! ONLY USE FOR GLOBAL
        DATA i.e files that are fort.*3 or fort.*4

        NOTE THIS DOES NOT CURRENTLY WORK FOR ANY NTS DATA EXCEPT FOR MAXELE

        comparision_data = fulldomain_data - subdomain_data

        :param list() ts_names: names of ADCIRC timeseries
            output files to be recorded from each run
        :param list() nts_names: names of ADCIRC non timeseries
            output files to be recorded from each run
        :param string save_file: name of file to save comparision matricies to
        :param int timesteps: number of timesteps to read from file
        :rtype: tuple
        :returns: (ts_error, nts_error, time_obs, ts_data, nts_data)

        """
        
        if save_file == None:
            save_file = self.path+'/compare_s2f.mat'

        full_file = os.path.join(self.fulldomain.path, 'full.mat')
        sub_file = os.path.join(self.path, 'sub.mat')

        # Save matricies to *.mat file for use by MATLAB or Python
        mdict = dict()
        if readmatsub:
            subdict = sio.loadmat(sub_file)
            savesub = False
        else:
            subdict = dict()

        if fulldict == None:
            if readmatfull:
                fulldict = sio.loadmat(full_file)
                savefull = False
            else:
                fulldict = dict()
        else:
            readmatfull = True
            savefull = False

        # Pre-allocate arrays for non-timeseries data
        nts_error = {}
        ts_error = {}
        time_obs = {}

        fulldom_nodes = [v-1 for v in self.sub2full_node.values()]

        nts_data = {}
        ts_data = {}

        # Get nts_error
        for fid in nts_names:
            key = fid.replace('.', '')
            if not readmatfull:
                fulldict[key] = output.get_nts_sr(self.fulldomain.path,
                                                  self.fulldomain, fid)
            if not readmatsub:
                subdict[key] = output.get_nts_sr(self.path, self, fid)

        # Get ts_data
        for fid in ts_names:
            key = fid.replace('.', '')
            if not readmatsub:
                subdict[key], time_obs[key] = output.get_ts_sr(self.path, fid,
                                                               True,
                                                               ihot=self.ihot) 
                subdict[key+'_time'] = time_obs[key]
            if not readmatfull:
                fulldict[key] = output.get_ts_sr(self.fulldomain.path,
                                                 fid, timesteps=timesteps,
                                                 ihot=self.fulldomain.ihot)[0]
       
        if not readmatsub:
            # fix dry nodes
            if subdict.has_key('fort63'):
                subdict['fort63'] = np.expand_dims(subdict['fort63'], axis=2)
                subdict = rmn.fix_dry_nodes(subdict, self)
                subdict['fort63'] = np.squeeze(subdict['fort63'])
            # fix dry data
            if subdict.has_key('fort61'):
                subdict['fort61'] = np.expand_dims(subdict['fort61'], axis=1)
                subdict = rmn.fix_dry_data(subdict, self)
                subdict['fort61'] = np.squeeze(subdict['fort61'])
            # fix dry nodes nts
            if subdict.has_key('maxele63'):
                subdict['maxele63'] = np.expand_dims(subdict['maxele63'], axis=1)
                subdict = rmn.fix_dry_nodes_nts(subdict, self)
                subdict['maxele63'] = np.squeeze(subdict['maxele63'])


        if not readmatfull:
            # fix dry nodes
            if fulldict.has_key('fort63'):
                fulldict['fort63'] = np.expand_dims(fulldict['fort63'], axis=2)
                fulldict = rmn.fix_dry_nodes(fulldict, self)
                fulldict['fort63'] = np.squeeze(fulldict['fort63'])
            # fix dry data
            if fulldict.has_key('fort61'):
                fulldict['fort61'] = np.expand_dims(fulldict['fort61'], axis=1)
                fulldict = rmn.fix_dry_data(fulldict, self)
                fulldict['fort61'] = np.squeeze(fulldict['fort61'])
            # fix dry nodes nts
            if fulldict.has_key('maxele63'):
                fulldict['maxele63'] = np.expand_dims(fulldict['maxele63'], axis=1)
                fulldict = rmn.fix_dry_nodes_nts(fulldict, self)
                fulldict['maxele63'] = np.squeeze(fulldict['maxele63'])



        
        # Get nts_error
        for fid in nts_names:
            key = fid.replace('.', '')
            nts_data[key] = np.array([fulldict[key][fulldom_nodes].T,
                subdict[key].T]).T

        # Get ts_data
        for fid in ts_names:
            key = fid.replace('.', '')
            sub_data, time_obs[key] = subdict[key], subdict[key+'_time']
            total_obs = sub_data.shape[1]
            if timesteps and timesteps < total_obs:
                total_obs = timesteps
            full_data = fulldict[key]
            if self.recording[key][2] == 1:
                full_data = full_data[fulldom_nodes, 0:total_obs] 
            else:
                full_data = full_data[fulldom_nodes, 0:total_obs, :]
            ts_data[key] = np.array([full_data.T, sub_data.T]).T


        # update max vaules
        if nts_data.has_key('maxele63'):
            nts_data['maxele63'][..., 0] = np.max(ts_data['fort63'][..., 0],
                                                  axis=1)
        if nts_data.has_key('maxvel63'):
            nts_data['maxele63'][..., 0] = np.max(np.sqrt(ts_data['fort64'][...,
                0, 0]**2 + ts_data['fort64'][..., 1, 0]**2), axis=1)
        
        # Get ts_error
        for fid in ts_names:
            key = fid.replace('.', '')
            ts_error[key] = (ts_data[key][..., 0] - ts_data[key][..., 1])

        # Get nts_error
        for fid in nts_names:
            key = fid.replace('.', '')
            nts_error[key] = (nts_data[key][..., 0] - nts_data[key][..., 1])

        # Update and save
        # export nontimeseries data
        for k, v in nts_error.iteritems():
            mdict[k] = v
            print k
            #b = np.ma.fix_invalid(v, fill_value=0)
            b = v
            print np.max(abs(b)), np.argmax(abs(b))
            print "Nodes above threshold", sum(np.abs(b) > 1e-2)
        # export timeseries data
        for k, v in ts_error.iteritems():
            mdict[k] = v
            print k
            #b = np.ma.fix_invalid(v, fill_value=0)
            b = v
            print np.max(abs(b)), np.argmax(abs(b))
            print "Nodes above threshold", sum(np.abs(b) > 1e-2)

        # export time_obs data
        for k, v in time_obs.iteritems():
            mdict[k+'_time'] = v

        sio.savemat(save_file, mdict, do_compression=True)
        if savesub:
            sio.savemat(sub_file, subdict, do_compression=True)
        if savefull:
            sio.savemat(full_file, fulldict, do_compression=True)

        return (ts_error, nts_error, time_obs, ts_data, nts_data)

    def create_fort15(self):
        """
        Copy the ``fort.15`` from ``fulldomain.path`` to ``self.path`` and
        modify for a subdomain run.

        .. seealso:: :meth:`polyadcirc.pyADCIRC.fort15_management.subdomain`
        """

        f15.subdomain(self.fulldomain.path, self.path)

    def read_py_node(self):
        """
        Read in the subdomain to fulldomain node map
        
        Store as ::
            
            self.sub2full_node = dict()
        
        where key = subdomain node #, value = fulldomain node #
        """
        self.sub2full_node = {}
        with open(self.path+'/py.140', 'r') as fid:
            fid.readline() # skip header
            for line in fid:
                k, v = np.fromstring(line, dtype=int, sep=' ')
                self.sub2full_node[k] = v

    def read_py_ele(self):
        """
        Read in the subdomain to fulldomain element map
        
        Store as ::
            
            self.sub2full_element = dict()
        
        where key = subdomain element #, value = fulldomain element #
        """
        self.sub2full_element = {}
        with open(self.path+'/py.141', 'r') as fid:
            fid.readline() # skip header
            for line in fid:
                k, v = np.fromstring(line, dtype=int, sep=' ')
                self.sub2full_element[k] = v

    def read_bv_nodes(self):
        """
        Read in the nodes on the boundary and store in ``self.bv_nodes`` as a
        list.

        :rtype: list()
        :returns: list of boundary nodes
        """
        self.bv_nodes = []
        with open(os.path.join(self.path, 'bv.nodes'), 'r') as fid:
            for line in fid:
                self.bv_nodes.append(int(np.fromstring(line, sep=' ')[0]))
        return self.bv_nodes

    def update_sub2full_map(self):
        """
        Read in the subdomain to fulldomain element and node maps
        """
        #: dict() where key = subdomain node #, value = fulldomain node #
        self.read_py_node()
        #: dict() where key = subdomain element #, value = fulldomain element #
        self.read_py_ele()
        #: list of boundary nodes
        self.read_bv_fort13()

    def trim_fort13(self, old_fort13, new_fort13):
        """
        Trim ``old_fort13`` to match the nodes in this subdomain and save as
        ``new_fort13``. This only assumes that a ``py.140`` file exists.

        :param string old_fort13: path to the old ``fort.13`` file to be
            trimmed
        :param string new_fort13: path to save the new ``fort.13`` file
        """
        trim_fort13(old_fort13, new_fort13, os.path.join(self.path, 'py.140'))

    def trim_multiple_fort13(self, old_fort13, new_fort13):
        """
        Trim ``old_fort13`` to match the nodes in this subdomain and save as
        ``new_fort13``. This only assumes that a ``py.140`` file exists.

        :param string old_fort13: path to the old ``fort.13`` file to be
            trimmed
        :param string new_fort13: path to save the new ``fort.13`` file
        """
        trim_multiple_fort13(old_fort13, new_fort13, os.path.join(self.path,
            'py.140'))

    def read_bv_fort13(self):
        """
        Read the boundary value nodal values for Manning's n from
        ``self.fulldomain`` and save as a ``dict`` as ``self.bv_fort13``.
        """
        self.read_bv_nodes()
        self.bv_fort13 = f13.read_nodal_attr(self, self.path,
                                             nums=self.bv_nodes)

    def set_bv_fort13(self, mann_dict):
        """
        Replace the boundary nodal values with the boundary nodal values in the
        fulldomain.

        :param dict mann_dict: dictonary of nodal values
        
        :rtype: dict
        :returns: dictionary of nodal values

        """
        for k, v in self.bv_fort13.iteritems():
            mann_dict[k] = v
        return mann_dict

    def update_mann(self, data, path=None, default=None, file_name='fort.13'):
        """
        Write out fort.13 to path with the attributes contained in Data.  

        :type data: :class:`np.array` or :class:`dict`
        :param data: containing the nodal attribute information
        :type path: string or None
        :param path: the directory to which the fort.13 file will be written
        :type default: None or float
        :param default: default value
        :type file_name: string
        :param file_name: the name of the ``fort.13`` formatted file

        """
        data = self.set_bv_fort13(data)
        f13.update_mann(data, path, default, file_name)


def trim_fort13(old_fort13, new_fort13, pynode_map):
    """
    Trim ``old_fort13`` to match the nodes in this subdomain and save as
    ``new_fort13``. This only assumes that a ``py.140`` file exists.

    :param string old_fort13: path to the old ``fort.13`` file to be
        trimmed
    :param string new_fort13: path to save the new ``fort.13`` file
    """
    print pynode_map
    gensub.main13(None, old_fort13, new_fort13, pynode_map)

def trim_multiple_fort13(old_fort13, new_fort13, pynode_map):
    """
    Trim ``old_fort13`` to match the nodes in this subdomain and save as
    ``new_fort13``. This only assumes that a ``py.140`` file exists.

    :param string old_fort13: path to the old ``fort.13`` file to be
        trimmed
    :param string new_fort13: path to save the new ``fort.13`` file
    """
    size = comm.Get_size()
    rank = comm.Get_rank()

    print "len old, len new", len(old_fort13), len(new_fort13)

    for i in range(0+rank, len(old_fort13), size):
        if not os.path.exists(os.path.dirname(new_fort13[i])):
            os.makedirs(os.path.dirname(new_fort13[i]))
        trim_fort13(old_fort13[i], new_fort13[i], pynode_map)

def ellipse_properties(x, y, w):
    """
    Given a the (x,y) locations of the foci of the ellipse and the width return
    the center of the ellipse, width, height, and angle relative to the x-axis.

    :param double x: x-coordinates of the foci
    :param double y: y-coordinates of the foci
    :param double w: width of the ellipse
    :rtype: tuple of doubles
    :returns: (center_coordinates, width, height, angle_in_rads)

    """
    p1 = [x[0], y[0]]
    p2 = [x[1], y[1]]
    
    #center point
    xy = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2]		
    #distance between points
    d = ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**(0.5)	
    #theta to positive Xaxis
    angle = math.atan((p1[1] - p2[1])/(p1[0] - p2[0])) 
    #sin = math.sin(-angle)
    #cos = math.cos(-angle)
    #width will be the axis the points lie on
    width = 2*((0.5*d)**2 + (0.5*w)**2)**(0.5) 		
    height = w

    return (xy, width, height, angle*180/math.pi)

