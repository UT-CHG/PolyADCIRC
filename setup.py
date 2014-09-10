#!/usr/bin/env python

from distutils.core import setup

setup(name='PolyADCIRC',
      version='0.1dev',
      description='Parallel ADCIRC Multi-Simulation Framework',
      author='Lindley Graham',
      author_email='lgraham@ices.utexas.edy',
      url='https://github.com/lcgraham/PolyADCIRC',
      packages=['polyadcirc', 'polyadcirc.run_framework', 'polyadcirc.pyADCIRC',
      'polyadcirc.pyGriddata'],
      license='Revised BSD License'
      )

