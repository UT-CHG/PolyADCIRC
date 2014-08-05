===================
Running on TACC
===================

To run a set of simulations on `Stampede <http://www.tacc.utexas.edu/user-services/user-guides/stampede-user-guide>`_ you need to load the following modules::

    $ module load git
    $ module load python
    $ module load intel
    $ module load mvapich
    $ module load mkl 

To make thse your default modules either add these commands to your ``~/.bashrc`` or :command:`module save`.

.. seealso::

    Stampede User Guide `Modules <http://http://www.tacc.utexas.edu/user-services/user-guides/stampede-user-guide#computing:modules>`_

File System Setup
-----------------

The major file systems available on `Stampede <http://www.tacc.utexas.edu/user-services/user-guides/stampede-user-guide>`_ are ``$HOME``, ``$WORK``,
``$SCRATCH``, ``/tmp``, and ``$ARCHIVE``. 

Installation
~~~~~~~~~~~~

You can install PolyADCIRC in the ``$HOME`` directory as described in the
:ref:`overview`. If you want to use the cutting edge version from the git repo,
I would sugguest putting the git repo containing the Polysim directory in
``$HOME``.  Files are not backed up in the``$WORK`` or ``$SCRATCH``
directories, so if you need to put the ``landuse.git`` repo in either of these
locations use the ``--separate-gir-dir=$HOME/someplace`` option. 

To clone the git repo containing the PolyADCIRC directory::

    $ git clone username@ices-workstation:/org/groups/chg/lgraham/PolyADCIRC.git

or::

    $ git clone git@github.com:lcgraham/PolyADCIRC.git

Since this code is currently in development it is not in a public repository.
If you would like a copy of the code let me know.

Input/Output Directory Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This code currently assumes use of v50 of :program:`ADCIRC`. The top directory
containing the ``work``, ``src``, etc. folders for :program:`ADCIRC` should be
kept in the ``$WORK`` directory due to memory quota constraints.

Within the ``work/`` folder of your :program:`ADCIRC` directory you have 2
options with regard to file structure

    0. (RECOMMENDED) Copy ``/h1/lgraham/group_mts_012914/Inlet_test`` to a
       convienent location.    

    1. (NOT RECOMMENDED) Clone the git repo ``ADCIRC_landuse`` here and
       add/alter data/input files ::
            
            $ git clone --separate-git-dir=$HOME/ADCIRC_landuse ices-workstation:/org/groups/chg/lgraham/ADCIRC_landuse.git
            $ cd ADCIRC_landuse
            $ git checkout --track origin/stampede

    2. Create your own directory and add any missing data/input files. The
       recommended directory structure is as follows ::

            adcirc_dir/
                src/
                swan/
                util/
                ...
                work/
                    ADCIRC_landuse/ (THIS YOU CLONE OR CREATE)
                        grid_name1/
                        ...
                        grid_namen/
                            inputs/
                                grid_dir1/
                                grid_dir2/
                                ...
                            runs/
                                fort.13
                                README
                                save_dir1/
                                ...
                                save_dirn/
                            landuse_basis/
                                basis_dir1/
                                ...
                                basis_dirn

       The ``ADCIRC_landuse/`` MUST be in the ``work/`` (``base_dir`` used by
       :class:`~polyadcirc.run_framwork.random_manningsn.runSet`) directory of
       your :program:`ADCIRC` build. The ``ADCIRC_landuse/`` directory can be
       renamed but it MUST contain any ``grid_dir``, ``save_dir``, or
       ``basis_dir`` used by
       :class:`~polyadcirc.run_framwork.random_manningsn.runSet`. There must be a
       ``fort.13`` file specific to ``grid_dir`` stored in the directory
       containing the ``save_dir``. 

.. seealso::

    Stampede User Guide `File Systems
    <http://www.tacc.utexas.edu/user-services/user-guides/stampede-user-guide#overview:filesystems>`_
    
    :class:`~polyadcirc.run_framework.random_manningsn.runSet` class documenation

    Git Documentation `Remote Branches
    <http://git-scm.com/book/en/Git-Branching-Remote-Branches>`_
    
