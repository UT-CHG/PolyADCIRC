# Copyright (C) 2013 Lindley Graham

"""
This package is a Python-based framework for running batches of parallel ADCIRC
simulations with varying parameters (Manning's n and limited variable
bathymetry, etc). Includes documentation for a Python interface to a slightly 
modified verion of GridData (Griddata_v1.32.F90). GridData is a FORTRAN program
originally developed by Seizo Tanaka (ST3) and C.H.Lab., University of Notre
Dame.

All code documented here is written for Linux with a bash shell. It can be
modified for other shells. This code requires GNU Parallel to be installed in
order to run properly.

This package contaings three subpackages

* :mod:`~polyadcirc.pyADCIRC` a set of modules primarily for I/O with
  :program:`ADCIRC` through text files
* :mod:`~polyadcirc.run_framework` a set of modules used to run batches of
  :program:`PADCIRC` in parallel
* :mod:`~polyadcirc.pyGriddata` a set modules and some FORTRAN code used to
  create sets of nodal data for use by :program:`PADCIRC` 
  

"""
__all__ = ['util', 'pyADCIRC', 'run_framework', 'pyGriddata']
