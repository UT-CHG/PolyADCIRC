.. _overview:

========
Overview
========

Installation
------------

The code currently resides at `GitHub <https://github.com/UT-CHG/PolyADCIRC>`_.
If you have a `.zip <https://github.com/UT-CHG/PolyADCIRC/archive/master.zip>`_
file you can install PolyADCIRC using::

    python setup.py install

from the package root directory. The PolyADCIRC package is currently NOT avaiable in
the `Python Package Index <http://pypi.python.org/pypi/Sphinx>`_ this may
change in the future. This package requires `GNU Parallel
<http://www.gnu.org/software/parallel/>`_, `matplotlib
<http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package interacts with :program:`ADCIRC`
and :program:`GridData`. :program:`ADCIRC` is NOT provided with this package.

:program:`Griddata_parallel.out` needs to be compiled in the
``PolyADCIRC/polyadcirc/pyGriddata`` folder::

    gfortran -openmp -DHIGHMEM -o Griddata_parallel.out Griddata_v1.32.F90

Cutting Edge Version
~~~~~~~~~~~~~~~~~~~~
To use the cutting edge version of this package you need to add the PolySim git
repo to your ``PYTHONPATH``. The PolySim repo is located at::

    /org/groups/chg/lgraham/PolySim.git

You can do this by adding the line::

    export PYTHONPATH=~/PolyADCIRC:$PYTHONPATH

to your ``~/.bash_profile`` or ``~/.bashrc`` file.

To check that this has worked you can type (in a Python enviroment)::

    >>> import sys
    >>> sys.path

and the PolyADCIRC directory should be listed in that path. 

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
            subdomain.py
            random_wall.py       
            fulldomain.py
            domain.py            
        pyGriddata/
            __init__.py  
            file_management.py
            table_to_mesh_map.py  
            manufacture_gap.py
            gridObject.py


Code Overview
--------------

:mod:`pyADCIRC` Package
~~~~~~~~~~~~~~~~~~~~~~~

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
Dependencies via ``import`` statements::

    polyadcirc/
        pyADCIRC/
            \-prep_management (polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn) 
            \-plotADCIRC(polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn, 
                polyadcirc.run_framework.random_wall) 
            \-fort13_management (polyadcirc.pyGriddata.prep_mesh,
                polyadcirc.pyGriddata.table_to_mesh_map, 
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn, 
                polyadcirc.run_framework.random_wall)
            \-fort15_management (polyadcirc.pyADCIRC.plotADCIRC,
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.run_framework.subdomain)             
            \-fort14_management (polyadcirc.pyGriddata.prep_mesh,
                polyadcirc.pyGriddata.file_management, 
                polyadcirc.run_framework.domain,
                polyadcirc.run_framework.random_wall)
            \-basic (polyadcirc.pyADCIRC.fort14_management,
                polyadcirc.pyADCIRC.fort15_management)
            \-output (polyadcirc.run_framework.random_wall,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.run_framework.subdomain)          
            \-convert_fort14_to_fort13 (polyadcirc.pyGriddata.gridObject)
            \-flag_fort14 (polyadcirc.pyADCIRC.fort14_management)       
        run_framework/
            \-random_manningsn (polyadcirc.run_framework.random_wall,
                polyadcirc.run_framework.subdomain)  
            \-domain (polyadcirc.run_framework.fulldomain,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.run_framework.subdomain)
        pyGriddata/
            \-file_management (polyadcirc.pyADCIRC.plotADCIRC,
                polyadcirc.pyGriddata.prep_mesh)
            \-table_to_mesh_map (polyadcirc.pyGriddata.prep_mesh,
                polyadcirc.run_framework.random_manningsn,
                polyadcirc.run_framework.subdomain)

External dependencies
---------------------
This pacakge requires `matplotlib <http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package is written in `Python
<http://http://docs.python.org/2>`_.

::    
  
  matplotlib 
      \-collections 
      | \-LineCollection (polyadcirc.pyADCIRC.plotADCIRC)
      \-pyplot (polyadcirc.pyADCIRC.plotADCIRC)
      \-tri (polyadcirc.pyADCIRC.plotADCIRC)
    mpl_toolkits 
      \-axes_grid1 
        \-make_axes_locatable (polyadcirc.pyADCIRC.plotADCIRC)
    numpy (polyadcirc.pyADCIRC.volume,polyadcirc.run_framework.random_manningsn,polyadcirc.pyADCIRC.fort15_management,polyadcirc.run_framework.domain,polyadcirc.pyGriddata.manufacture_gap,polyadcirc.run_framework.random_wall,polyadcirc.pyGriddata.prep_mesh,polyadcirc.run_framework.subdomain,polyadcirc.pyGriddata.table_to_mesh_map,polyadcirc.pyADCIRC.plotADCIRC,polyadcirc.pyADCIRC.fort14_management,polyadcirc.pyADCIRC.fort13_management,polyadcirc.pyADCIRC.fort1920_management,polyadcirc.pyADCIRC.convert_fort14_to_fort13,polyadcirc.pyADCIRC.output)
    scipy 
      \-interpolate 
      | \-griddata (polyadcirc.run_framework.domain)
      \-io (polyadcirc.run_framework.subdomain,polyadcirc.run_framework.random_wall,polyadcirc.run_framework.random_manningsn)






