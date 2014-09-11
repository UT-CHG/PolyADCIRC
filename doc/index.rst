.. PolyADCIRC documentation master file, created by
   sphinx-quickstart on Fri Jun  7 17:41:35 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PolyADCIRC's documentation!
==========================================

Python-based framework for running batches of parallel `ADCIRC <adcirc.org>`_
simulations with varying parameters (Manning's *n* and limited variable
bathymetry, etc). Includes documentation for a Python interface to a slightly
modified verion of :program:`GridData` (Griddata_v1.32.F90).
:program:`GridData` is a :program:`FORTRAN` program originally developed by
Seizo Tanaka (ST3) and C.H.Lab., University of Notre Dame.

All code documented here is written for Linux with a bash shell. It can be
modified for other shells. This code requires `GNU Parallel
<http://www.gnu.org/software/parallel/>`_ to be installed in order to run
properly.

Useful scripts are contained in ``examples/``
Python source code for this package is contained in ``polyadcirc/``


Contents:

.. toctree::
   :maxdepth: 2
   
   overview
   Running on TACC <running_on_TACC>
   submerged_wall
   Large Jobs <large_jobs>
   All about mapping landuse data to the mesh <landuse_stuff>
   todo_list

.. todo:: Add pictures and comment examples.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Disclaimer
==========
This code was originally developed for research purposes use at your own risk.
Hopefully, the documentation is clear. You might find bugs I have overlooked.
If you find something amiss please report this problem to me through GitHub or
submit a fix. Thanks!

This material is based upon work supported by the National Science Foundation
Graduate Research Fellowship under Grant No. DGE-1110007. Any opinion,
findings, and conclusions or recommendations expressed in this material are
those of the authors(s) and do not necessarily reflect the views of the
National Science Foundation.
