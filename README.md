PolyADCIRC
==========

This code was originally developed for research purposes use at your own risk. Hopefully, the documentation is clear. You might find bugs I have overlooked. If you find something amiss please report this problem through GitHub  by raising an issue or submit a pull-request. Thanks!

This code has been documented with Sphinx. To build documentation run 
``make html`` in the ``doc/`` folder.
All documentation is contained in ``doc/`` 
To build/update the documentation use the following commands::

    sphinx-apidoc -f -o doc polyadcirc
    cd doc
    make html
    make html

This will create the html documetation in ``gh-pages/html``. If you want to create the documentation somewhere else you will need to change ``doc/Makefile``.

You will need to run sphinx-apidoc anytime a new module or method in the source code has been added. If only the *.rst files have changed then you can simply run ``make html`` twice in the doc folder.

Useful scripts are contained in ``examples/``
Python source code for this package is contained in ``polyadcirc/``

This material is based upon work supported by the National Science Foundation
Graduate Research Fellowship under Grant No. DGE-1110007. Any opinion,
findings, and conclusions or recommendations expressed in this material are
those of the authors(s) and do not necessarily reflect the views of the
National Science Foundation.

