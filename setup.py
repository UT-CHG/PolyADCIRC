#!/usr/bin/env python

from distutils.core import setup

setup(name='PolySim',
version='0.1dev',
description='PyADCIRC Multi-Simulation Framework',
author='Lindley Graham',
author_email='lgraham@ices.utexas.edy',
url='http://users.ices.utexas.edu/~lgraham/polysim/html/index.html',
packages=['polysim', 'polysim.run_framework', 'polysim.pyADCIRC',
'polysim.pyGriddata'],
license='Revised BSD License'
)

