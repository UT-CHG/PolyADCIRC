#!/usr/bin/env python

from distutils.core import setup

setup(name='PolySim',
version='0.1dev',
description='PyADCIRC Multi-Simulation Framework',
author='Lindley Graham',
author_email='lgraham@ices.utexas.edy',
url='http://users.ices.utexas.edu/~lgraham/polyadcirc/html/index.html',
packages=['polyadcirc', 'polyadcirc.run_framework', 'polyadcirc.pyADCIRC',
'polyadcirc.pyGriddata'],
license='Revised BSD License'
)

