.. _overview:

========
Overview
========

Installation
------------

The code currently resides at `GitHub
<https://github.com/lcgraham/PolyADCIRC>`_.
If you have a 
`zip file <https://github.com/lcgraham/PolyADCIRC/archive/master.zip>`_ you can install
PolyADCIRC using::

    python setup.py -install

from the package root directory. The PolyADCIRC package is currently NOT avaiable in
the `Python Package Index <http://pypi.python.org/pypi/Sphinx>`_ this may
change in the future. This package requires `GNU Parallel
<http://www.gnu.org/software/parallel/>`_, `matplotlib
<http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package interacts with :program:`ADCIRC`
and :program:`GridData` which are NOT provided with this package.

Package Layout
--------------

The package layout is as follows::

    polyadcirc/
        pyADCIRC/
             __init__.py
            prep_management.py    
            fort1920_management.py
            plotADCIRC.py         
            fort13_management.py
            fort15_management.py  
            fort14_management.py
            basic.py
            output.py             
            convert_fort14_to_fort13.py
            flag_fort14.py        
            volume.py
        run_framework/
            __init__.py
            random_manningsn.py  
            random_wall.py       
            random_wall_Q.py
            domain.py            
        pyGriddata/
            __init__.py  
            file_management.py
            grid_management.py
            table_management.py
            table_to_mesh_map.py  
            manufacture_gap.py


Code Overview
--------------

:mod:`pyADCIRC` Package
~~~~~~~~~~~~~~~~~~~~

.. automodule:: polyadcirc.pyADCIRC

:mod:`run_framework` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: polyadcirc.run_framework

:mod:`pyGriddata` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: polyadcirc.pyGriddata


.. seealso:: :ref:`modindex` for detailed documentation of modules, classes, etc.

Internal dependencies
---------------------
Dependencies via :keyword:`import` statements::

    polyadcirc 
          \-pyADCIRC 
          | \-basic (polyadcirc.pyGriddata.grid_management,
                polyadcirc.pyGriddata.table_management,
                polyadcirc.pyADCIRC.fort15_management,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.pyADCIRC.fort14_management,
                polyadcirc.run_framework.domain) 
          | \-convert_fort14_to_fort13 (polyadcirc.pyGriddata.grid_management)
          | \-flag_fort14 (polyadcirc.pyADCIRC.fort14_management)
          | \-fort13_management (polyadcirc.pyGriddata.grid_management,
                polyadcirc.pyADCIRC.convert_fort14_to_fort13,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.pyGriddata.table_to_mesh_map,
                polyadcirc.run_framework.random_wall_Q,
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_wall)
          | \-fort14_management (polyadcirc.run_framework.random_wall_Q,
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_wall,
                polyadcirc.pyGriddata.grid_management)
          | \-fort15_management (polyadcirc.pyADCIRC.plotADCIRC,
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn) 
          | \-output (polyadcirc.run_framework.random_wall_Q,
                polyadcirc.run_framework.random_wall,
                polyadcirc.run_framework.random_manningsn)
          | \-plotADCIRC (polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_wall,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.pyGriddata.grid_management)
          | \-prep_management (polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn)
          \-pyGriddata 
          | \-file_management (polyadcirc.pyADCIRC.plotADCIRC,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.pyGriddata.grid_management)
          | \-table_management (polyadcirc.pyGriddata.grid_management)
          | \-table_to_mesh_map (polyadcirc.run_framework.random_wall_Q,
                polyadcirc.run_framework.random_wall,
              polyadcirc.run_framework.random_manningsn,
              polyadcirc.pyGriddata.grid_management) 
          \-run_framework 
            \-domain (polyadcirc.run_framework.random_manningsn,
                      polyadcirc.pyGriddata.grid_management) 
            \-random_manningsn (polyadcirc.run_framework.random_wall_Q,
                                polyadcirc.run_framework.random_wall)
            \-random_wall (polyadcirc.run_framework.random_wall_Q)



External dependencies
---------------------
This pacakge requires `matplotlib <http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package is written in `Python
<http://http://docs.python.org/2>`_.

::    
  
    matplotlib 
        \-collections (polyadcirc.pyADCIRC.plotADCIRC)
        \-pyplot (polyadcirc.pyADCIRC.plotADCIRC)
        \-tri (polyadcirc.pyADCIRC.plotADCIRC)
    mpl_toolkits 
        \-axes_grid1 (polyadcirc.pyADCIRC.plotADCIRC)
    numpy (polyadcirc.pyADCIRC.plotADCIRC,
           polyadcirc.run_framework.random_manningsn,
           polyadcirc.pyADCIRC.fort15_management, polyadcirc.pyADCIRC.output,
           polyadcirc.pyADCIRC.convert_fort14_to_fort13,
           polyadcirc.pyGriddata.manufacture_gap,
           polyadcirc.pyADCIRC.fort1920_management,
           polyadcirc.run_framework.random_wall_Q, polyadcirc.run_framework.domain,
           polyadcirc.pyGriddata.grid_management,
           polyadcirc.pyGriddata.table_to_mesh_map,
           polyadcirc.pyADCIRC.fort14_management,
           polyadcirc.pyADCIRC.fort13_management,
           polyadcirc.run_framework.random_wall, polyadcirc.pyADCIRC.volume)
    scipy 
        \-interpolate (polyadcirc.run_framework.random_wall_Q,
                       polyadcirc.run_framework.domain) 
        \-io (polyadcirc.run_framework.random_wall_Q,
              polyadcirc.run_framework.random_wall,
              polyadcirc.run_framework.random_manningsn)


