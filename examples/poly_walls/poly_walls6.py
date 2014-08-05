#! /usr/bin/env python
# import necessary modules
import polyadcirc.run_framework.domain as dom
import polyadcirc.run_framework.random_wall as rmw
import numpy as np

run_no = 5
walls_per_run = 3

adcirc_dir = '/work/01837/lcgraham/v50_subdomain/work'
grid_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/inputs/poly_walls'
save_dir = adcirc_dir + '/ADCIRC_landuse/Inlet/runs/poly_wall_'+str(run_no)
basis_dir = adcirc_dir +'/ADCIRC_landuse/Inlet/landuse_basis/gap/beach_walls_2lands'
# assume that in.prep* files are one directory up from basis_dir
script = "run_script_"+str(run_no)+".sh"
timeseries_files = []#["fort.63"]
nontimeseries_files = ["tinun.63", "maxvel.63", "maxele.63"]#, "timemax63"]

# NoNx12/TpN where NoN is number of nodes and TpN is tasks per node, 12 is the
# number of cores per node See -pe line in submission_script <TpN>way<NoN x
# 12>
nprocs = 8 # number of processors per PADCIRC run
ppnode = 12
NoN = 32 
num_of_parallel_runs = (ppnode*NoN)/nprocs # procs_pnode * NoN / nproc

domain = dom.domain(grid_dir)
domain.update()

main_run = rmw.runSet(grid_dir, save_dir, basis_dir, num_of_parallel_runs,
        base_dir = adcirc_dir, script_name = script)
main_run.initialize_random_field_directories(num_procs = nprocs)

# Set samples
lam_domain = np.array([[.07, .15], [.1, .2]])
lam1 = np.linspace(lam_domain[0, 0], lam_domain[0, 1], 52)
lam2 = np.linspace(lam_domain[1, 0], lam_domain[1, 1], 50)
lam4 = 0.012
lam1, lam2, lam4 = np.meshgrid(lam1, lam2, lam4)
lam_samples = np.column_stack((lam1.ravel(), lam2.ravel(), lam4.ravel()))

mann_pts = lam_samples.transpose()
num_walls = 21

a = run_no*walls_per_run
b = (run_no+1)*walls_per_run

ymin = np.linspace(1500, -1500, num_walls)[a:b]
xmin = 1420*np.ones(ymin.shape)
xmax = 1580*np.ones(ymin.shape)
ymax = 1500*np.ones(ymin.shape)
wall_height = -2.5*np.ones(ymax.shape)
# box_limits [xmin, xmax, ymin, ymax, wall_height]
mann_pts = np.tile(mann_pts,ymin.size)
wall_points = np.column_stack((xmin, xmax, ymin, ymax, wall_height))
wall_points = wall_points.transpose()

# setup and save to shelf
# set up saving
save_file = 'py_save_file'+str(run_no)

# Run experiments
# MainFile_RandomMann
main_run.run_points(domain, wall_points, mann_pts, save_file, 
        num_procs = nprocs, procs_pnode = ppnode, ts_names = timeseries_files,
        nts_names = nontimeseries_files)









