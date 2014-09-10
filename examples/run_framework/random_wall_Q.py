#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.run_framework.random_wall_Q as rmw
import numpy as np
import polyadcirc.pyADCIRC.basic as basic

adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet_b2/inputs/poly_walls'
save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet_b2/runs/large_random_2D'#poly_wall'
basis_dir = adcirc_dir +'/ADCIRC_landuse/Inlet_b2/gap/beach_walls_2lands'
# assume that in.prep* files are one directory up from basis_dir
script = "large_random_2D.sh"
timeseries_files = []#["fort.63"]
nontimeseries_files = ["maxele.63"]#, "timemax63"]

# NoNx12/TpN where NoN is number of nodes and TpN is tasks per node, 12 is the
# number of cores per node See -pe line in submission_script <TpN>way<NoN x
# 12>
nprocs = 4 # number of processors per PADCIRC run
ppnode = 16
NoN = 20
TpN = 16 # must be 16 unless using N option
num_of_parallel_runs = (TpN*NoN)/nprocs # procs_pnode * NoN / nproc

domain = dom.domain(grid_dir)
domain.update()

main_run = rmw.runSet(grid_dir, save_dir, basis_dir, num_of_parallel_runs,
        base_dir=adcirc_dir, script_name=script)
main_run.initialize_random_field_directories(num_procs=nprocs)

# Set samples
num_samples = 10000 
lam_domain = np.array([[.07, .15], [.1, .2]])
random_points = lam_domain[:, 0] + (lam_domain[:, 1]-lam_domain[:,
    0])*np.random.rand(num_samples, lam_domain.shape[-1]) 
lam4 = 0.012*np.ones((num_samples, ))
lam_samples = np.column_stack((random_points, lam4.ravel()))

mann_pts = lam_samples.transpose()

ymin = -1050*np.ones(mann_pts.shape[-1]) #np.linspace(1500, -1050, num_walls)
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

stat_x = np.concatenate((1900*np.ones((7,)), [1200], 1300*np.ones((3,)),
    [1500])) 
stat_y = np.array([1200, 600, 300, 0, -300, -600, -1200, 0, 1200, 0, -1200,
    -1400])

stations = []

for x, y in zip(stat_y, stat_y):
    stations.append(basic.location(x, y))

# Run experiments
# MainFile_RandomMann
main_run.run_nobatch_q(domain, wall_points, mann_pts, save_file, 
        num_procs=nprocs, procs_pnode=ppnode, stations=stations, TpN=TpN)









