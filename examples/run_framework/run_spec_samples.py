#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.run_framework.random_wall as rmw
import numpy as np
import scipy.io as sio

# Specify run parameter folders 
adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet_b2/inputs/for_walls'
save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet_b2/runs/for_wall_q2'
basis_dir = adcirc_dir +'/ADCIRC_landuse/Inlet_b2/gap/beach_walls_2lands'
# assume that in.prep* files are one directory up from basis_dir
script = "b2_forward_q2.sh"
timeseries_files = ["fort.61"]
nontimeseries_files = ["maxele.63", "timemax63", "tinun.63"]#, "timemax63"]

# NoNx12/TpN where NoN is number of nodes and TpN is tasks per node, 12 is the
# number of cores per node See -pe line in submission_script <TpN>way<NoN x
# 12>
nprocs = 4 # number of processors per PADCIRC run
ppnode = 16
NoN = 20
TpN = 16 # must be 16 unless using N option
num_of_parallel_runs = (TpN*NoN)/nprocs

domain = dom.domain(grid_dir)
domain.update()

main_run = rmw.runSet(grid_dir, save_dir, basis_dir, num_of_parallel_runs,
                      base_dir=adcirc_dir, script_name=script)
main_run.initialize_random_field_directories(num_procs=nprocs)

# Set samples
num_walls = 1
q1qn = sio.loadmat("q1q2_truth7_forward_samples.mat")
mann_pts = np.squeeze(np.array(zip(q1qn['x_samples_forward'],
                      q1qn['y_samples_forward'])))
mann_pts = mann_pts.transpose()
mann_all = np.append(mann_pts, np.array([[.107], [.106]]), axis=1)
lam4 = 0.012*np.ones((mann_all.shape[1]))
mann_pts = np.row_stack((mann_all, lam4))

ymin = np.array([-1050]) #np.linspace(1500, -1050, num_walls)
xmin = 1420*np.ones(ymin.shape)
xmax = 1580*np.ones(ymin.shape)
ymax = 1500*np.ones(ymin.shape)
wall_height = -2.5*np.ones(ymax.shape)
# box_limits [xmin, xmax, ymin, ymax, wall_height]
wall_points = np.column_stack((xmin, xmax, ymin, ymax, wall_height))
wall_points = wall_points.transpose()

# setup and save to shelf
# set up saving
save_file = 'py_save_file'

# Run experiments
# MainFile_RandomMann
main_run.run_points(domain, wall_points, mann_pts, save_file, 
                    num_procs=nprocs, procs_pnode=ppnode,
                    ts_names=timeseries_files, nts_names=nontimeseries_files)









