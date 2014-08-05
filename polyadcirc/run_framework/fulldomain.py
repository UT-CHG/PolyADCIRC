# -*- coding: utf-8 -*-
"""
This module contains a set of methods and a class for interacting with NCSU
Subdomain Modeling Python code and associated files. The focus of this module
is the :class:`fulldomain`.
"""

import polysim.run_framework.domain as dom
import subprocess, glob, sys

class fulldomain(dom.domain):
    """
    Objects of this class contain all the data needed by :mod:`py.genbcs`,
    :mod:`py.genfull`, and :mod:`py.gensub` for a particular full domain
    mesh/grid. References to :class:`polysim.run_framework.subdomain` objects
    are also contained in an instantiation of this class.
    """
    def __init__(self, path, subdomains = None, node_num = 0, element_num = 0,
            node = None, element = None):
        """
        Initialization
        """
        super(fulldomain, self).__init__(path, node_num, element_num, node,
                element)
        # figure out where the script dir for the ncsu subdomain code is
        for sys_path in sys.path:
            potential_file_list = glob.glob(sys_path+'/py')
            if potential_file_list:
                self.script_dir = potential_file_list[0]
                break

        #: list() of :class:`~polysim.run_framework.subdomain`
        if subdomains == None:
            self.subdomains = list()
        else:
            self.subdomains = subdomains

    def add_subdomain(self, subdomain):
        """
        Adds subdomain to self.subdomains.

        :type subdomain: :class:`~polysim.run_framework.subdomain`
        :param subdomain: subdomain within this domain

        """
        self.subdomains.append(subdomain)
        subdomain.fulldomain = self

    def update_subdomains(self):
        """
        Update relational references between fulldomain and it's subdomains by
        setting subdomain.fulldomain = self
        """
        for subdomain in self.subdomains:
            subdomain.fulldomain = self

    def genfull(self, noutgs = 1, nspoolgs = 1, subdomains = None):
        """
        Generate the full domain control file, ``fort.015``, and save it to
        ``self.path``.

        :param int noutgs: flag controlling whether or not ``fort.06*`` will be
            written out
        :param int nspoolgs: the number of timesteps at which information is
            written to the new output files ``fort.06*``
        :rtype: string
        :returns: command line for invoking genfull.py

        """
        if subdomains == None:
            subdomains = self.subdomains
        if len(subdomains) == 0:
            with open(self.path+'/genfull.in', 'w') as fid:
                fid.write(str(noutgs)+'\n')
                fid.write(str(nspoolgs)+'\n')
            command = "python "+self.script_dir+" -a "+self.path+'/ '
            command += " < genfull.in"
            subprocess.call(command, shell = True, cwd = self.path)
        else:
            with open(self.path+'/genfull.in', 'w') as fid:
                fid.write(str(noutgs)+'\n')
                fid.write(str(nspoolgs)+'\n')
                for subdomain in subdomains:
                    subdomain.nspoolgs = nspoolgs
                    fid.write(subdomain.path+'/\n')
            command = "python "+self.script_dir+"/genfull.py -s "+self.path+'/ '
            command += str(len(subdomains)) + " < genfull.in"
            subprocess.call(command, shell = True, cwd = self.path)
        return command

    def genbcss(self, forcing_freq = None, dt = None, nspoolgs = None, h0 =
            None): 
        """
        Generate the ``fort.019`` files for the subdomains. This requires the
        presence of the output files from a fulldomain run, ``fort.06*``.

        :param list() forcing_freq: number of timesteps at which infomration
            is written to a boudnary conditions file (``fort.019``)
        :param list() dt: One timestep in seconds
        :param list() nspoolgs: the number of timesteps at which information is
            written to the new output files ``fort.06*``
        :param list() h0: minimum water depth for a node to be wet
        :rtype: list()
        :return: command lines for invoking genbcs.py

        """
        commands = []
        if self.check_fulldomain():
            if forcing_freq == None:
                forcing_freq =  [1 for i in self.subdomains]
            if dt == None:
                dt = [self.time.dt for i in self.subdomains]
            if nspoolgs == None:
                nspoolgs = [1 for i in self.subdomains]
            if h0 == None:
                h0 = [None for s in self.subdomains]
            for f, d, ns, h, subdomain in zip(forcing_freq, dt, nspoolgs, h0,
                    self.subdomains):
                commands.append(subdomain.genbcs(f, d, ns, h))
        else:
            print "Output files from the fulldomain run do not exist"
        return commands

    def check_fulldomain(self):
        """
        Check to see if the ``fort.06*`` and ``PE*/fort.065`` files exist

        :rtype: boolean
        :returns: False if the ``fort.06*`` files don't exist

        """
        fort06 = glob.glob(self.path+'/fort.06*')
        fort065 = glob.glob(self.path+'/PE*/fort.065')
        if len(fort06) > 0 and len(fort065) > 0:
            return True
        else:
            return False

    def check_subdomains(self):
        """
        Check all the subdomains to make sure the ``fort.019`` file exists

        :rtype: boolean
        :returns: False if ``fort.019`` is missing from at least one of the
            subdomains

        """
        for sub in self.subdomains:
            if not(sub.check()):
                return False
            else:
                return True

    def setup_all(self):
        """
        Set up all of the subdomains
        """
        for sub in self.subdomains:
            sub.setup()