Python Scripts
--------------

The following submission and Python scripts should be located in the
directory ``PolyADCIRC/examples/``.

Currently my workflow has been something like...

On Stampede::

    $ cd $WORK/landuse_bin
    $ qsub submission_script.sub
    $ qstat

Once the job has finished running, check the ``$JOB_NAME.$JOB_ID`` file for errors.

.. code-block:: none 
    
    $ scp $WORK/v50_ADCIRC/work/ADCIRC_landuse/Inlet/runs/my_run/py_save_file.mat
    ices-workstation.ices.utexas.edu:~/workspace/ADCIRC_landuse/Inlet/runs/my_run.

On my ICES workstation in ``bin/`` start an interactive Python session using
:command:`python` or :program:`ipython`

.. code-block:: python

    >>> run load_test.py
    >>> whos

Now the data collected from the :program:`PADCIRC` runs are accessible in
Python for plotting and analysis. The ``py_save_file.mat`` file is also
readable by MATLAB and Octave.
    
.. _run-stampede-test:

run_stampede_test
~~~~~~~~~~~~~~~~~

This is the script I've been using for my current setup. This is the script
that should be modified for future runs. There are other scripts in the
``examples/`` directory which may be helpful, although minor changes may be
required.

Allow running from the command line using :command:`./run_stampede_test.py`::

    #! /usr/bin/env/python

Import necessary modules::

    import polyadcirc.run_framework.domain as dom
    import polyadcirc.run_framework.random_manningsn as rmn
    import numpy as np
    import os, glob

Store string references to important directories::

  adcirc_dir = '/work/01837/lcgraham/v50release_130626/work'
  grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/inputs/tides'
  save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/runs/vel_test'
  basis_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/landuse_basis/gap/bands'
  # assume that in.prep* files are one directory up from basis_dir

``grid_dir``
    directory where the ``fort.15``, ``fort.14``, and ``fort.22`` files are
    stored

``save_dir``
    directory where the ``RF_directory_*/`` are created and job specific data
    is saved

``basis_dir``
    directory containing the ``landuse_##`` folders which each contain a
    ``fort.13`` file specific to the landuse classification

``adcirc_dir``
    directory containing compiled :program:`ADCIRC` executables

Set run specific names of ``script`` and ``save_file``::

    script = "runRUNrun.sh"
    save_file = 'py_save_file'

Setting diffrerent ``script`` names allows for simulatenous runs of
:program:`PolyADCIRC` with differing ``grid_dir``, ``save_dir``, and
``basis_dir``.

Designate which :program:`ADCIRC` specific output files to collect data from::

    timeseries_files = ["fort.61", "fort.63", "fort.62", "fort.64"]
    nontimeseries_files = ["tinun.63", "maxvel.63"]

Set ``nprocs`` to be number of processors per :program:`PADCIRC` run. Set
``ppnode`` to be ``TpN`` (tasks per node) or the number of processors per node. On Stampede,
12 is the number of processors per node. Set ``NoN`` to be number of nodes requested
by the ``submission_script.sub``. See ``-pe `` line in submission_script
``<TpN>way<NoN x 12>``.::

    nprocs = 2
    ppnode = 12
    NoN = 2
    num_of_parallel_runs = (ppnode*NoN)/nprocs # procs_pnode * NoN / nproc

Store directory references and set up random field directories::
   
    main_run = rmn.runSet(grid_dir, save_dir, basis_dir, num_of_parallel_runs,
            base_dir = adcirc_dir, script_name = script)
    main_run.initialize_random_field_directories(num_procs = nprocs)

Store ``fort.14`` and ``fort.15`` data in :class:`~polyadcirc.run_framework.domain`::
    
    domain = dom.domain(grid_dir)
    domain.update()

