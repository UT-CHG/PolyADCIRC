#! /usr/bin/env/python

# import necessary modules
import polyadcirc.pyADCIRC.plotADCIRC as pa
import polyadcirc.run_framework.random_manningsn as rmn

# setup and load from shelf
# set up saving
save_file = 'py_save_file.mat'
base_dir = '/h1/lgraham/workspace'

grid_dir = base_dir+'/ADCIRC_landuse/Inlet/inputs/tides'
save_dir = base_dir+'/ADCIRC_landuse/Inlet/runs/vel_test'
basis_dir = base_dir+'/ADCIRC_landuse/Inlet/landuse_basis/gap/bands'

main_run, domain, mann_pts = rmn.loadmat(save_file, base_dir, grid_dir,
        save_dir, basis_dir)

#main_run.make_plots(mann_pts, domain)
