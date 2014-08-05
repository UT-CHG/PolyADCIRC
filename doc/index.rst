.. PolyADCIRC documentation master file, created by
   sphinx-quickstart on Fri Jun  7 17:41:35 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PolyADCIRC's documentation!
===================================

Python-based framework for running batches of parallel `ADCIRC <adcirc.org>`_
simulations with varying parameters (Manning's *n* and limited variable
bathymetry, etc). Includes documentation for a Python interface to a slightly
modified verion of :program:`GridData` (Griddata_v1.32.F90).
:program:`GridData` is a :program:`FORTRAN` program originally developed by
Seizo Tanaka (ST3) and C.H.Lab., University of Notre Dame.

This code extends the :program:`PolyADCIRC` framework to work with a slightly
modifed version of :program:`Subdomain ADCIRC v.50`. :program:`Subdomain ADCIRC
v.50` was developed by Alper Altuntas and Jason Simon under the direction of
John Baugh; Department of Civil, Construction, and Enviromental Engineering
North Carolina State University (NCSU), Raleigh, NC 27695.

All code documented here is written for Linux with a bash shell. It can be
modified for other shells. This code requires `GNU Parallel
<http://www.gnu.org/software/parallel/>`_ to be installed in order to run
properly.

Contents:

.. toctree::
   :maxdepth: 2
   
   overview
   Running on Lonestar <running_on_lonestar>
   submerged_wall
   Large Jobs <large_jobs>
   All about mapping landuse data to the mesh <landuse_stuff>
   subdomain
   todo_list

.. todo:: Add pictures and comment examples.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


