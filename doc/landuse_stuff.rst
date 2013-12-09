=============================================
"All" about land use and land classifications
=============================================

This code creates the set of landuse basis folders, ``landuse_##``, required by
:class:`polysim.random_manningsn.runSet`.  All the below code is set up to be
run on a workstation. Modifications would be
needed to run it on Lonestar.

Preparing basis vector files from GAP/NLCD data
-----------------------------------------------

The ``prep_from_data.py`` script in ``examples`` prepares ``*.table`` and
``*.13`` files needed for ``T:**_manning.table-->fort.13`` and creates the n x
m matrix of multiplier factors where n = # nodes, and m = # land classification
values. It works ok, but could use some polishing.

Import the necessary modules::

   import polysim.pyGriddata.table_management as tm
   import polysim.pyGriddata.gridObject as go
   import polysim.pyGriddata.prep_mesh as prep

Read in the ``CCAP_Manning.table`` file in the current working directory.::

    table = tm.read_table('CCAP_Manning.table')

To read in multiple ``*.table`` files use::

    tables = tm.read_tables()

Create necessary :class:`~polysim.pyGriddata.table_management.gapInfo`
objects, one for each ``*.asc`` file, requires ``*.asc`` files in current
working directory::

    gap15 = tm.gapInfo('15N.asc', table, 2, 15 )
    gap16_1 = tm.gapInfo('16N_part1.asc', table, 2, 16 )
    gap16_2 = tm.gapInfo('16N_part2.asc', table, 2, 16 )
    gap17 = tm.gapInfo('17N.asc', table, 2, 17)

Create a :class:`~polysim.pyGriddata.gridObject.gridInfo` object and store
references to the :class:`~polysim.pyGriddata.table_management.gapInfo`
objects. Currently this assumes that the ``flagged_fort.14`` (or ``fort.14``)
file is in the current working directory::

    gap_list = [gap15, gap16_1]
    grid = go.gridInfo('flagged_fort.14', gap_list)

Explictly set the ``grid_dir`` to the current working directory::

    grid_dir = '.'
    
    
Set up files to run :program:`Griddata_v1.32.F90` to create the landuse basis
folders. Appropriately flag the nodes of the ``fort.14`` file. Finally, run
:program:`Griddata_v1.32.F90` to map the landuse classification data to the
mesh::

    prep.prep_all(grid, path = grid_dir)
    prep.prep_test(grid, path = grid_dir)

    prep.prep_all(grid, path = grid_dir)
    prep.prep_test(grid, path = grid_dir)

This code also maps the landuse classifcation data to the mesh for a
test case for verifcation purposes. The method
:meth:`~polysim.pyGriddata.prep_mesh.compare` generates a set of images in a
``figs/`` folder for visual verification::

    prep.compare(basis_dir = grid_dir)

Comparing the Python vs. :program:`Griddata_v1.32.F90` Reconstructions
----------------------------------------------------------------------

To compare the Python vs. the "pure" :program:`Griddata_v1.32.F90`
constructions, I usually move the ``test`` and ``landuse_*/`` folders out of
the ``bin/`` directory into another folder. The ``fort.14`` file needs to also
be copied to this folder. Within this folder I do the following::

    >>> fm.mkdir('figs')
    >>> prep.compare(basis_dir = '.')


``basis_dir`` is the folder where the ``test`` and ``landuse_*`` folders are
located in addition to the ``fort.14`` file. A set of plots will be created in
``figs``. The values in the ``difference.png`` figure should be very small.


Manufacturing GAP data
----------------------

This section deals mostly with how to use
:mod:`~polysim.pyGriddata.manufacture_gap`. The relevant example scripts
for this section located in ``examples/`` are
    
    * :mod:`manu_prep_comp.py`, requires ``rand_Manning.table`` file
    * :mod:`bands.py`, requires ``rand_Manning.table`` file

What follows is an explaination of the script ``bands.py``, the script
``manu_prep_comp.py`` similar and simpler:

Import the necessary modules::

    import polysim.run_framework.domain as dom
    import polysim.pyGriddata.manufacture_gap as manu
    import polysim.pyGriddata.table_management as tm
    import polysim.pyGriddata.gridObject as go
    import polysim.pyGriddata.prep_mesh as prep

First determine the limits of the domain you wish to create your mesh for::

    grid_dir = '.'

    domain = dom.domain(grid_dir)
    domain.read_spatial_grid()

    x_values = [n.x for n in domain.node.values()]
    y_values = [n.y for n in domain.node.values()]
    xr = max(x_values)
    xl = min(x_values)
    yu = max(y_values)
    yl = min(y_values)

Divide up the domain into a collection of rectangles determined by ``x_points``
and ``y_points``::

    x_points = (xl, 750, 1500, xr)
    y_points = (yl, -1200, -750, 100, 500, 1150, 1300, yu)

Designate the probablities for each of the four landuse classifications for
each rectangle::

    p = [[0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0, 0, 0, 1],
     [0.8, 0.2, 0.0, 0],
     [0.0, 0.2, 0.8, 0],
     [0.8, 0.2, 0, 0],
     [0.2, 0.4, 0.4, 0],
     [0.1, 0.2, 0.7, 0],
     [0.2, 0.4, 0.4, 0],
     [0.7, 0.3, 0, 0],
     [1, 0, 0, 0],
     [0, 0, 1, 0 ],
     [0.9, 0.1, 0, 0 ],
     [0.8, 0.1, 0.1, 0],
     [0.1, 0.2, 0.7, 0], 
     [0.2, 0.4, 0.4, 0], 
     [0, 0.1, 0.9, 0]]

You can construct data by randomly selecting values from four classifications at a
resolution of 30 m and write that out to a file ``band_sections.asc``::

    rand_rect = manu.random_patches(x_points, y_points, [1, 2, 3, 4],
        p_sections = p)
    manu.write_gapfile(rand_rect, xl, yl, 'band_sections.asc')

For other methods to create random GAP data see
:mod:`polysim.pyGriddata.manufacture_gap`.

Finally, create and verify the landuse basis ``fort.13`` files::

    table = tm.read_table('rand_Manning.table')
    gap_sec = tm.gapInfo('band_sections.asc', table)
    gap_list = [gap_sec]
    grid = go.gridInfo('flagged_fort.14', gap_list)

    prep.prep_all(grid, path = grid_dir)
    prep.prep_test(grid, path = grid_dir)

    prep.prep_all(grid, path = grid_dir)
    prep.prep_test(grid, path = grid_dir)
    prep.compare(basis_dir = grid_dir)

.. note:: Right now I'm averaging using the 1x scheme. If you want to use a
    higher averaging scheme you will need to choose ``xl, xr, yl, yu`` such
    that you define a rectangular domain *larger* than your mesh to compensate
    for the averaging scheme. 
