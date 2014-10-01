=============================================
"All" about land use and land classifications
=============================================

This code creates the set of landuse basis folders, ``landuse_##``, required by
:class:`polyadcirc.random_manningsn.runSet`.  All the below code is set up to be
run on a workstation.

Preparing basis vector files from GAP/NLCD data
-----------------------------------------------

The ``from_GAPDATA.py`` script in ``examples/pyGriddata`` prepares ``*.table`` and
``*.13`` files needed to map landuse classifications to the computationa mesh.

Import the necessary modules::

    
    import polyadcirc.pyGriddata.table_management as tm
    import polyadcirc.pyGriddata.grid_management as gm

Specify the folders containing mesh files::
    
    adcirc_dir = '/h1/lgraham/workspace'
    grid_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/inputs'

Specify the folder in which to create the ``landuse_##`` folders containing the
``fort.13`` formatted files::

    basis_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/landuse_basis/gap/shelf_test'


Read in the ``CCAP_Manning.table`` file in the current working directory.::

    table = tm.read_table('CCAP_Manning_20100922.table',
                          adcirc_dir+'/landuse/tables') 

To read in multiple ``*.table`` files use::

    tables = tm.read_tables()

Create a list of :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
objects, one for each ``*.asc`` file::

    gap_files = glob.glob('/h1/lgraham/workspace/landuse/data/CCAP_Data/Job*/*.asc')
    gap_list = tm.create_gap_list(table, gap_files) 

Create a :class:`~polyadcirc.pyGriddata.gridObject.gridInfo` object and store
references to the :class:`~polyadcirc.pyGriddata.table_management.gapInfo`
objects::

    grid = gm.gridInfo(basis_dir, grid_dir, gap_list,
            executable_dir="directory_containing_Griddataexecutable")
    
Set up files to run :program:`Griddata_v1.32.F90` to create the landuse basis
folders and run :program:`Griddata_v1.32.F90` to map the landuse classification
data to the mesh::
    
    grid.prep_all()

Create a ``fort.13`` formatted file using the Manning's n vales in
``CCAP_Manning_20100922.table``::

    grid.prep_test()

This code also maps the landuse classifcation data to the mesh for a
test case for verifcation purposes. The method
:meth:`~polyadcirc.pyGriddata.prep_mesh.compare` generates a set of images in a
``figs/`` folder for visual verification::

    gm.compare(basis_dir)

``basis_dir`` is the folder where the ``test`` and ``landuse_*`` folders are
located in addition to the ``fort.14`` file. A set of plots will be created in
``figs``. The values in the ``difference.png`` figure should be very small.


Bathymetry based landuse classifications
----------------------------------------

You can also map Manning's n values to the computational mesh according to
bathymetry. The script ``examples/pyGriddata/add_shelf.py`` demonstrates how to
create a land classification for nodes within a user-specified range of
bathymetry that are not already included in a given set of land classification
meshes.

Import necessary modules::

    import polyadcirc.run_framework.domain as dom
    import polyadcirc.pyGriddata.file_management as fm
    import polyadcirc.pyGriddata.table_to_mesh_map as tmm
    import polyadcirc.pyADCIRC.fort13_management as f13
    import glob

Specify the folder containing the ``fort.14`` file::
    adcirc_dir = '/h1/lgraham/workspace'
    grid_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/inputs'

Specify the folder containing a ``fort.13`` file to use as a template::

    save_dir = adcirc_dir + '/ADCIRC_landuse/Katrina_small/runs/output_test'

Specify the folder containing a pre-existing set of land classification
meshes::

    basis_dir = adcirc_dir +'/ADCIRC_landuse/Katrina_small/landuse_basis/gap/shelf_test'

Load in the physical mesh with bathymetry information from a ``fort.14`` file::

    domain = dom.domain(grid_dir)
    domain.update()

Load in the landuse classification meshes as a list of dictionaries::

    bv_dict = tmm.get_basis_vectors(basis_dir)

Create a dictionary specifiying a landuse classification mesh for the nodes
with bathymetry between 0 and 50::

    shelf_limits = [0, 50]
    shelf_bv = tmm.create_shelf(domain, shelf_limits, bv_dict)

Write this new landuse classification mesh out to an appropriately numbered
``landuse_##`` folder in the ``basis_dir``::

    # get list of landuse folder names
    folders = glob.glob(basis_dir+'/landuse_*')
    # create new folder
    folder_name = basis_dir+'/landuse_'+'{:=02d}'.format(len(folders))
    fm.mkdir(folder_name)
    # copy a fort.13 file to that folder
    fm.copy(save_dir+'/fort.13', folder_name+'/fort.13')
    f13.update_mann(shelf_bv, folder_name)

Manufacturing GAP data
----------------------

This section deals mostly with how to use
:mod:`~polyadcirc.pyGriddata.manufacture_gap`. The relevant example scripts
for this section located in ``examples/pyGriddata`` are
    
    * :mod:`manufactureGAP_patches.py`, requires ``rand_Manning.table`` file
    * :mod:`manufactureGAP_vertical.py`, requires ``rand_Manning.table`` file

What follows is an explaination of the script ``manufactureGAP_patches.py``, the script
``manufactureGAP_vertical.py`` is similar and simpler:

Import the necessary modules::

    import polyadcirc.run_framework.domain as dom
    import polyadcirc.pyGriddata.manufacture_gap as manu

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
:mod:`polyadcirc.pyGriddata.manufacture_gap`.

To create and verify the landuse basis ``fort.13`` files you should modify
``example/pyGriddata/from_GAPDATA.py`` appropriately.

.. note:: Right now I'm averaging using the 1x scheme. If you want to use a
    higher averaging scheme you will need to choose ``xl, xr, yl, yu`` such
    that you define a rectangular domain *larger* than your mesh to compensate
    for the averaging scheme. 
