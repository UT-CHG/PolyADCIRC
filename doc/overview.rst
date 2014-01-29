.. _overview:

========
Overview
========

Installation
------------

If you have a `.tar.bz2<link>`_ file or `.zip<link>`_ file you can install
PolySim using::

    python setup.py --install

from the package root directory. PolySim packages are currently NOT avaiable in
the `Python Package Index <http://pypi.python.org/pypi/Sphinx>`_ this may
change in the future. This package requires `GNU Parallel
<http://www.gnu.org/software/parallel/>`_, `matplotlib
<http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package interacts with :program:`ADCIRC`
and :program: `GridData` which are NOT provided with this package.

Cutting Edge Version
~~~~~~~~~~~~~~~~~~~~
To use the cutting edge version of this package you need to add the PolySim git
repo to your ``PYTHONPATH``. The PolySim repo is located at::

    /org/groups/chg/lgraham/PolySim.git

You can do this by adding the line::

    export PYTHONPATH=~/PolySim:$PYTHONPATH

to your ``~/.bash_profile`` or ``~/.bashrc`` file.

To check that this has worked you can type (in a Python enviroment)::

    >>> import sys
    >>> sys.path

and the PolySim directory should be listed in that path. 

Package Layout
--------------

The package layout is as follows::

    polysim/
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
~~~~~~~~~~~~~~~~~~~~

.. automodule:: polysim.pyADCIRC

:mod:`run_framework` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: polysim.run_framework

:mod:`pyGriddata` Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: polysim.pyGriddata


.. seealso:: :ref:`modindex` for detailed documentation of modules, classes, etc.

Internal dependencies
---------------------
Dependencies via :keyword:`import` statements::

    polysim/
        pyADCIRC/
            \-prep_management (polysim.run_framework.domain,
                polysim.run_framework.random_manningsn) 
            \-plotADCIRC(polysim.run_framework.domain,
                polysim.run_framework.random_manningsn, 
                polysim.run_framework.random_wall) 
            \-fort13_management (polysim.pyGriddata.prep_mesh,
                polysim.pyGriddata.table_to_mesh_map, 
                polysim.run_framework.domain,
                polysim.run_framework.random_manningsn, 
                polysim.run_framework.random_wall)
            \-fort15_management (polysim.pyADCIRC.plotADCIRC,
                polysim.run_framework.domain,
                polysim.run_framework.random_manningsn,
                )             
            \-fort14_management (polysim.pyGriddata.prep_mesh,
                polysim.pyGriddata.file_management, 
                polysim.run_framework.domain,
                polysim.run_framework.random_wall)
            \-basic (polysim.pyADCIRC.fort14_management,
                polysim.pyADCIRC.fort15_management)
            \-output (polysim.run_framework.random_wall,
                polysim.run_framework.random_manningsn,
                )          
            \-convert_fort14_to_fort13 (polysim.pyGriddata.gridObject)
            \-flag_fort14 (polysim.pyADCIRC.fort14_management)       
        run_framework/
            \-random_manningsn (polysim.run_framework.random_wall,
                )  
            \-domain (polysim.run_framework.random_manningsn,
                )
        pyGriddata/
            \-file_management (polysim.pyADCIRC.plotADCIRC,
                polysim.pyGriddata.prep_mesh)
            \-table_to_mesh_map (polysim.pyGriddata.prep_mesh,
                polysim.run_framework.random_manningsn,
                )

External dependencies
---------------------
This pacakge requires `matplotlib <http://http://matplotlib.org>`_, `scipy <scipy.org>`_, mpl_toolkit, and `numpy
<http://http://www.numpy.org>`_. This package is written in `Python
<http://http://docs.python.org/2>`_.

::    
  
  matplotlib 
      \-collections 
      | \-LineCollection (polysim.pyADCIRC.plotADCIRC)
      \-pyplot (polysim.pyADCIRC.plotADCIRC)
      \-tri (polysim.pyADCIRC.plotADCIRC)
    mpl_toolkits 
      \-axes_grid1 
        \-make_axes_locatable (polysim.pyADCIRC.plotADCIRC)
    numpy (polysim.pyADCIRC.volume,polysim.run_framework.random_manningsn,polysim.pyADCIRC.fort15_management,polysim.run_framework.domain,polysim.pyGriddata.manufacture_gap,polysim.run_framework.random_wall,polysim.pyGriddata.prep_mesh,,polysim.pyGriddata.table_to_mesh_map,polysim.pyADCIRC.plotADCIRC,polysim.pyADCIRC.fort14_management,polysim.pyADCIRC.fort13_management,polysim.pyADCIRC.fort1920_management,polysim.pyADCIRC.convert_fort14_to_fort13,polysim.pyADCIRC.output)
    scipy 
      \-interpolate 
      | \-griddata (polysim.run_framework.domain)
      \-io (,polysim.run_framework.random_wall,polysim.run_framework.random_manningsn)