Set samples::

    lam_domain = np.array([[.02, .2], [.02, .2], [.02, .2]])
    lam1 = np.linspace(lam_domain[0, 0], lam_domain[0, 1], 3)
    lam2 = np.linspace(lam_domain[1, 0], lam_domain[1, 1], 3)
    lam3 = np.linspace(lam_domain[2, 0], lam_domain[2, 1], 3)
    lam4 = 0.02
    lam1, lam2, lam3, lam4 = np.meshgrid(lam1, lam2, lam3, lam4)
    lam_samples = np.column_stack((lam1.ravel(), lam2.ravel(), lam3.ravel(),
    lam4.ravel()))

    mann_pts = lam_samples.transpose()


.. note::

    ``mann_pts`` must have the shape (number_of_landclasses, number_of_samples)
    in this case that is (4, 27)

Run samples::
    
    main_run.run_points(domain, mann_pts, save_file, num_procs = nprocs,
        procs_pnode = ppnode, ts_names = timeseries_files, 
        nts_names = nontimeseries_files, screenout=True) 
 
Job Submission Script
---------------------

An example submission script is included in
``examples/submission_script.sub``. To run on Stampede you will need to rewrite
the ``qsub`` script as a ``sbatch`` submission script and modify the the
requested nodes as Stampede has a different number of cores per node than
Stampede. These types of python scripts create a lot of hostfiles in your
``$HOME\.sge`` (``$HOME\.slurm``) so you should schedule a cron tab that
periodially wipes old files.
You should copy any scripts you wish to modify and run into a separate folder
in your ``$WORK`` directory. In these examples I am working from
``$WORK/landuse_bin``.  You will need to modify the lines that designate the
``adcirc_dir``, ``grid_dir``, ``save_dir``, and ``basis_dir`` to match your
directory structure.

To run :ref:`run-stampede-test` you need to modify ``submission_script.sub``
so that the line ``#$ -M youremail@someplace.com`` has your e-mail. Then you
can submit it to the queue using::
    
    $ qsub submission_script.sub

To check on your job you can use the commend::

    $ qstat

Currently the output is saved to a :program:`python` formatted binary file called
``py_save_file.mat`` in ``save_dir``.

.. seealso::

    Stampede User Guide `Running Applications
    <http://www.tacc.utexas.edu/user-services/user-guides/stampede-user-guide#running>`_

    `Numpy for MATLAB users <http://wiki.scipy.org/NumPy_for_Matlab_Users>`_
    
    `Numpy Input/Output (ascii/binary)
    <http://wiki.scipy.org/Cookbook/InputOutput>`_

    `SciPy Input/Output
    <http://docs.scipy.org/doc/scipy/reference/tutorial/io.html>`_
  
load_test
~~~~~~~~~~~~~~~

To run this code on my workstation I generally have the ``sl6`` and ``python``
(or ``epd``) modules loaded (:command:`module load module_name`). I would also
recommend installing the latest versions of `numpy <numpy.org>`_, `scipy
<scipy.org>`_, and `matplotlib <matplotlib.org>`_.

Import necessary modules::

    import polyadcirc.pyADCIRC.plotADCIRC as pa
    import polyadcirc.run_framework.random_manningsn as rmn

Set up local directory and file references::

    save_file = 'py_save_file.mat'
    base_dir = '/h1/lgraham/workspace'

    grid_dir = base_dir+'/ADCIRC_landuse/Inlet/inputs/tides'
    save_dir = base_dir+'/ADCIRC_landuse/Inlet/runs/vel_test'
    basis_dir = base_dir+'/ADCIRC_landuse/Inlet/landuse_basis/gap/bands'

Load the run set up and data::

    main_run, domain, mann_pts = rmn.loadmat(save_file, base_dir, grid_dir,
            save_dir, basis_dir)

Now the data is availiable for plotting methods in
:mod:`~polyadcirc.pyADCIRC.plotADCIRC`.
