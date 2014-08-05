PolyADCIRC
==========

This code has been documented with Sphinx. To build documentation run 
``make html`` in the ``doc/`` folder.
All documentation is contained in ``doc/_build/_html`` 
To build/update the documentation use the following commands::

    sphinx-apidoc -f -o doc polysim
    cd doc
    make html
    make html

You will need to run sphinx-apidoc anytime a new module or method in the source code has been added. If only the *.rst files have changed then you can simply run ``make html`` twice in the doc folder.

Useful scripts are contained in ``examples/``
Python source code for this package is contained in ``polysim/``
