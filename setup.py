#!/usr/bin/env python

# Copyright (C) 2013 Lindley Graham


try:
  from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='PolyADCIRC',
      version='0.3.0',
      description='Parallel ADCIRC Multi-Simulation Framework',
      author='Lindley Graham',
      author_email='lichgraham@gmail.com',
      url='https://github.com/UT-CHG/PolyADCIRC',
      packages=['polyadcirc', 'polyadcirc.run_framework', 'polyadcirc.pyADCIRC',
      'polyadcirc.pyGriddata'],
      license='Revised BSD License',
      install_requires=['matplotlib', 'scipy', 'numpy']
      )

