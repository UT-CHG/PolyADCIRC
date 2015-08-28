# Copyright (C) 2013 Lindley Graham

"""
See :class:`domain`
"""
from polyadcirc.pyADCIRC.basic import pickleable 
import polyadcirc.pyADCIRC.prep_management as prep
import subprocess, os
import polyadcirc.pyADCIRC.fort15_management as f15
import polyadcirc.pyADCIRC.fort14_management as f14
import polyadcirc.pyADCIRC.fort13_management as f13
import polyadcirc.pyADCIRC.plotADCIRC as plot
import numpy as np
from scipy.interpolate import griddata

class domain(pickleable):
    """
    :class:`~polyadcirc.run_framework.domain` 
    Objects of this class contain all the data needed by
    :class:`~polyadcirc.run_framework.random_manningsn`
    and :class:`~polyadcirc.pyADCIRC.plotADCIRC` for particular mesh(s) or
    grid(s)

    path
        full path to the directory containing the ``fort.##`` files for this
        particular mesh(s) or grid(s)
    node_num
        number of nodes
    element_num
        number of elements
    node
        list of nodes
    element
        list of elements where each element is a list of nodes
    manningsn_default
        default Manning's *n* value 
    manningsn_num
        number of non-default nodes
    time
        instance of :class:`~polyadcirc.pyADCIRC.basic.time` class
    make_domain_map
        (boolean) whether or not a domain map has been created

    """
    def __init__(self, path, node_num=0, element_num=0, node=None,
                 element=None):
        """
        Initializatoin
        """
        #: int, number of nodes
        self.node_num = node_num
        #: int, number of elements
        self.element_num = element_num
        if node or element:
            #: boolean, whether or not a domain map has been created
            self.make_domain_map = False
            #: list(), list of nodes
            self.node = node
            #: list(), list of elements where each element is a list of nodes
            self.element = element
        else:
            self.make_domain_map = True
            self.node = dict()
            self.element = dict()
        #: string, full path to the dir containing the ``fort.##`` files
        self.path = path
        super(domain, self).__init__()

    def read_spatial_grid_header(self):
        """
        Reads in spatial grid header from ``fort.14`` file in self.path

        See :meth:`polyadcirc.pyADCIRC.fort14_management.read_spatial_grid`       
        """
        f14.read_spatial_grid_header(self, self.path)

    def read_spatial_grid(self):
        """
        Reads in spatial grid from ``fort.14`` file in self.path

        See :meth:`polyadcirc.pyADCIRC.fort14_management.read_spatial_grid`       
        """
        f14.read_spatial_grid(self, self.path)

    def read_recording_data(self):
        """
        Reads in recording information from ``fort.15`` in self.path

        See :meth:`polyadcirc.pyADCIRC.fort15_management.read_recording_data`
        """
        f15.read_recording_data(self, self.path)

    def update(self, path=None):
        """
        Sets the directory containing files for this domain to self.path

        Reads in data from ``fort.14`` and ``fort.15`` files and updates self
        accordingly

        :type path: string or None
        :param path: directory containing ``fort.##`` files

        See :meth:`~polyadcirc.pyADCIRC.fort15_management.read_spatial_grid` 
        See :meth:`~polyadcirc.pyADCIRC.fort15_management.read_recording_data` 

        """
        if path:
            self.path = path
        # Read in the fort.14 file
        self.read_spatial_grid() 
        # Read in the fort.15 file
        self.read_recording_data()

    def make_node_to_element_map(self):
        """
        Create the node to element map
        """
        for k, v in self.node.iteritems():
            v.element = []
            for i, w in self.element.iteritems():
                if k in w:
                    v.element.append(i)

    def array_bathymetry(self):
        """
        :rtype: :class:`np.array` of size(1, node_num)
        :returns: array containing the bathymetry at all nodes in numerical
        order

        """
        bathymetry = np.array([node.bathymetry for node in self.node.values()])
        self.bathymetry = bathymetry
        return self.bathymetry
    
    def array_x(self):
        """
        :rtype: :class:`np.array` of size(1, node_num)
        :returns: array containing the x locations at all nodes in numerical
            order

        """
        return np.array([node.x for node in self.node.values()])   
    
    def array_y(self):
        """
        :rtype: :class:`np.array` of size(1, node_num)
        :returns: array containing the y locations at all nodes in numerical
            order

        """
        return np.array([node.y for node in self.node.values()])
    
    def array_manningsn(self):
        """
        :rtype: :class:`np.array` of size(1, node_num)
        :returns: array of containing the Manning's *n* value at all nodes in
            numerical order

        """
        return np.array([node.manningsn for node in self.node.values()]) 

    def dict_bathymetry(self):
        """
        :rtype: :class:`dict`
        :returns: ``key`` -- node number, ``value`` -- bathymetry

        """
        temp = dict()
        for k, node in self.node.iteritems():
            temp[k] = node.bathymetry
        return temp

    def dict_manningsn(self):
        """
        :rtype: :class:`dict`
        :returns: ``key`` -- node number, ``value`` -- manningsn

        """
        temp = dict()
        for k, node in self.node.iteritems():
            temp[k] = node.manningsn
        return temp

    def read_nodal_attr(self, path=None, file_name='fort.13'):
        """
        Load in nodal attributes from a ``*.13`` file (only does Manning's *n*
        for now) and return a dictonary (like a MATLAB struct) with these
        attributes).

        :type path: string or None
        :param path: directory containing ``fort.13`` formatted file
        :param string file_name: ``fort.13`` formatted file name
        :returns: See :meth:`~polyadcirc.pyADCIRC.fort13_management.read_nodal_attr`

        """
        if path == None:
            path = self.path
        return f13.read_nodal_attr(self, path, file_name)

    def read_default(self, path=None, file_name='fort.13'):
        """
        Read in default nodal value from a ``*.13`` file

        :type path: string or None
        :param path: directory containing ``fort.13`` formatted file
        :param string file_name: ``fort.13`` formatted file name
        :returns: See :meth:`~polyadcirc.pyADCIRCfort13_management.read_default`

        """
        if path == None:
            path = self.path
        return f13.read_default(self, path, file_name)

    def get_Triangulation(self, path=None, save=True, show=False, ext='.eps',
                          ics=2):
        """
        :type path: None or string
        :param string path: directory containing ``figs/`` folder
        :param boolean save: flag
        :param boolean show: flag
        :returns: See :meth:`~polyadcirc.pyADCIRC.plotADCIRC.get_Triangulation`

        """
        return plot.get_Triangulation(self, path, save, show, ext=ext, ics=ics)

    def plot_bathymetry(self, path=None, save=True, show=False, ext='.eps',
                        ics=2):
        """
        :type path: None or string
        :param string path: directory containing ``figs/`` folder
        :param boolean save: flag
        :param boolean show: flag
        :returns: See :meth:`~polyadcirc.pyADCIRC.plotADCIRC.bathymetry`

        """
        return plot.bathymetry(self, path, save, show, ext=ext, ics=ics)

    def plot_station_locations(self, path=None, bathymetry=False, 
                               save=True, show=False, ext='.eps',
                               ics=2):
        """
        :param string path: directory containing ``figs/`` folder
        :type bathymetry: boolean
        :param bathymetry: flag whether or not to plot bathymetry in the
            background 
        :param boolean save: flag
        :param boolean show: flag
        :returns: See :meth:`~polyadcirc.pyADCIRC.plotADCIRC.station_locations`

        """
        return plot.station_locations(self, path, bathymetry, save, show,
                                      ext=ext, ics=ics)

    def adjust(self, x_lims=None, b_lims=None, path=None, plotb=False):
        """
        Adds a bathymetry between x-locations defined by ``x_lims`` with
        bathymetry linearly interpolated between ``b_lims``

        :param list() x_lims: [x_min, x_max]
        :param list() b_lims: [b_min, b_max]
        :type path: string or None
        :param path: directory containing the ``fort.14`` to be adjusted

        """
        if path == None:
            path = self.path
        if x_lims == None:
            x_lims = [0, 0]
            x_lims[0] = np.min(np.array([node.x for node in \
                    self.node.values()]))  
            x_lims[1] = np.max(np.array([node.x for node in \
                    self.node.values()]))
        for n in self.node.values():
            n.bathymetry += adjust_factor(n.x, x_lims, b_lims)
        if plotb:
            self.plot_bathymetry(path)
 
    def add_wall(self, box_limits, wall_height=-2, path=None, plotb=False,
                 save=False, show=False):
        """

        :type path: string or None
        :param path: directory containing the ``fort.14`` to be adjusted
	:param box_limits: [xmin, xmax, ymin, ymax] 

        adds a land wall of default 2 m in area defined by box_limits
        """
        if path == None:
            path = self.path
        for n in self.node.values():
            if box_limits[0] <= n.x <= box_limits[1]: 
                if  box_limits[2] <= n.y <= box_limits[3]:
                    n.bathymetry = wall_height
        if plotb:
            self.plot_bathymetry(path, save, show)

    def set_station_bathymetry(self, key='fort61', method='linear'):
        #pylint: disable-msg=E1101
        """
        Sets they bathymetry for all stations by interpolating w.r.t. the nodal
        locations

        :param string key: key for domain.stations[key]
        :param string method: linear interpolation method see
            :meth:`scipy.interpolate.griddata` 

        """
        points = np.array([[n.x, n.y] for n in self.node.itervalues()])
        station_locs = np.array([[s.x, s.y] for s in self.stations[key]])
        station_bath = griddata(points, self.array_bathymetry(), 
                                station_locs, method)
        for i, s in enumerate(self.stations[key]):
            s.bathymetry = station_bath[i]
    
    def run(self, num_procs, base_dir, input_dir=None, global_dir=None, 
            write_option=None, num_writers=None, LorS=None, R=False):
        """
        Preprocess and run ADCIRC on this domain

        .. seealso:: `Generic ADCIRC Command Line
        Options<http://adcirc.org/home/documentation/generic-adcirc-command-line-options/>`_

        :param int num_procs: number of processors for this ADCIRC run
        :param string base_dir: directory containing the padcirc executables
        :param string input_dir: directory containing the input files
        :param string global_dir: directory to write fulldomain output files to
        :param string write_option: (optional) specifiy ``W`` or ``Ws`` flag
        :param int num_writers: number of MPI process to dedicate soley to the
            task of writing ascii files
        :param string LorS: (optional) specify ``L`` or ``S`` flag
        :param string R: (optional) specify ``R`` flag

        """
        if base_dir == None:
            base_dir = self.path
        if input_dir == None:
            input_dir = self.path
        if global_dir == None:
            global_dir = self.path
        if not os.path.exists(self.path+'/adcprep'):
            os.symlink(base_dir+'/adcprep', self.path+'/adcprep')
        prep.write_1(self.path, num_procs)
        prep.write_2(self.path, num_procs)
        subprocess.call('./adcprep < in.prep1 > prep_o.txt', shell=True, 
                        cwd=self.path) 
        subprocess.call('./adcprep < in.prep2 > prep_o.txt', shell=True, 
                        cwd=self.path) 
        command = ['ibrun', 'padcirc', '-I', input_dir, '-O', global_dir]
        if LorS:
            command.append('-'+LorS)
        if R:
            command.append('-'+R)
        if write_option:
            command.append('-'+write_option)
            command.append(str(num_writers))
        subprocess.call(command, cwd=base_dir)
 
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
        f13.update_mann(data, path, default, file_name)   

    def find_neighbors(self):
        """
        Determine the neighbors of each of the nodes and store in
        ``self.node[#].neighbors`` as a ``set()``.
        """
        for n in self.node.itervalues():
            n.neighbors = set()
        for e in self.element.itervalues():
            self.node[e[0]].neighbors.add(e[1])
            self.node[e[0]].neighbors.add(e[2])
            self.node[e[1]].neighbors.add(e[0])
            self.node[e[1]].neighbors.add(e[2])
            self.node[e[2]].neighbors.add(e[1])
            self.node[e[2]].neighbors.add(e[0])

def adjust_factor(x, x_lims, b_lims=None):
    """
    :param float x: current x value
    :param float x_lims: box of x values to adjust
    :param float b_lims: bathy adj at x_lims
    :rtype: float
    :returns: b = bathy adjustment

    """
    if b_lims == None:
        return 0
    if x < x_lims[0] or x > x_lims[1]:
        return 0
    else:
        value = b_lims[0]
        slope = (b_lims[1]-b_lims[0]) / (x_lims[1]-x_lims[0])
        value += (x-x_lims[0])*slope
        return value 

