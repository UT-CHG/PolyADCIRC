===========================
Limited Variable Bathymetry
===========================

The :class:`~polysim.run_framework.domain.domain` class has two built in methods that
give the user a limited ability to alter the bathymetry of the
:class:`~polysim.run_framework.domain.domain`. The class
`polysim.run_framework.random_wall.runSet` uses the
:meth:`polysim.pyADCIRC.fort14_management.update` method and
:meth:`polysim.run_framework.domain.domain.add_wall` method to run
:program:`PADCIRC` with variable Manning's *n* fields and variable bathymetry.
    
few_walls
~~~~~~~~~~~~~~~~~

This script models a submerged mound by setting the bathymetry to a specified
``wall_height`` at nodes contained in a rectangle defined by ``y_min``,
``y_max``, ``x_min``, and ``x_max``. To recude model error the user may desire
to refine the mesh in areas where the bathymetry will be altered.

Allow running from the command line using :command:`./few_walls.py`::

    #! /usr/bin/env/python

Import necessary modules::

    import polysim.run_framework.domain as dom
    import polysim.run_framework.random_wall as rmw
    import numpy as np

Store string references to important directories::

    adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
    grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
    save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/runs/few_walls'
    basis_dir = adcirc_dir
    +'/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

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

    script = "runWALLrun.sh"
    save_file = 'py_save_file'

Setting diffrerent ``script`` names allows for simulatenous runs of
:program:`PolySim` with differing ``grid_dir``, ``save_dir``, and
``basis_dir``.

Designate which :program:`ADCIRC` specific output files to collect data from::

    timeseries_files = ["fort.63"]
    nontimeseries_files = ["tinun.63", "maxvel.63", "maxele.63", "timemax63"]

The non-timeseries output ``timemax63`` is not an :program:`ADCIRC` output
file. The data from the ``fort.63`` file used to determine time of maximum
elevation in a post-processing step within the
:meth:`~polysim.run_framework.random_wall.runSet.run_points` method.

Set ``nprocs`` to be number of processors per :program:`PADCIRC` run. Set
``ppnode`` to be ``TpN`` (tasks per node) or the number of processors per node. On Lonestar,
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

Store ``fort.14`` and ``fort.15`` data in :class:`~polysim.run_framework.domain`::
    
    domain = dom.domain(grid_dir)
    domain.update()

Set Manning's *n* samples::

    lam_domain = np.array([[.07, .15], [.1, .2]])
    lam1 = np.linspace(lam_domain[0, 0], lam_domain[0, 1], 20)
    lam2 = np.linspace(lam_domain[1, 0], lam_domain[1, 1], 20)
    lam4 = 0.012
    lam1, lam2, lam4 = np.meshgrid(lam1, lam2, lam4)
    lam_samples = np.column_stack((lam1.ravel(), lam2.ravel(), lam4.ravel()))

    mann_pts = lam_samples.transpose()

Set wall samples::

    num_walls = 6

    ymin = np.linspace(1500, -1500, num_walls)
    xmin = 1420*np.ones(ymin.shape)
    xmax = 1580*np.ones(ymin.shape)
    ymax = 1500*np.ones(ymin.shape)
    wall_height = -2.5*np.ones(ymax.shape)
    # box_limits [xmin, xmax, ymin, ymax, wall_height]
    wall_points = np.column_stack((xmin, xmax, ymin, ymax, wall_height))
    wall_points = wall_points.transpose()
    
Tile ``mann_pts`` so that the number of columns is ``mann_pts.shape[1] *
num_walls``. This samples Manning's *n* points on the same regular grid for each
point in ``wall_points``. However, this need not be the case. See
``examples/walls_rand_man.py`` for an example with varying numbers of random
Manning's *n* samples per wall sample. 

.. seealso::

    :meth:`~polysim.run_framework.random_wall.runSet.run_points`.

Run samples::
    
    main_run.run_points(domain, wall_points, mann_pts, save_file, 
        num_procs = nprocs, procs_pnode = ppnode, ts_names = timeseries_files,
        nts_names = nontimeseries_files)


Job Submission Script
---------------------

An example submission script is included in ``examples/submission_script.sub``.
You should copy any scripts you wish to modify and run into a separate folder
in your ``$WORK`` directory. In these examples I am working from
``$WORK/landuse_bin``.  You will need to modify the lines that designate the
``adcirc_dir``, ``grid_dir``, ``save_dir``, and ``basis_dir`` to match your
directory structure.

To run :ref:`run-lonestar-test` you need to modify ``submission_script.sub``
so that the line ``#$ -M youremail@someplace.com`` has your e-mail. Then you
can submit it to the queue using::
    
    $ qsub submission_script.sub

To check on your job you can use the commend::

    $ qstat

Currently the output is saved to a :program:`python` formatted binary file called
``py_save_file.mat`` in ``save_dir``.

.. seealso::

    Lonestar User Guide `Running Applications
    <http://www.tacc.utexas.edu/user-services/user-guides/lonestar-user-guide#running>`_

    `Numpy for MATLAB users <http://wiki.scipy.org/NumPy_for_Matlab_Users>`_
    
    `Numpy Input/Output (ascii/binary)
    <http://wiki.scipy.org/Cookbook/InputOutput>`_

    `SciPy Input/Output
    <http://docs.scipy.org/doc/scipy/reference/tutorial/io.html>`_
  
load_few_walls
~~~~~~~~~~~~~~~

This script is very similar to ``examples/load_test.py``.

Import necessary modules::
    
    import polysim.run_framework.random_wall as rmw
    import polysim.pyADCIRC.plotADCIRC as pa

Set up local directory and file references::
    
    base_dir = '/h1/lgraham/workspace'
    grid_dir = base_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
    save_dir = base_dir + '/ADCIRC_landuse/Inlet/runs/few_walls'
    basis_dir = base_dir + '/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

    save_file = 'py_save_file.mat'

Load the run set up and data::

    main_run, domain, mann_pts, wall_pts, points = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir, basis_dir)

Now the data is availiable for plotting methods in
:mod:`~polysim.pyADCIRC.plotADCIRC`.

Determine the total number of samples modeled::

    pt_nos = range(points.shape[-1])

Plot the non-timeseries data for all of the samples modeled::

    pa.nts_pcolor(main_run.nts_data, domain, points = pt_nos, path = save_dir)

