=====================
Large Jobs
=====================

PolyADCIRC runs batches of simulations of size ``num_of_parallel_runs``. PolyADCIRC
relies on `GNU Parallel <http://www.gnu.org/software/parallel/>`_ to handle
simultaneously running a batch of serial jobs in parallel. PolyADCIRC relies on
:program:`ibrun`, a `TACC
<http://www.tacc.utexas.edu/user-services/user-guides>`_ specific batch MPI
launch command to handle simulataneously running a batch of parallel jobs in
parallel. Based on user inputs PolyADCIRC writes the appropriate Bash scripts
which are run using the :meth:`subprocess.POpen` command. Once the batch size
(``num_of_parallel_runs``) gets too large the user may encounter ::

    tail: write error: Broken pipe

The current work around is to reduce your batch size and break your job up into
multiple jobs. These jobs may then be submitted to the queue and either run
independently or sequentially. When doing so make sure that the run scripts
specify a different ``save_dir``, ``save_file``, and ``script_name`` for each
job. After your jobs complete the data may be concatenated into a single file.
This file will have the same structure as if a single job was run. You might
also want to create a ``crontab`` to periodically clear our your ``.sge``
directory.

An example of this is in the ``examples/poly_walls/`` folder. The
``poly_wallsn.py`` files break a job into 7 parts and ``concatenate_many.py``
stiches the data from all 7 runs into a single file.

concatenate_pair
~~~~~~~~~~~~~~~~~

This file demonstrates concatenating data from two separate jobs.

Import necessary modules::

    import numpy as np
    import polyadcirc.run_framework.random_wall as rmw

Specifiy directories for the jobs that were run::

    base_dir = '/h1/lgraham/workspace'
    grid_dir = base_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
    save_dir1 = base_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall1'
    save_dir2 = base_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall2'
    basis_dir = base_dir + '/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

Specify the save file::

    save_file = 'py_save_file'

Load the data from both runs:: 

    main_run, domain, mann_pts1, wall_pts1, points1 = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir1, basis_dir)
    other_run, domain, mann_pts2, wall_pts2, points2 = rmw.loadmat(save_file,
        base_dir, grid_dir, save_dir2, basis_dir)
            
Concatenate the data from both runs and save to a
:class:`~polyadcirc.run_framework.random_wall.runSet` object::

    cated = main_run.concatenate(other_run, points1, points2)

Store the concatenated version of ``points`` in a dictonary object::

    mdat = dict()
    mdat['points'] = cated[1]

Concatenate and store ``mann_pts`` and ``wall_pts`` in the dictionary::
    
    mdat['mann_pts'] = np.concatenate((mann_pts1, mann_pts2), 
        axis = points1.ndim-1)
    mdat['wall_pts'] = np.concatenate((wall_pts1, wall_pts2), 
        axis = points1.ndim-1)

Save the data to a new save file in ``save_dir1`` as ``cat_file.mat``::

    main_run.update_mdict(mdat)
    main_run.save(mdat, 'cat_file')
                
concatenate_many
~~~~~~~~~~~~~~~~~~

This file demonstrates concatenating data from seven different jobs.

Import necessary modules::

    import polyadcirc.run_framework.random_wall as rmw

Specify the directories for the jobs and the base string for the ``save_dir``
and ``save_file``. The name pattern for the ``save_dir`` and ``save_file`` is
``name+str(n)`` where ``n`` indicates this the the files and directory for the
nth job::

    base_dir = '/h1/lgraham/workspace'
    grid_dir = base_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
    save_dir = base_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall'
    basis_dir = base_dir + '/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'

    save_file = 'py_save_file'

Load the data from the first job::

    main_run, domain, mann_pts, wall_pts, points = rmw.loadmat(save_file+'0',
        base_dir, grid_dir, save_dir+'_0', basis_dir)

Load and concatenate the data for the remaning runs::

    for i in xrange(1,7):
        save_file2 = save_file+str(i) # construct the save_file name
        save_dir2 = save_dir+'_'+str(i) # construct the save_dir name
        # load the data
        other_run, domain, mann_pts2, wall_pts2, points2 = rmw.loadmat(save_file2, 
            base_dir, grid_dir, save_dir2,basis_dir)
        # concatenate the data
        run, points = main_run.concatenate(other_run, points, points2)

Save the data to ``save_dir+'_0'`` ::

    mdat = dict()
    mdat['points'] = points

    main_run.update_mdict(mdat)
    main_run.save(mdat, 'poly7_file')

Notice that in this example ``mann_pts``
and ``wall_pts`` are NOT saved. These two arrays have been stitched together
into the ``points`` array using ``numpy.vstack((np.repeat(wall_points,
s_p_wall,1), mann_pts))`` in
:meth:`polyadcirc.run_framework.random_wall.runSet.run_points` into a single
array.
