"""

This package contains a set of modules mainly for the mapping of nodal data to
an :program:`ADCIRC` mesh using landuse data and the :program:`Fortran90`
program :program:`Griddata_v1.32.F90`. :program:`GridData` is a
:program:`FORTRAN` program originally developed by Seizo Tanaka (ST3) and
C.H.Lab., University of Notre Dame. 


This package contains the modules

    * :mod:`~polyadcirc.pyGriddata.file_management`
    * :mod:`~polyadcirc.pyGriddata.table_management`
    * :mod:`~polyadcirc.pyGriddata.table_to_mesh_map`
    * :mod:`~polyadcirc.pyGriddata.gridObject`
    * :mod:`~polyadcirc.pyGriddata.manufacture_gap`
    * :mod:`~polyadcirc.pyGriddata.prep_mesh`

:mod:`~polyadcirc.pyGriddata.prep_mesh` prepares ``*.table and
*.13`` files needed for :mod:`~polyadcirc.pyGriddata.table_to_mesh_map` and creates the n x m
matrix of multiplier factors where n = # nodes, and m = # land classification
values, assuming there are no surprises with the spatial averaging.

additional needed files:
    * compiled version of :program:`Gridata_v1.32.F90` named
      :program:`Griddata_parallel.out` 
    * ``.asc`` files
    * ``*.14 files``
    * `fort.13`` file to use as a template for
      :meth:`~polyadcirc.pyGriddata.prep_mesh.convert`

:mod:`~polyadcirc.pyGriddata.table_to_mesh_map` given a ``**_manning.table``
(and data file(s) from above) produces a ``fort.13`` ready for use by
:program:`ADCIRC` 

.. node :: This module requires a modified version of
    :program:`Griddatat_v1.32.F90` that takes ``*.in`` files

.. todo:: update so that this works similarly to how I have things working on
    lonestar and so that there is also a version that runs on a workstation
    
"""
__all__  = ['file_management', 'table_management', 'table_to_mesh_map',
          'gridObject', 'manufacture_gap', 'prep_mesh']
