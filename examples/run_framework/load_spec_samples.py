#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.random_wall as rmw
import numpy as np
import scipy.io as sio
from scipy.interpolate import griddata

# Specify run parameter folders 
base_dir = '/h1/lgraham/workspace'
grid_dir = base_dir + '/ADCIRC_landuse/Inlet_b2/inputs/for_walls'
save_dir = base_dir + '/ADCIRC_landuse/Inlet_b2/runs/for_wall_q2'
basis_dir = base_dir +'/ADCIRC_landuse/Inlet_b2/gap/beach_walls_2lands'

# setup and save to shelf
# set up saving
save_file = 'py_save_file'

# Load and fix water heights
main_run, domain, mann_pts, wall_pts, points = rmw.loadmat(save_file, base_dir,
        grid_dir, save_dir, basis_dir)

mdict = dict()
mdict['time_obs'] = main_run.time_obs
mdict['ts_data'] = main_run.ts_data
mdict['nts_data'] = main_run.nts_data
mdict['mann_pts'] = mann_pts

# Interpolate station data for non-time series data
# Change xi to add more or different stations
xi = np.array([[s.x, s.y] for s in domain.stations['fort61']])
points = np.column_stack((domain.array_x(), domain.array_y()))
orig = main_run.nts_data.copy()
for key, values in orig.iteritems():
    if key[-1] == str(3):
        main_run.nts_data[key[:-1]+'1'] = griddata(points, values, xi)

mdict['nts_data'] = main_run.nts_data
sio.savemat('data_q1q2.mat', mdict, do_compression=True)
